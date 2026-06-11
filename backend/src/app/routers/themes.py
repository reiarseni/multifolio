from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.theme import ThemeResponse
from app.services import themes as themes_service

router = APIRouter(prefix="/themes", tags=["themes"])


@router.get("", response_model=list[ThemeResponse])
async def list_themes(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await themes_service.list_themes(db)
