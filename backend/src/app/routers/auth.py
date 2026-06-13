import redis.asyncio as aioredis
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import get_redis
from app.db.session import get_db_session
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services import auth_service

settings = get_settings()

router = APIRouter(tags=["auth"])

COOKIE_NAME = "refresh_token"
COOKIE_MAX_AGE = settings.refresh_token_expire_days * 24 * 60 * 60


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        path="/auth",
        max_age=COOKIE_MAX_AGE,
        secure=settings.is_production,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    user = await auth_service.register_user(db, body.email, body.password)
    return UserResponse(id=user.id, email=user.email)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    redis: aioredis.Redis = Depends(get_redis),
) -> TokenResponse:
    access_token, refresh_token = await auth_service.login_user(
        db, redis, body.email, body.password
    )
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
    redis: aioredis.Redis = Depends(get_redis),
) -> TokenResponse:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token"
        )
    access_token, new_refresh_token = await auth_service.refresh_tokens(redis, refresh_token)
    _set_refresh_cookie(response, new_refresh_token)
    return TokenResponse(access_token=access_token)


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
    redis: aioredis.Redis = Depends(get_redis),
) -> dict:
    if refresh_token:
        await auth_service.logout_user(redis, refresh_token)
    response.delete_cookie(key=COOKIE_NAME, path="/auth")
    return {"message": "Logged out"}
