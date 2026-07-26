from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class ReviewLinkCreate(BaseModel):
    label: str | None = None
    password: str | None = None
    expires_in_hours: int | None = None


class ReviewLinkResponse(BaseModel):
    id: uuid.UUID
    facet_id: uuid.UUID
    token: str
    label: str | None
    requires_password: bool
    expires_at: datetime | None
    single_use: bool
    is_used: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReviewLinkValidateRequest(BaseModel):
    password: str | None = None


class ReviewLinkValidateResponse(BaseModel):
    valid: bool
    facet_id: uuid.UUID


class ReviewLinkAccessResponse(BaseModel):
    facet_id: uuid.UUID
    token: str
    label: str | None
