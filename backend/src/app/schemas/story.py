import uuid
from datetime import datetime

from pydantic import BaseModel


class StorySectionCreate(BaseModel):
    section_type: str
    title: str
    content: str | None = None
    media_urls: list[str] | None = None
    order: int = 0
    is_visible: bool = True


class StorySectionUpdate(BaseModel):
    section_type: str | None = None
    title: str | None = None
    content: str | None = None
    media_urls: list[str] | None = None
    order: int | None = None
    is_visible: bool | None = None


class StorySectionResponse(BaseModel):
    id: uuid.UUID
    facet_id: uuid.UUID
    section_type: str
    title: str
    content: str | None
    media_urls: list | None
    order: int
    is_visible: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StoryReorderRequest(BaseModel):
    section_ids: list[uuid.UUID]
