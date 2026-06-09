import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import BaseProfile


async def get_profile_or_404(db: AsyncSession, user_id: uuid.UUID) -> BaseProfile:
    result = await db.execute(select(BaseProfile).where(BaseProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return profile
