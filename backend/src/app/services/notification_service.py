from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.schemas.notification import (
    NotificationCreate,
    NotificationList,
    NotificationOut,
)


async def create_notification(
    db: AsyncSession,
    data: NotificationCreate,
) -> NotificationOut:
    notification = Notification(
        id=uuid.uuid4(),
        user_id=data.user_id,
        facet_id=data.facet_id,
        type=data.type,
        title=data.title,
        message=data.message,
        referrer_domain=data.referrer_domain,
        extra_data=data.extra_data or {},
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return NotificationOut.model_validate(notification)


async def get_user_notifications(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
    unread_only: bool = False,
) -> NotificationList:
    query = select(Notification).where(Notification.user_id == user_id)

    if unread_only:
        query = query.where(Notification.is_read == False)  # noqa: E712

    query = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    notifications = result.scalars().all()

    count_query = select(func.count()).where(
        Notification.user_id == user_id,
    )
    unread_query = select(func.count()).where(
        Notification.user_id == user_id,
        Notification.is_read == False,  # noqa: E712
    )

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    unread_result = await db.execute(unread_query)
    unread_count = unread_result.scalar() or 0

    return NotificationList(
        items=[NotificationOut.model_validate(n) for n in notifications],
        total=total,
        unread_count=unread_count,
    )


async def mark_as_read(
    db: AsyncSession,
    notification_id: uuid.UUID,
    user_id: uuid.UUID,
) -> NotificationOut | None:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        ),
    )
    notification = result.scalar_one_or_none()
    if not notification:
        return None

    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return NotificationOut.model_validate(notification)


async def mark_all_as_read(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> int:
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False,  # noqa: E712
        ),
    )
    notifications = result.scalars().all()
    count = len(notifications)

    for n in notifications:
        n.is_read = True

    await db.commit()
    return count
