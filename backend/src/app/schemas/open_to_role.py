import uuid
from datetime import datetime

from pydantic import BaseModel


class OpenToRoleBase(BaseModel):
    status: str = "not_available"
    role_type: str | None = None
    modality: str | None = None
    location: str | None = None
    timezone: str | None = None


class OpenToRoleUpdate(BaseModel):
    status: str | None = None
    role_type: str | None = None
    modality: str | None = None
    location: str | None = None
    timezone: str | None = None


class OpenToRoleResponse(BaseModel):
    id: uuid.UUID
    facet_id: uuid.UUID
    status: str
    role_type: str | None
    modality: str | None
    location: str | None
    timezone: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
