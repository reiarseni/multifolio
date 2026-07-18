from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from pydantic import ValidationError

from app.core.oauth import (
    generate_state,
    get_provider_callback,
    get_provider_client,
    store_state,
    validate_state,
)
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.facet import FacetBase, FacetResponse
from app.schemas.profile import BaseProfileResponse
from app.services.wcag import luminance, validate_external_assets, validate_wcag

ANY_FACET_ID = "00000000-0000-0000-0000-000000000000"


class TestValidationSync:
    def test_register_password_too_long(self):
        with pytest.raises(ValueError, match="at most 128"):
            RegisterRequest(email="a@b.com", password="x" * 129)

    def test_login_password_too_long(self):
        with pytest.raises(ValueError, match="at most 128"):
            LoginRequest(email="a@b.com", password="x" * 129)

    def test_facet_slug_invalid(self):
        with pytest.raises(ValueError, match="slug must contain only"):
            FacetBase(name="X", slug="BAD SLUG!", title="X", bio="X")

    def test_facet_response_from_dict(self):
        with pytest.raises(ValidationError):
            FacetResponse(data={})

    def test_profile_response_from_dict(self):
        with pytest.raises(ValidationError):
            BaseProfileResponse(data={})

    def test_get_provider_callback_google(self):
        cb = get_provider_callback("google", "http://localhost:3000/callback")
        assert cb is not None

    def test_get_provider_callback_github(self):
        cb = get_provider_callback("github", "http://localhost:3000/callback")
        assert cb is not None

    def test_wcag_luminance_short_hex(self):
        assert luminance("#fff") > 0.9

    def test_wcag_skip_missing_colors(self):
        assert validate_wcag({"color": {}}) == []

    def test_wcag_skip_non_dict_group(self):
        assert validate_external_assets({"colors": "not-a-dict"}) == []

    def test_wcag_fails_low_contrast(self):
        errors = validate_wcag({"color": {"primary": "#fff", "background": "#eee"}})
        assert len(errors) > 0

    def test_wcag_passes_good_contrast(self):
        errors = validate_wcag({"color": {"primary": "#000", "background": "#fff"}})
        assert len(errors) == 0

    def test_wcag_external_asset_error(self):
        errors = validate_external_assets({"color": {"primary": "url(http://evil.com/x)"}})
        assert len(errors) > 0


class TestOAuthSync:
    def test_generate_state_returns_random(self):
        s1 = generate_state()
        s2 = generate_state()
        assert len(s1) == 43
        assert s1 != s2

    def test_store_and_validate_state(self):
        state = generate_state()
        store_state(state)
        assert validate_state(state) is True

    def test_validate_state_invalid(self):
        assert validate_state(None) is False
        assert validate_state("nonexistent") is False

    def test_get_google_client(self):
        client = get_provider_client("google")
        assert client.__class__.__name__ == "GoogleOAuth2"

    def test_get_github_client(self):
        client = get_provider_client("github")
        assert client.__class__.__name__ == "GitHubOAuth2"

    def test_get_provider_client_invalid(self):
        with pytest.raises(ValueError, match="Unknown provider: invalid"):
            get_provider_client("invalid")


@pytest.mark.asyncio
@patch("app.routers.auth.get_provider_client")
async def test_oauth_callback_reaches_token_exchange(mock_get_provider, client: AsyncClient):
    mock_client = AsyncMock()
    mock_client.get_access_token.return_value = {"access_token": "fake_token"}
    mock_client.get_id_email = AsyncMock(return_value=("provider-uid", "oauth@test.com"))
    mock_get_provider.return_value = mock_client

    state = generate_state()
    store_state(state)
    resp = await client.get(f"/auth/google/callback?code=abc&state={state}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_oauth_login_google_redirect(client: AsyncClient):
    resp = await client.get("/auth/google/login")
    assert resp.status_code == 307


@pytest.mark.asyncio
async def test_oauth_login_invalid_provider(client: AsyncClient):
    resp = await client.get("/auth/invalid/login")
    assert resp.status_code == 400
    assert "Unsupported provider: invalid" in resp.text


@pytest.mark.asyncio
async def test_oauth_callback_invalid_provider(client: AsyncClient):
    resp = await client.get("/auth/invalid/callback")
    assert resp.status_code == 400
    assert "Unsupported provider: invalid" in resp.text


@pytest.mark.asyncio
async def test_oauth_callback_error(client: AsyncClient):
    resp = await client.get("/auth/google/callback?error=access_denied")
    assert resp.status_code == 403
    assert "access_denied" in resp.text


@pytest.mark.asyncio
async def test_oauth_callback_missing_state(client: AsyncClient):
    resp = await client.get("/auth/google/callback?code=abc")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_refresh_with_access_token(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    client.cookies.set("refresh_token", access_token)
    resp = await client.post("/auth/refresh")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_expired_token(client: AsyncClient, auth_tokens, redis_store):
    _, refresh_token = auth_tokens
    redis_store.clear()
    client.cookies.set("refresh_token", refresh_token)
    resp = await client.post("/auth/refresh")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    client.cookies.set("refresh_token", "not-a-valid-jwt-token")
    resp = await client.post("/auth/refresh")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_suggest_seo_invalid_token(client: AsyncClient):
    resp = await client.post(
        f"/api/facets/{ANY_FACET_ID}/seo/suggest",
        json={},
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_suggest_seo_refresh_token_as_access(client: AsyncClient, auth_tokens):
    _, refresh_token = auth_tokens
    resp = await client.post(
        f"/api/facets/{ANY_FACET_ID}/seo/suggest",
        json={},
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_seo_invalid_token(client: AsyncClient):
    resp = await client.put(
        f"/api/facets/{ANY_FACET_ID}/seo",
        json={"meta_title": "Test", "meta_description": "Test"},
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_seo_refresh_token_as_access(client: AsyncClient, auth_tokens):
    _, refresh_token = auth_tokens
    resp = await client.put(
        f"/api/facets/{ANY_FACET_ID}/seo",
        json={"meta_title": "Test", "meta_description": "Test"},
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
@patch("app.routers.health.aioredis.from_url")
async def test_health_redis_down(mock_from_url, client: AsyncClient):
    mock_redis = AsyncMock()
    mock_redis.ping.side_effect = Exception("Redis connection refused")
    mock_from_url.return_value = mock_redis
    resp = await client.get("/health")
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_get_seo_invalid_token(client: AsyncClient):
    resp = await client.get(
        f"/api/facets/{ANY_FACET_ID}/seo",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert resp.status_code == 401
