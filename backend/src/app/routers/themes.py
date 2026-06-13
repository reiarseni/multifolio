import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.theme import ThemeResponse, ThemeCreate
from app.services import themes as themes_service

router = APIRouter(prefix="/themes", tags=["themes"])


@router.get("", response_model=list[ThemeResponse])
async def list_themes(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await themes_service.list_themes(db)


@router.post("", response_model=ThemeResponse)
async def create_theme(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    data: ThemeCreate = None,
):
    return await themes_service.create_theme(db, current_user.id, data)


@router.delete("/{id}", response_model=ThemeResponse)
async def delete_theme(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await themes_service.delete_theme(db, current_user.id, id)
