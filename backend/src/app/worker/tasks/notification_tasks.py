from __future__ import annotations

import uuid

from sqlalchemy import select

from app.db.session import async_session_factory
from app.models import Facet
from app.schemas.notification import NotificationCreate
from app.services.notification_service import create_notification
from app.services.referrer_analyzer import (
    extract_domain,
    get_domain_info,
    is_notable_referrer,
)
from app.worker.celery_app import celery_app


@celery_app.task(name="notify_notable_visit")
def notify_notable_visit(facet_id: str, referrer_url: str | None = None) -> dict:
    import asyncio

    return asyncio.run(
        _async_notify_notable_visit(
            uuid.UUID(facet_id),
            referrer_url,
        )
    )


async def _async_notify_notable_visit(
    facet_id: uuid.UUID,
    referrer_url: str | None,
) -> dict:
    if not is_notable_referrer(referrer_url):
        return {"notification_created": False, "reason": "not_notable"}

    async with async_session_factory() as db:
        result = await db.execute(
            select(Facet).where(Facet.id == facet_id)
        )
        facet = result.scalar_one_or_none()

        if not facet or not facet.user_id:
            return {"notification_created": False, "reason": "facet_or_user_not_found"}

        domain = extract_domain(referrer_url)
        domain_info = get_domain_info(domain)

        title = f"Visit from {domain}" if domain else "New notable visit"
        message = f"Your facet received a visit from {domain or 'a notable referrer'}."

        notification = await create_notification(
            db,
            NotificationCreate(
                user_id=facet.user_id,
                facet_id=facet_id,
                type="notable_visit",
                title=title,
                message=message,
                referrer_domain=domain,
                extra_data=domain_info,
            ),
        )

        return {
            "notification_created": True,
            "notification_id": str(notification.id),
            "domain": domain,
        }
