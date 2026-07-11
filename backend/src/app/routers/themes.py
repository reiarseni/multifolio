import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.theme import ThemeCreate, ThemeResponse, ThemeUpdate
from app.services import themes as themes_service

router = APIRouter(prefix="/themes", tags=["themes"])


@router.get("", response_model=list[ThemeResponse])
async def list_themes(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await themes_service.list_themes(db, current_user.id)


@router.get("/community", response_model=list[ThemeResponse])
async def list_community_themes(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await themes_service.list_community_themes(db)


@router.get("/{id}", response_model=ThemeResponse)
async def get_theme(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await themes_service.get_theme(db, current_user.id, id)


@router.post("", response_model=ThemeResponse, status_code=201)
async def create_theme(
    data: ThemeCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await themes_service.create_theme(db, current_user.id, data)


@router.put("/{id}", response_model=ThemeResponse)
async def update_theme(
    id: uuid.UUID,
    data: ThemeUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await themes_service.update_theme(db, current_user.id, id, data)


@router.post("/{id}/publish", response_model=ThemeResponse)
async def publish_theme(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await themes_service.publish_theme(db, current_user.id, id)


@router.post("/{id}/unpublish", response_model=ThemeResponse)
async def unpublish_theme(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await themes_service.unpublish_theme(db, current_user.id, id)


@router.delete("/{id}", response_model=ThemeResponse)
async def delete_theme(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await themes_service.delete_theme(db, current_user.id, id)
