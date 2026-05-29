import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "SecurePass123!"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    resp = await client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "SecurePass123!"},
    )
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    resp = await client.post(
        "/auth/register",
        json={"email": "weak@example.com", "password": "short"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    resp = await client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "SecurePass123!"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "refresh_token" in resp.cookies


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user):
    resp = await client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "wrong-password"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient, auth_tokens):
    access_token, refresh_token = auth_tokens
    assert refresh_token is not None

    client.cookies.set("refresh_token", refresh_token)
    resp = await client.post("/auth/refresh")
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in resp.cookies


@pytest.mark.asyncio
async def test_refresh_without_cookie(client: AsyncClient):
    resp = await client.post("/auth/refresh")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rotates_token(client: AsyncClient, auth_tokens, redis_mock):
    _, refresh_token = auth_tokens
    assert refresh_token is not None

    resp1 = await client.post("/auth/refresh")
    assert resp1.status_code == 200
    assert "access_token" in resp1.json()
    # New refresh cookie is issued
    assert "refresh_token" in resp1.cookies


@pytest.mark.asyncio
async def test_logout_clears_cookie(client: AsyncClient, auth_tokens):
    _, refresh_token = auth_tokens
    client.cookies.set("refresh_token", refresh_token)
    resp = await client.post("/auth/logout")
    assert resp.status_code == 200
    assert resp.cookies.get("refresh_token") is None or resp.cookies.get("refresh_token") == ""
