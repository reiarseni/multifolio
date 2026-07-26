from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationCreate(BaseModel):
    user_id: uuid.UUID
    facet_id: uuid.UUID | None = None
    type: str
    title: str
    message: str
    referrer_domain: str | None = None
    extra_data: dict | None = None


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    facet_id: uuid.UUID | None = None
    type: str
    title: str
    message: str
    referrer_domain: str | None = None
    is_read: bool
    extra_data: dict | None = None
    created_at: datetime


class NotificationList(BaseModel):
    items: list[NotificationOut]
    total: int
    unread_count: int
