import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import (
    BaseProfile,
    Certification,
    Education,
    Skill,
    WorkExperience,
)
from app.schemas.profile import (
    BaseProfileUpdate,
    CertificationCreate,
    CertificationUpdate,
    EducationCreate,
    EducationUpdate,
    SkillCreate,
    SkillUpdate,
    WorkExperienceCreate,
    WorkExperienceUpdate,
)


async def _get_profile(db: AsyncSession, user_id: uuid.UUID) -> BaseProfile | None:
    result = await db.execute(select(BaseProfile).where(BaseProfile.user_id == user_id))
    return result.scalar_one_or_none()


async def _get_or_create_profile(db: AsyncSession, user_id: uuid.UUID) -> BaseProfile:
    profile = await _get_profile(db, user_id)
    if profile is not None:
        return profile
    profile = BaseProfile(user_id=user_id, full_name="")
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def _load_full_profile(db: AsyncSession, profile_id: uuid.UUID) -> BaseProfile:
    result = await db.execute(
        select(BaseProfile)
        .where(BaseProfile.id == profile_id)
        .options(
            selectinload(BaseProfile.user),
            selectinload(BaseProfile.experiences),
            selectinload(BaseProfile.educations),
            selectinload(BaseProfile.skills),
            selectinload(BaseProfile.certifications),
        )
    )
    return result.scalar_one()


async def get_profile(db: AsyncSession, user_id: uuid.UUID) -> BaseProfile:
    profile = await _get_or_create_profile(db, user_id)
    return await _load_full_profile(db, profile.id)


async def update_profile(
    db: AsyncSession, user_id: uuid.UUID, data: BaseProfileUpdate
) -> BaseProfile:
    profile = await _get_or_create_profile(db, user_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    await db.commit()
    return await _load_full_profile(db, profile.id)


async def add_experience(
    db: AsyncSession, user_id: uuid.UUID, data: WorkExperienceCreate
) -> WorkExperience:
    profile = await _get_or_create_profile(db, user_id)
    experience = WorkExperience(profile_id=profile.id, **data.model_dump())
    db.add(experience)
    await db.commit()
    await db.refresh(experience)
    return experience


async def update_experience(
    db: AsyncSession, user_id: uuid.UUID, experience_id: uuid.UUID, data: WorkExperienceUpdate
) -> WorkExperience:
    result = await db.execute(
        select(WorkExperience)
        .join(BaseProfile, WorkExperience.profile_id == BaseProfile.id)
        .where(WorkExperience.id == experience_id, BaseProfile.user_id == user_id)
    )
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(exp, field, value)
    await db.commit()
    await db.refresh(exp)
    return exp


async def delete_experience(db: AsyncSession, user_id: uuid.UUID, experience_id: uuid.UUID) -> None:
    result = await db.execute(
        select(WorkExperience)
        .join(BaseProfile, WorkExperience.profile_id == BaseProfile.id)
        .where(WorkExperience.id == experience_id, BaseProfile.user_id == user_id)
    )
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(exp)
    await db.commit()


async def add_education(db: AsyncSession, user_id: uuid.UUID, data: EducationCreate) -> Education:
    profile = await _get_or_create_profile(db, user_id)
    education = Education(profile_id=profile.id, **data.model_dump())
    db.add(education)
    await db.commit()
    await db.refresh(education)
    return education


async def update_education(
    db: AsyncSession, user_id: uuid.UUID, education_id: uuid.UUID, data: EducationUpdate
) -> Education:
    result = await db.execute(
        select(Education)
        .join(BaseProfile, Education.profile_id == BaseProfile.id)
        .where(Education.id == education_id, BaseProfile.user_id == user_id)
    )
    edu = result.scalar_one_or_none()
    if not edu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(edu, field, value)
    await db.commit()
    await db.refresh(edu)
    return edu


async def delete_education(db: AsyncSession, user_id: uuid.UUID, education_id: uuid.UUID) -> None:
    result = await db.execute(
        select(Education)
        .join(BaseProfile, Education.profile_id == BaseProfile.id)
        .where(Education.id == education_id, BaseProfile.user_id == user_id)
    )
    edu = result.scalar_one_or_none()
    if not edu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(edu)
    await db.commit()


async def add_skill(db: AsyncSession, user_id: uuid.UUID, data: SkillCreate) -> Skill:
    profile = await _get_or_create_profile(db, user_id)
    skill = Skill(profile_id=profile.id, **data.model_dump())
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return skill


async def update_skill(
    db: AsyncSession, user_id: uuid.UUID, skill_id: uuid.UUID, data: SkillUpdate
) -> Skill:
    result = await db.execute(
        select(Skill)
        .join(BaseProfile, Skill.profile_id == BaseProfile.id)
        .where(Skill.id == skill_id, BaseProfile.user_id == user_id)
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(skill, field, value)
    await db.commit()
    await db.refresh(skill)
    return skill


async def delete_skill(db: AsyncSession, user_id: uuid.UUID, skill_id: uuid.UUID) -> None:
    result = await db.execute(
        select(Skill)
        .join(BaseProfile, Skill.profile_id == BaseProfile.id)
        .where(Skill.id == skill_id, BaseProfile.user_id == user_id)
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(skill)
    await db.commit()


async def add_certification(
    db: AsyncSession, user_id: uuid.UUID, data: CertificationCreate
) -> Certification:
    profile = await _get_or_create_profile(db, user_id)
    cert = Certification(profile_id=profile.id, **data.model_dump())
    db.add(cert)
    await db.commit()
    await db.refresh(cert)
    return cert


async def update_certification(
    db: AsyncSession, user_id: uuid.UUID, cert_id: uuid.UUID, data: CertificationUpdate
) -> Certification:
    result = await db.execute(
        select(Certification)
        .join(BaseProfile, Certification.profile_id == BaseProfile.id)
        .where(Certification.id == cert_id, BaseProfile.user_id == user_id)
    )
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cert, field, value)
    await db.commit()
    await db.refresh(cert)
    return cert


async def delete_certification(db: AsyncSession, user_id: uuid.UUID, cert_id: uuid.UUID) -> None:
    result = await db.execute(
        select(Certification)
        .join(BaseProfile, Certification.profile_id == BaseProfile.id)
        .where(Certification.id == cert_id, BaseProfile.user_id == user_id)
    )
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(cert)
    await db.commit()
