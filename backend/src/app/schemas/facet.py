import uuid
from datetime import datetime

from pydantic import BaseModel, model_validator


class FacetBase(BaseModel):
    name: str
    slug: str
    title: str | None = None
    bio: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    pdf_template: str = "moderna"
    is_published: bool = False


class FacetCreate(FacetBase):
    experience_ids: list[uuid.UUID] = []
    education_ids: list[uuid.UUID] = []
    skill_ids: list[uuid.UUID] = []
    certification_ids: list[uuid.UUID] = []
    project_ids: list[uuid.UUID] = []


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
    certification_ids: list[uuid.UUID] | None = None
    project_ids: list[uuid.UUID] | None = None


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
    certification_ids: list[uuid.UUID] = []
    project_ids: list[uuid.UUID] = []

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_ids(cls, data):
        attrs = {
            "selected_experiences": "experience_ids",
            "selected_educations": "education_ids",
            "selected_skills": "skill_ids",
            "selected_certifications": "certification_ids",
            "selected_projects": "project_ids",
        }
        for orm_attr, schema_attr in attrs.items():
            items = getattr(data, orm_attr, None)
            if items is not None:
                setattr(data, schema_attr, [item.id for item in items])
        return data
