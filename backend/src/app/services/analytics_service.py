import hashlib
import uuid
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import FacetEvent
from app.schemas.analytics import AnalyticsMetrics, ReferrerCount, TrendPoint, TrendResponse


def _hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()


async def record_event(
    db: AsyncSession,
    facet_id: uuid.UUID,
    ip: str,
    referrer: str | None = None,
    user_agent: str | None = None,
    time_on_page: int | None = None,
) -> FacetEvent:
    event = FacetEvent(
        facet_id=facet_id,
        visitor_ip_hash=_hash_ip(ip),
        referrer=referrer,
        user_agent=user_agent,
        time_on_page=time_on_page,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def get_facet_metrics(
    db: AsyncSession,
    facet_id: uuid.UUID,
    days: int = 30,
) -> AnalyticsMetrics:
    since = datetime.utcnow() - timedelta(days=days)

    total_q = await db.execute(
        select(func.count(FacetEvent.id)).where(
            FacetEvent.facet_id == facet_id,
            FacetEvent.created_at >= since,
        )
    )
    total_views = total_q.scalar() or 0

    unique_q = await db.execute(
        select(func.count(func.distinct(FacetEvent.visitor_ip_hash))).where(
            FacetEvent.facet_id == facet_id,
            FacetEvent.created_at >= since,
        )
    )
    unique_views = unique_q.scalar() or 0

    avg_q = await db.execute(
        select(func.avg(FacetEvent.time_on_page)).where(
            FacetEvent.facet_id == facet_id,
            FacetEvent.created_at >= since,
            FacetEvent.time_on_page.isnot(None),
        )
    )
    avg_time = avg_q.scalar()

    ref_q = await db.execute(
        select(
            FacetEvent.referrer,
            func.count(FacetEvent.id).label("count"),
        )
        .where(
            FacetEvent.facet_id == facet_id,
            FacetEvent.created_at >= since,
            FacetEvent.referrer.isnot(None),
        )
        .group_by(FacetEvent.referrer)
        .order_by(func.count(FacetEvent.id).desc())
        .limit(10)
    )
    top_referrers = [ReferrerCount(referrer=r.referrer, count=r.count) for r in ref_q.all()]

    return AnalyticsMetrics(
        total_views=total_views,
        unique_views=unique_views,
        avg_time_on_page=avg_time,
        top_referrers=top_referrers,
    )


async def get_trends(
    db: AsyncSession,
    facet_id: uuid.UUID,
    days: int = 30,
) -> TrendResponse:
    since = datetime.utcnow() - timedelta(days=days)

    q = await db.execute(
        select(
            func.date(FacetEvent.created_at).label("date"),
            func.count(FacetEvent.id).label("value"),
        )
        .where(
            FacetEvent.facet_id == facet_id,
            FacetEvent.created_at >= since,
        )
        .group_by(func.date(FacetEvent.created_at))
        .order_by(func.date(FacetEvent.created_at))
    )
    rows = q.all()

    return TrendResponse(
        metric="views",
        period=f"last_{days}_days",
        data=[TrendPoint(date=str(r.date), value=r.value) for r in rows],
    )
