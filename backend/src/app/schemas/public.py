import uuid
from datetime import date

from pydantic import BaseModel


class PublicProjectImage(BaseModel):
    id: uuid.UUID
    image_url: str
    caption: str | None

    model_config = {"from_attributes": True}


class PublicProject(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    cover_image_url: str | None
    markdown_content: str | None
    github_url: str | None
    live_url: str | None
    images: list[PublicProjectImage] = []

    model_config = {"from_attributes": True}


class PublicExperience(BaseModel):
    id: uuid.UUID
    company: str
    position: str
    description: str | None
    start_date: date
    end_date: date | None
    is_current: bool
    location: str | None

    model_config = {"from_attributes": True}


class PublicEducation(BaseModel):
    id: uuid.UUID
    institution: str
    degree: str
    field: str | None
    description: str | None
    start_date: date
    end_date: date | None
    is_current: bool

    model_config = {"from_attributes": True}


class PublicSkill(BaseModel):
    id: uuid.UUID
    name: str
    category: str | None
    level: str | None
    is_transversal: bool

    model_config = {"from_attributes": True}


class PublicCertification(BaseModel):
    id: uuid.UUID
    name: str
    issuer: str
    issue_date: date | None
    credential_url: str | None

    model_config = {"from_attributes": True}


class PublicFacetResponse(BaseModel):
    slug: str
    title: str | None
    bio: str | None
    meta_title: str | None
    meta_description: str | None
    pdf_template: str

    full_name: str
    email: str
    phone: str | None
    photo_url: str | None
    website: str | None
    linkedin_url: str | None
    github_url: str | None

    experiences: list[PublicExperience] = []
    educations: list[PublicEducation] = []
    skills: list[PublicSkill] = []
    certifications: list[PublicCertification] = []
    projects: list[PublicProject] = []
