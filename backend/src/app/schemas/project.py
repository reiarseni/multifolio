import uuid
from datetime import datetime

from pydantic import BaseModel


class ProjectImageResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    image_url: str
    caption: str | None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectAttachmentResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    file_url: str
    filename: str
    mime_type: str
    file_size: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectImageCreate(BaseModel):
    image_url: str
    caption: str | None = None
    sort_order: int = 0


class ProjectAttachmentCreate(BaseModel):
    file_url: str
    filename: str
    mime_type: str
    file_size: int


class ProjectBase(BaseModel):
    title: str
    description: str | None = None
    cover_image_url: str | None = None
    markdown_content: str | None = None
    github_url: str | None = None
    live_url: str | None = None
    sort_order: int = 0


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    cover_image_url: str | None = None
    markdown_content: str | None = None
    github_url: str | None = None
    live_url: str | None = None
    sort_order: int | None = None


class ProjectResponse(ProjectBase):
    id: uuid.UUID
    profile_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    images: list[ProjectImageResponse] = []
    attachments: list[ProjectAttachmentResponse] = []

    model_config = {"from_attributes": True}
