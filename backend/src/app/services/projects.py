import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import BaseProfile, Project, ProjectAttachment, ProjectImage
from app.schemas.project import (
    ProjectAttachmentCreate,
    ProjectCreate,
    ProjectImageCreate,
    ProjectUpdate,
)


async def _get_profile(db: AsyncSession, user_id: uuid.UUID) -> BaseProfile | None:
    result = await db.execute(select(BaseProfile).where(BaseProfile.user_id == user_id))
    return result.scalar_one_or_none()


async def _ensure_profile(db: AsyncSession, user_id: uuid.UUID) -> BaseProfile:
    profile = await _get_profile(db, user_id)
    if profile is None:
        profile = BaseProfile(user_id=user_id, full_name="")
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


async def _get_user_project(db: AsyncSession, user_id: uuid.UUID, project_id: uuid.UUID) -> Project:
    profile = await _get_profile(db, user_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id, Project.profile_id == profile.id)
        .options(selectinload(Project.images), selectinload(Project.attachments))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return project


async def list_projects(db: AsyncSession, user_id: uuid.UUID) -> list[Project]:
    profile = await _get_profile(db, user_id)
    if profile is None:
        return []
    result = await db.execute(
        select(Project)
        .where(Project.profile_id == profile.id)
        .order_by(Project.sort_order)
        .options(selectinload(Project.images), selectinload(Project.attachments))
    )
    return list(result.scalars().all())


async def get_project(db: AsyncSession, user_id: uuid.UUID, project_id: uuid.UUID) -> Project:
    return await _get_user_project(db, user_id, project_id)


async def create_project(db: AsyncSession, user_id: uuid.UUID, data: ProjectCreate) -> Project:
    profile = await _ensure_profile(db, user_id)
    project = Project(profile_id=profile.id, **data.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    result = await db.execute(
        select(Project)
        .where(Project.id == project.id)
        .options(selectinload(Project.images), selectinload(Project.attachments))
    )
    return result.scalar_one()


async def update_project(
    db: AsyncSession, user_id: uuid.UUID, project_id: uuid.UUID, data: ProjectUpdate
) -> Project:
    project = await _get_user_project(db, user_id, project_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    await db.commit()
    await db.refresh(project)
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.images), selectinload(Project.attachments))
    )
    return result.scalar_one()


async def delete_project(db: AsyncSession, user_id: uuid.UUID, project_id: uuid.UUID) -> None:
    project = await _get_user_project(db, user_id, project_id)
    await db.delete(project)
    await db.commit()


async def add_image(
    db: AsyncSession, user_id: uuid.UUID, project_id: uuid.UUID, data: ProjectImageCreate
) -> ProjectImage:
    await _get_user_project(db, user_id, project_id)
    image = ProjectImage(project_id=project_id, **data.model_dump())
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return image


async def delete_image(
    db: AsyncSession, user_id: uuid.UUID, project_id: uuid.UUID, image_id: uuid.UUID
) -> None:
    await _get_user_project(db, user_id, project_id)
    result = await db.execute(
        select(ProjectImage).where(
            ProjectImage.id == image_id,
            ProjectImage.project_id == project_id,
        )
    )
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(image)
    await db.commit()


async def add_attachment(
    db: AsyncSession, user_id: uuid.UUID, project_id: uuid.UUID, data: ProjectAttachmentCreate
) -> ProjectAttachment:
    await _get_user_project(db, user_id, project_id)
    attachment = ProjectAttachment(project_id=project_id, **data.model_dump())
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)
    return attachment


async def delete_attachment(
    db: AsyncSession, user_id: uuid.UUID, project_id: uuid.UUID, attachment_id: uuid.UUID
) -> None:
    await _get_user_project(db, user_id, project_id)
    result = await db.execute(
        select(ProjectAttachment).where(
            ProjectAttachment.id == attachment_id,
            ProjectAttachment.project_id == project_id,
        )
    )
    attachment = result.scalar_one_or_none()
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(attachment)
    await db.commit()
