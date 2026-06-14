import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import FacetThemeConfig, Theme
from app.schemas.theme import ThemeCreate

PREDEFINED_THEME_NAMES = {"minimal", "formal", "bold"}


async def list_themes(db: AsyncSession, user_id: uuid.UUID) -> list[Theme]:
    result = await db.execute(
        select(Theme)
        .where((Theme.is_public.is_(True)) | (Theme.owner_id == user_id))
        .order_by(Theme.name)
    )
    return list(result.scalars().all())


async def get_theme_or_404(db: AsyncSession, theme_id: uuid.UUID) -> Theme:
    result = await db.execute(select(Theme).where(Theme.id == theme_id))
    theme = result.scalar_one_or_none()
    if not theme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tema no encontrado")
    return theme


async def create_theme(db: AsyncSession, user_id: uuid.UUID, data: ThemeCreate) -> Theme:
    if data.name.lower() in PREDEFINED_THEME_NAMES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Nombre de tema predefinido del sistema no permitido",
        )

    theme = Theme(
        id=uuid.uuid4(),
        owner_id=user_id,
        name=data.name,
        tokens=data.tokens,
        is_public=data.is_public,
    )

    db.add(theme)
    await db.commit()
    await db.refresh(theme)

    return theme


async def delete_theme(db: AsyncSession, user_id: uuid.UUID, theme_id: uuid.UUID) -> Theme:
    theme = await get_theme_or_404(db, theme_id)

    if theme.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para eliminar este tema",
        )

    if theme.name.lower() in PREDEFINED_THEME_NAMES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No se pueden eliminar los temas predefinidos del sistema",
        )

    result = await db.execute(
        select(FacetThemeConfig).where(FacetThemeConfig.theme_id == theme_id).limit(1)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el tema porque está siendo usado por una faceta",
        )

    await db.delete(theme)
    await db.commit()

    return theme
