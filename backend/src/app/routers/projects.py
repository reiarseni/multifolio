import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.profile import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services import projects as projects_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/public/{project_id}", response_model=ProjectResponse)
async def get_public_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.images), selectinload(Project.attachments))
    )
    project = result.scalar_one_or_none()
    if not project:
        from fastapi import HTTPException, status

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


@router.delete("/{project_id}")
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await projects_service.delete_project(db, current_user.id, project_id)
    return {"message": "Project deleted"}
