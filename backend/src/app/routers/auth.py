import redis.asyncio as aioredis
from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import get_redis
from app.core.oauth import (
    generate_state,
    get_provider_client,
    store_state,
    validate_state,
)
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


PROVIDERS = ("google", "github")


@router.get("/{provider}/login")
async def oauth_login(provider: str, request: Request) -> RedirectResponse:
    if provider not in PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}",
        )

    client = get_provider_client(provider)
    state = generate_state()
    store_state(state)

    base_url = str(request.base_url).rstrip("/")
    redirect_url = f"{base_url}/auth/{provider}/callback"

    authorization_url = await client.get_authorization_url(
        redirect_uri=redirect_url,
        state=state,
    )

    return RedirectResponse(url=authorization_url)


@router.get("/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    response: Response = None,
    db: AsyncSession = Depends(get_db_session),
    redis: aioredis.Redis = Depends(get_redis),
):
    if provider not in PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}",
        )

    if error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"OAuth error: {error}",
        )

    if not validate_state(state):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired state parameter",
        )

    client = get_provider_client(provider)
    base_url = str(request.base_url).rstrip("/")
    redirect_url = f"{base_url}/auth/{provider}/callback"

    token = await client.get_access_token(code, redirect_url)
    access_token = token["access_token"]

    if provider == "google":
        user_info = await client.get_id_email(access_token)
        provider_user_id = user_info[0]
        email = user_info[1]
        name = user_info[2] if len(user_info) > 2 else None
    else:
        user_info = await client.get_profile(access_token)
        provider_user_id = str(user_info["id"])
        email = user_info.get("email")
        name = user_info.get("name")
        if not email:
            emails = await client.get_emails(access_token)
            email = emails[0]["email"] if emails else None

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve email from OAuth provider",
        )

    user = await auth_service.social_login_or_register(db, provider, provider_user_id, email, name)

    access_token_jwt, refresh_token = await auth_service.create_social_tokens(redis, user)

    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token_jwt)
