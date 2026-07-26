import secrets

from redis.asyncio import Redis

from httpx_oauth.clients.github import GitHubOAuth2
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback

from app.core.config import get_settings

settings = get_settings()

_SCOPE_SEPARATOR = " "
GOOGLE_SCOPES = ["openid", "profile", "email"]
GITHUB_SCOPES = ["read:user", "user:email"]

OAUTH_PROVIDERS = {
    "google": {
        "client_class": GoogleOAuth2,
        "scopes": GOOGLE_SCOPES,
    },
    "github": {
        "client_class": GitHubOAuth2,
        "scopes": GITHUB_SCOPES,
    },
}

_STATE_PREFIX = "oauth_state:"
_STATE_TTL = 600  # 10 minutes


def get_google_client() -> GoogleOAuth2:
    return GoogleOAuth2(
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
    )


def get_github_client() -> GitHubOAuth2:
    return GitHubOAuth2(
        client_id=settings.github_client_id,
        client_secret=settings.github_client_secret,
    )


def get_provider_client(provider: str):
    if provider == "google":
        return get_google_client()
    if provider == "github":
        return get_github_client()
    raise ValueError(f"Unknown provider: {provider}")


def get_provider_callback(provider: str, redirect_url: str) -> OAuth2AuthorizeCallback:
    client = get_provider_client(provider)
    return OAuth2AuthorizeCallback(client, redirect_url=redirect_url)


def generate_state() -> str:
    return secrets.token_urlsafe(32)


async def store_state(redis: Redis, state: str) -> None:
    await redis.setex(f"{_STATE_PREFIX}{state}", _STATE_TTL, "1")


async def validate_state(redis: Redis, state: str | None) -> bool:
    if not state:
        return False
    key = f"{_STATE_PREFIX}{state}"
    exists = await redis.get(key)
    if not exists:
        return False
    await redis.delete(key)
    return True
