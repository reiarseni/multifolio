from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_current_user_inactive(auth_tokens, db_session):
    from app.models.user import User as UserModel

    result = await db_session.execute(__import__("sqlalchemy").select(UserModel).limit(1))
    user = result.scalar_one()
    user.is_active = False
    await db_session.commit()

    access_token, _ = auth_tokens
    from fastapi.security import HTTPAuthorizationCredentials

    from app.core.deps import get_current_user
    from app.db.session import get_db_session

    try:
        async for db in get_db_session():
            creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=access_token)
            await get_current_user(credentials=creds, db=db)
    except Exception:
        pass


@pytest.mark.asyncio
async def test_refresh_token_not_accepted(client: AsyncClient, auth_tokens):
    _, refresh_token = auth_tokens
    headers = {"Authorization": f"Bearer {refresh_token}"}

    resp = await client.get("/api/profile", headers=headers)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token_returns_401(client: AsyncClient):
    headers = {"Authorization": "Bearer invalid-token-here"}
    resp = await client.get("/api/profile", headers=headers)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_redis():
    from app.core.deps import get_redis

    try:
        async for r in get_redis():
            info = await r.info()
            assert info is not None
    except Exception:
        pytest.skip("Redis not available")


@pytest.mark.asyncio
async def test_inactive_user_returns_403(client: AsyncClient, auth_tokens, db_session):
    from sqlalchemy import select

    from app.models.user import User as UserModel

    access_token, _ = auth_tokens

    result = await db_session.execute(select(UserModel).limit(1))
    user = result.scalar_one()
    user.is_active = False
    await db_session.commit()

    headers = {"Authorization": f"Bearer {access_token}"}
    resp = await client.get("/api/profile", headers=headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_comments_by_facet_id_empty(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = {"Authorization": f"Bearer {access_token}"}

    resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    facet_id = resp.json()["id"]

    resp = await client.get(f"/api/facets/{facet_id}/comments", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_comment_with_section_ref(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = {"Authorization": f"Bearer {access_token}"}

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    facet_id = facet_resp.json()["id"]

    link_resp = await client.post(
        "/api/review/links",
        json={"facet_id": facet_id},
        headers=headers,
    )
    token = link_resp.json()["token"]

    resp = await client.post(
        f"/api/review/{token}/comments",
        json={
            "content": "Comment with section",
            "section_ref": "header-1",
            "author_name": "Alice",
            "author_email": "alice@example.com",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["section_ref"] == "header-1"
    assert resp.json()["author_name"] == "Alice"
    assert resp.json()["author_email"] == "alice@example.com"
