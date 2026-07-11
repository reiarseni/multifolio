import csv
import io
import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.analytics import AnalyticsMetrics, TrendResponse
from app.services import analytics_service

router = APIRouter(prefix="/facets", tags=["analytics"])


@router.get("/{facet_id}/analytics", response_model=AnalyticsMetrics)
async def get_facet_analytics(
    facet_id: uuid.UUID,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await analytics_service.get_facet_metrics(db, facet_id, days)


@router.get("/{facet_id}/analytics/trends", response_model=TrendResponse)
async def get_facet_trends(
    facet_id: uuid.UUID,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await analytics_service.get_trends(db, facet_id, days)


@router.get("/{facet_id}/analytics/export")
async def export_facet_analytics(
    facet_id: uuid.UUID,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    metrics = await analytics_service.get_facet_metrics(db, facet_id, days)
    trends = await analytics_service.get_trends(db, facet_id, days)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Total Views", metrics.total_views])
    writer.writerow(["Unique Views", metrics.unique_views])
    writer.writerow(["Avg Time on Page (s)", metrics.avg_time_on_page or 0])
    writer.writerow([])
    writer.writerow(["Date", "Views"])
    for point in trends.data:
        writer.writerow([point.date, point.value])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=analytics_{facet_id}.csv"},
    )
