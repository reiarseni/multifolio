import pytest
from httpx import AsyncClient

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.services.wcag import (
    contrast_ratio,
    luminance,
    validate_external_assets,
    validate_wcag,
)

# ── core/security.py ────────────────────────────────────────────────────────


def test_hash_and_verify_password():
    hashed = hash_password("SecurePass123!")
    assert hashed != "SecurePass123!"
    assert verify_password("SecurePass123!", hashed)
    assert not verify_password("WrongPassword!", hashed)


def test_create_and_decode_access_token():
    token = create_access_token("user-123")
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_create_and_decode_refresh_token():
    token = create_refresh_token("user-456")
    payload = decode_token(token)
    assert payload["sub"] == "user-456"
    assert payload["type"] == "refresh"


def test_decode_invalid_token():
    with pytest.raises(Exception):
        decode_token("invalid.token.here")


# ── core/oauth.py ───────────────────────────────────────────────────────────


def test_generate_state_is_unique():
    from app.core.oauth import generate_state, store_state, validate_state

    s1 = generate_state()
    s2 = generate_state()
    assert s1 != s2
    assert len(s1) > 16

    store_state(s1)
    assert validate_state(s1) is True
    assert validate_state(s2) is False
    assert validate_state(None) is False
    assert validate_state("") is False


def test_provider_client_google():
    from app.core.oauth import get_provider_client

    client = get_provider_client("google")
    assert client is not None


def test_provider_client_github():
    from app.core.oauth import get_provider_client

    client = get_provider_client("github")
    assert client is not None


def test_provider_client_unknown():
    from app.core.oauth import get_provider_client

    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider_client("gitlab")


def test_get_provider_callback():
    from app.core.oauth import get_provider_callback

    callback = get_provider_callback("github", "http://localhost:8000/auth/callback")
    assert callback is not None


# ── core/deps.py (via endpoints) ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_access_with_refresh_token_fails(client: AsyncClient, auth_tokens):
    _, refresh_token = auth_tokens
    headers = {"Authorization": f"Bearer {refresh_token}"}
    resp = await client.get("/api/projects", headers=headers)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_access_with_invalid_token_fails(client: AsyncClient):
    headers = {"Authorization": "Bearer invalid.token.here"}
    resp = await client.get("/api/projects", headers=headers)
    assert resp.status_code == 401


# ── services/wcag.py ────────────────────────────────────────────────────────


def test_luminance():
    assert luminance("#000000") == 0.0
    assert luminance("#ffffff") == 1.0
    assert luminance("#ff0000") > 0
    assert luminance("fff") == luminance("ffffff")


def test_contrast_ratio():
    assert contrast_ratio("#000000", "#ffffff") == 21.0
    assert contrast_ratio("#ffffff", "#000000") == 21.0
    assert contrast_ratio("#000000", "#000000") == 1.0
    assert contrast_ratio("#ff0000", "#ffffff") > 3.0


def test_validate_wcag_passes():
    tokens = {
        "color": {
            "background": "#ffffff",
            "primary": "#000000",
            "text_heading": "#111111",
            "text_body": "#222222",
            "text_muted": "#666666",
            "accent": "#333333",
            "surface": "#f5f5f5",
        }
    }
    errors = validate_wcag(tokens)
    assert len(errors) == 0


def test_validate_wcag_fails():
    tokens = {
        "color": {
            "background": "#ffffff",
            "primary": "#cccccc",
        }
    }
    errors = validate_wcag(tokens)
    assert len(errors) > 0
    assert "no cumple WCAG" in errors[0]


def test_validate_external_assets():
    tokens = {
        "color": {"primary": "#000000"},
        "fonts": {"url": "https://fonts.example.com/font.woff"},
    }
    errors = validate_external_assets(tokens)
    assert len(errors) == 1
    assert "fonts.url" in errors[0]


def test_validate_external_assets_no_errors():
    tokens = {
        "color": {"primary": "#000000"},
        "spacing": {"sm": "8px"},
    }
    errors = validate_external_assets(tokens)
    assert len(errors) == 0


def test_validate_external_assets_skips_non_dict():
    tokens = {
        "color": "#000000",
        "fonts": ["list", "of", "items"],
    }
    errors = validate_external_assets(tokens)
    assert len(errors) == 0


# ── services/auth_service.py (tokens without db.execute) ────────────────────


@pytest.mark.asyncio
async def test_refresh_with_invalid_token(client: AsyncClient):
    client.cookies.set("refresh_token", "invalid.jwt.token")
    resp = await client.post("/auth/refresh")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_access_token_as_refresh(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    client.cookies.set("refresh_token", access_token)
    resp = await client.post("/auth/refresh")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_without_cookie(client: AsyncClient):
    resp = await client.post("/auth/refresh")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_not_in_redis(client: AsyncClient):
    from app.core.security import create_refresh_token

    fake_refresh = create_refresh_token("00000000-0000-0000-0000-000000000000")
    client.cookies.set("refresh_token", fake_refresh)
    resp = await client.post("/auth/refresh")
    assert resp.status_code == 401


# ── Pydantic schema validators ──────────────────────────────────────────────


def test_register_password_too_long():
    from app.schemas.auth import RegisterRequest

    with pytest.raises(ValueError):
        RegisterRequest(email="test@test.com", password="a" * 129)


def test_login_password_too_long():
    from app.schemas.auth import LoginRequest

    with pytest.raises(ValueError):
        LoginRequest(email="test@test.com", password="a" * 129)


def test_facet_invalid_slug():
    from app.schemas.facet import FacetCreate

    with pytest.raises(ValueError):
        FacetCreate(name="Test", slug="INVALID SLUG")


def test_base_profile_response_dict_passthrough():
    from app.schemas.profile import BaseProfileResponse

    data = {
        "id": "00000000-0000-0000-0000-000000000000",
        "user_id": "00000000-0000-0000-0000-000000000000",
        "full_name": "Test User",
        "email": "test@test.com",
        "phone": None,
        "location": None,
        "title": None,
        "bio": None,
        "photo_url": None,
        "website": None,
        "linkedin_url": None,
        "github_url": None,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    result = BaseProfileResponse.model_validate(data)
    assert result.email == "test@test.com"


def test_facet_response_model_validator_dict_passthrough():
    from app.schemas.facet import FacetResponse

    data = {
        "id": "00000000-0000-0000-0000-000000000000",
        "user_id": "00000000-0000-0000-0000-000000000000",
        "name": "Test",
        "slug": "test",
        "title": "Test",
        "bio": "Bio",
        "meta_title": None,
        "meta_description": None,
        "pdf_template": "moderna",
        "is_published": False,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    result = FacetResponse.model_validate(data)
    assert result.name == "Test"
