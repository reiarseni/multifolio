import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Theme


async def list_themes(db: AsyncSession) -> list[Theme]:
    result = await db.execute(
        select(Theme).where(Theme.is_public.is_(True)).order_by(Theme.name)
    )
    return list(result.scalars().all())


async def get_theme_or_404(db: AsyncSession, theme_id: uuid.UUID) -> Theme:
    result = await db.execute(select(Theme).where(Theme.id == theme_id))
    theme = result.scalar_one_or_none()
    if not theme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tema no encontrado")
    return theme
