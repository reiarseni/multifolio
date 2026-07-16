import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ReviewLinkCreate(BaseModel):
    label: str | None = None
    password: str | None = Field(None, min_length=6, max_length=128)
    expires_in_hours: int | None = Field(None, ge=1, le=720)


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
    password: str


class ReviewLinkAccessResponse(BaseModel):
    facet_id: uuid.UUID
    token: str
    label: str | None
