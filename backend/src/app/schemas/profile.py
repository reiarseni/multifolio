import uuid
from datetime import date, datetime

from pydantic import BaseModel


class WorkExperienceBase(BaseModel):
    company: str
    position: str
    description: str | None = None
    start_date: date
    end_date: date | None = None
    is_current: bool = False
    location: str | None = None
    sort_order: int = 0


class WorkExperienceCreate(WorkExperienceBase):
    pass


class WorkExperienceResponse(WorkExperienceBase):
    id: uuid.UUID
    profile_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EducationBase(BaseModel):
    institution: str
    degree: str
    field: str | None = None
    description: str | None = None
    start_date: date
    end_date: date | None = None
    is_current: bool = False
    sort_order: int = 0


class EducationCreate(EducationBase):
    pass


class EducationResponse(EducationBase):
    id: uuid.UUID
    profile_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SkillBase(BaseModel):
    name: str
    category: str | None = None
    level: str | None = None
    is_transversal: bool = False
    sort_order: int = 0


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: uuid.UUID
    profile_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class CertificationBase(BaseModel):
    name: str
    issuer: str
    issue_date: date | None = None
    expiry_date: date | None = None
    credential_url: str | None = None
    sort_order: int = 0


class CertificationCreate(CertificationBase):
    pass


class CertificationResponse(CertificationBase):
    id: uuid.UUID
    profile_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class BaseProfileUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    title: str | None = None
    bio: str | None = None
    photo_url: str | None = None
    website: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None


class BaseProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    email: str
    phone: str | None
    location: str | None
    title: str | None
    bio: str | None
    photo_url: str | None
    website: str | None
    linkedin_url: str | None
    github_url: str | None
    created_at: datetime
    updated_at: datetime
    experiences: list[WorkExperienceResponse] = []
    educations: list[EducationResponse] = []
    skills: list[SkillResponse] = []
    certifications: list[CertificationResponse] = []

    model_config = {"from_attributes": True}
