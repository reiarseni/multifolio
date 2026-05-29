from datetime import timedelta

import redis.asyncio as aioredis
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User

settings = get_settings()

REFRESH_TOKEN_PREFIX = "refresh_token:"


def _redis_key(token: str) -> str:
    return f"{REFRESH_TOKEN_PREFIX}{token}"


async def register_user(db: AsyncSession, email: str, password: str) -> User:
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(
    db: AsyncSession, redis: aioredis.Redis, email: str, password: str
) -> tuple[str, str]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    ttl = int(timedelta(days=settings.refresh_token_expire_days).total_seconds())
    await redis.setex(_redis_key(refresh_token), ttl, str(user.id))

    return access_token, refresh_token


async def refresh_tokens(redis: aioredis.Redis, refresh_token: str) -> tuple[str, str]:
    user_id = await redis.get(_redis_key(refresh_token))
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
        )

    await redis.delete(_redis_key(refresh_token))

    uid = user_id.decode() if isinstance(user_id, bytes) else user_id
    new_access_token = create_access_token(uid)
    new_refresh_token = create_refresh_token(uid)

    ttl = int(timedelta(days=settings.refresh_token_expire_days).total_seconds())
    await redis.setex(_redis_key(new_refresh_token), ttl, user_id)

    return new_access_token, new_refresh_token


async def logout_user(redis: aioredis.Redis, refresh_token: str) -> None:
    await redis.delete(_redis_key(refresh_token))
