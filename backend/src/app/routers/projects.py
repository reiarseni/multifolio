import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.profile import Facet, Project, facet_projects
from app.models.user import User
from app.schemas.project import (
    ProjectAttachmentCreate,
    ProjectAttachmentResponse,
    ProjectCreate,
    ProjectImageCreate,
    ProjectImageResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services import projects as projects_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/public/{project_id}", response_model=ProjectResponse)
async def get_public_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    result = await db.execute(
        select(Project)
        .join(facet_projects, Project.id == facet_projects.c.project_id)
        .join(Facet, Facet.id == facet_projects.c.facet_id)
        .where(Project.id == project_id, Facet.is_published)
        .options(selectinload(Project.images), selectinload(Project.attachments))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return project


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await projects_service.list_projects(db, current_user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await projects_service.get_project(db, current_user.id, project_id)


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    body: ProjectCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await projects_service.create_project(db, current_user.id, body)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    body: ProjectUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await projects_service.update_project(db, current_user.id, project_id, body)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await projects_service.delete_project(db, current_user.id, project_id)


@router.post("/{project_id}/images", response_model=ProjectImageResponse, status_code=201)
async def add_project_image(
    project_id: uuid.UUID,
    body: ProjectImageCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await projects_service.add_image(db, current_user.id, project_id, body)


@router.delete("/{project_id}/images/{image_id}", status_code=204)
async def delete_project_image(
    project_id: uuid.UUID,
    image_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await projects_service.delete_image(db, current_user.id, project_id, image_id)


@router.post("/{project_id}/attachments", response_model=ProjectAttachmentResponse, status_code=201)
async def add_project_attachment(
    project_id: uuid.UUID,
    body: ProjectAttachmentCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await projects_service.add_attachment(db, current_user.id, project_id, body)


@router.delete("/{project_id}/attachments/{attachment_id}", status_code=204)
async def delete_project_attachment(
    project_id: uuid.UUID,
    attachment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await projects_service.delete_attachment(db, current_user.id, project_id, attachment_id)
