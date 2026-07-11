from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session
from app.models.analytics import FacetEvent
from app.worker.celery_app import celery_app


@celery_app.task(name="aggregate_facet_metrics")
def aggregate_facet_metrics() -> dict:
    import asyncio

    return asyncio.get_event_loop().run_until_complete(_aggregate())


async def _aggregate() -> dict:
    async with async_session() as db:
        since = datetime.utcnow() - timedelta(hours=1)

        q = await db.execute(
            select(FacetEvent.facet_id).where(FacetEvent.created_at >= since).distinct()
        )
        facet_ids = [row[0] for row in q.all()]

        return {"facets_processed": len(facet_ids), "timestamp": datetime.utcnow().isoformat()}
