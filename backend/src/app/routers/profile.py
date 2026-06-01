import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.profile import (
    BaseProfileResponse,
    BaseProfileUpdate,
    CertificationCreate,
    CertificationResponse,
    EducationCreate,
    EducationResponse,
    SkillCreate,
    SkillResponse,
    WorkExperienceCreate,
    WorkExperienceResponse,
)
from app.services import profile_service

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=BaseProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await profile_service.get_profile(db, current_user.id)


@router.put("", response_model=BaseProfileResponse)
async def update_profile(
    body: BaseProfileUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await profile_service.update_profile(db, current_user.id, body)


@router.post("/experiences", response_model=WorkExperienceResponse)
async def create_experience(
    body: WorkExperienceCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await profile_service.add_experience(db, current_user.id, body)


@router.put("/experiences/{experience_id}", response_model=WorkExperienceResponse)
async def update_experience(
    experience_id: uuid.UUID,
    body: WorkExperienceCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await profile_service.update_experience(db, current_user.id, experience_id, body)


@router.delete("/experiences/{experience_id}")
async def delete_experience(
    experience_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await profile_service.delete_experience(db, current_user.id, experience_id)
    return {"message": "Experience deleted"}


@router.post("/education", response_model=EducationResponse)
async def create_education(
    body: EducationCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await profile_service.add_education(db, current_user.id, body)


@router.put("/education/{education_id}", response_model=EducationResponse)
async def update_education(
    education_id: uuid.UUID,
    body: EducationCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await profile_service.update_education(db, current_user.id, education_id, body)


@router.delete("/education/{education_id}")
async def delete_education(
    education_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await profile_service.delete_education(db, current_user.id, education_id)
    return {"message": "Education deleted"}


@router.post("/skills", response_model=SkillResponse)
async def create_skill(
    body: SkillCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await profile_service.add_skill(db, current_user.id, body)


@router.put("/skills/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: uuid.UUID,
    body: SkillCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await profile_service.update_skill(db, current_user.id, skill_id, body)


@router.delete("/skills/{skill_id}")
async def delete_skill(
    skill_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await profile_service.delete_skill(db, current_user.id, skill_id)
    return {"message": "Skill deleted"}


@router.post("/certifications", response_model=CertificationResponse)
async def create_certification(
    body: CertificationCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await profile_service.add_certification(db, current_user.id, body)


@router.put("/certifications/{cert_id}", response_model=CertificationResponse)
async def update_certification(
    cert_id: uuid.UUID,
    body: CertificationCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await profile_service.update_certification(db, current_user.id, cert_id, body)


@router.delete("/certifications/{cert_id}")
async def delete_certification(
    cert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await profile_service.delete_certification(db, current_user.id, cert_id)
    return {"message": "Certification deleted"}
