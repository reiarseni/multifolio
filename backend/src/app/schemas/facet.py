import re
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator, model_validator

from app.schemas.theme import FacetThemeConfigResponse


class FacetBase(BaseModel):
    name: str
    slug: str
    title: str | None = None
    bio: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    pdf_template: str = "moderna"
    is_published: bool = False

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", v):
            raise ValueError("slug must contain only lowercase letters, numbers, and hyphens")
        return v


class FacetCreate(FacetBase):
    experience_ids: list[uuid.UUID] = []
    education_ids: list[uuid.UUID] = []
    skill_ids: list[uuid.UUID] = []
    project_ids: list[uuid.UUID] = []
    certification_ids: list[uuid.UUID] = []


class FacetUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    title: str | None = None
    bio: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    pdf_template: str | None = None
    is_published: bool | None = None
    experience_ids: list[uuid.UUID] | None = None
    education_ids: list[uuid.UUID] | None = None
    skill_ids: list[uuid.UUID] | None = None
    project_ids: list[uuid.UUID] | None = None
    certification_ids: list[uuid.UUID] | None = None


class FacetResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    slug: str
    title: str | None
    bio: str | None
    meta_title: str | None
    meta_description: str | None
    pdf_template: str
    is_published: bool
    created_at: datetime
    updated_at: datetime
    experience_ids: list[uuid.UUID] = []
    education_ids: list[uuid.UUID] = []
    skill_ids: list[uuid.UUID] = []
    project_ids: list[uuid.UUID] = []
    certification_ids: list[uuid.UUID] = []
    theme_config: FacetThemeConfigResponse | None = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _map_orm_ids(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return data
        return {
            "id": data.id,
            "user_id": data.user_id,
            "name": data.name,
            "slug": data.slug,
            "title": data.title,
            "bio": data.bio,
            "meta_title": data.meta_title,
            "meta_description": data.meta_description,
            "pdf_template": data.pdf_template,
            "is_published": data.is_published,
            "created_at": data.created_at,
            "updated_at": data.updated_at,
            "experience_ids": [e.id for e in data.selected_experiences],
            "education_ids": [e.id for e in data.selected_educations],
            "skill_ids": [s.id for s in data.selected_skills],
            "project_ids": [p.id for p in data.selected_projects],
            "certification_ids": [c.id for c in data.selected_certifications],
            "theme_config": data.theme_config,
        }
