from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class CommentCreate(BaseModel):
    content: str
    parent_id: uuid.UUID | None = None
    section_ref: str | None = None
    author_name: str | None = None
    author_email: str | None = None


class CommentResponse(BaseModel):
    id: uuid.UUID
    facet_id: uuid.UUID
    parent_id: uuid.UUID | None
    author_name: str | None
    author_email: str | None
    content: str
    section_ref: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    replies: list[CommentResponse] = []

    model_config = {"from_attributes": True}


class CommentResolveRequest(BaseModel):
    comment_id: uuid.UUID


class CommentUnreadCount(BaseModel):
    count: int


class ReviewLinkCreate(BaseModel):
    facet_id: uuid.UUID


class ReviewLinkResponse(BaseModel):
    id: uuid.UUID
    facet_id: uuid.UUID
    token: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewLinkAccessResponse(BaseModel):
    facet_id: uuid.UUID
    token: str
    is_active: bool
