import secrets
import time

from httpx_oauth.clients.github import GitHubOAuth2
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback

from app.core.config import get_settings

settings = get_settings()

SCOPE_SEPARATOR = " "
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


_STATE_STORE: dict[str, float] = {}
_STATE_TTL = 600  # 10 minutes


def store_state(state: str) -> None:
    _STATE_STORE[state] = time.time()


def validate_state(state: str | None) -> bool:
    if not state or state not in _STATE_STORE:
        return False
    created = _STATE_STORE.pop(state)
    return (time.time() - created) < _STATE_TTL
