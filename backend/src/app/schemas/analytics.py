from pydantic import BaseModel


class ReferrerCount(BaseModel):
    referrer: str
    count: int


class AnalyticsMetrics(BaseModel):
    total_views: int
    unique_views: int
    avg_time_on_page: float | None
    top_referrers: list[ReferrerCount]


class TrendPoint(BaseModel):
    date: str
    value: int


class TrendResponse(BaseModel):
    metric: str
    period: str
    data: list[TrendPoint]


class RecordEventRequest(BaseModel):
    facet_id: str
    referrer: str | None = None
    user_agent: str | None = None
    time_on_page: int | None = None
