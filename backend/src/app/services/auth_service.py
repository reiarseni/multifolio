import secrets
from datetime import timedelta

import jwt
import redis.asyncio as aioredis
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
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


_DUMMY_HASH = hash_password("dummy-timing-protection-hash")


async def login_user(
    db: AsyncSession, redis: aioredis.Redis, email: str, password: str
) -> tuple[str, str]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # Always run bcrypt to avoid timing-based email enumeration
    candidate_hash = user.hashed_password if user else _DUMMY_HASH
    if not user or not verify_password(password, candidate_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    ttl = int(timedelta(days=settings.refresh_token_expire_days).total_seconds())
    await redis.setex(_redis_key(refresh_token), ttl, str(user.id))

    return access_token, refresh_token


async def refresh_tokens(redis: aioredis.Redis, refresh_token: str) -> tuple[str, str]:
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

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
    await redis.setex(_redis_key(new_refresh_token), ttl, uid)

    return new_access_token, new_refresh_token


async def logout_user(redis: aioredis.Redis, refresh_token: str) -> None:
    await redis.delete(_redis_key(refresh_token))


async def social_login_or_register(
    db: AsyncSession,
    provider: str,
    provider_user_id: str,
    email: str,
    name: str | None = None,
) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        user.auth_provider = provider
        user.provider_user_id = provider_user_id
    else:
        random_password = secrets.token_urlsafe(32)
        user = User(
            email=email,
            hashed_password=hash_password(random_password),
            auth_provider=provider,
            provider_user_id=provider_user_id,
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)
    return user


async def create_social_tokens(
    redis: aioredis.Redis, user: User
) -> tuple[str, str]:
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    ttl = int(timedelta(days=settings.refresh_token_expire_days).total_seconds())
    await redis.setex(_redis_key(refresh_token), ttl, str(user.id))

    return access_token, refresh_token
