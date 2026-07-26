from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


@pytest.mark.asyncio
async def test_create_review_link(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    assert facet_resp.status_code == 201
    facet_id = facet_resp.json()["id"]

    resp = await client.post(
        "/api/review/links",
        json={"facet_id": facet_id},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "token" in data
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_validate_review_link(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

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

    resp = await client.get(f"/api/review/{token}/validate")
    assert resp.status_code == 200
    assert resp.json()["is_active"] is True


@pytest.mark.asyncio
async def test_list_review_links(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    facet_id = facet_resp.json()["id"]

    await client.post(
        "/api/review/links",
        json={"facet_id": facet_id},
        headers=headers,
    )

    resp = await client.get(f"/api/facets/{facet_id}/review-links", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_deactivate_review_link(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

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
    link_id = link_resp.json()["id"]

    resp = await client.delete(f"/api/review-links/{link_id}", headers=headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_create_comment_via_link(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

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
            "content": "Excelente portfolio!",
            "author_name": "Reclutador",
            "author_email": "reclutador@example.com",
            "section_ref": "experiencia-1",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["content"] == "Excelente portfolio!"
    assert data["author_name"] == "Reclutador"
    assert data["section_ref"] == "experiencia-1"


@pytest.mark.asyncio
async def test_list_comments_via_link(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

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

    await client.post(
        f"/api/review/{token}/comments",
        json={"content": "Comentario 1"},
    )

    resp = await client.get(f"/api/review/{token}/comments")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["content"] == "Comentario 1"


@pytest.mark.asyncio
async def test_reply_to_comment(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

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

    comment_resp = await client.post(
        f"/api/review/{token}/comments",
        json={"content": "Comentario padre"},
    )
    parent_id = comment_resp.json()["id"]

    resp = await client.post(
        f"/api/review/{token}/comments",
        json={"content": "Respuesta", "parent_id": parent_id},
    )
    assert resp.status_code == 201
    assert resp.json()["parent_id"] == parent_id


@pytest.mark.asyncio
async def test_resolve_comment(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

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

    comment_resp = await client.post(
        f"/api/review/{token}/comments",
        json={"content": "Para resolver"},
    )
    comment_id = comment_resp.json()["id"]

    resp = await client.patch(
        f"/api/comments/{comment_id}/resolve",
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "resolved"


@pytest.mark.asyncio
async def test_unread_count(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

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

    await client.post(
        f"/api/review/{token}/comments",
        json={"content": "Nuevo comentario"},
    )

    resp = await client.get("/api/dashboard/comments/unread", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["count"] > 0


@pytest.mark.asyncio
async def test_list_comments_by_facet(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

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

    await client.post(
        f"/api/review/{token}/comments",
        json={"content": "Comentario"},
    )

    resp = await client.get(f"/api/facets/{facet_id}/comments", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_invalid_link_returns_404(client: AsyncClient):
    resp = await client.get("/api/review/invalid-token/validate")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_comment_on_invalid_link_returns_404(client: AsyncClient):
    resp = await client.post(
        "/api/review/invalid-token/comments",
        json={"content": "Test"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_comment_wrong_parent_facet(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Facet A", "slug": "facet-a"},
        headers=headers,
    )
    facet_a_id = facet_resp.json()["id"]

    link_resp = await client.post(
        "/api/review/links",
        json={"facet_id": facet_a_id},
        headers=headers,
    )
    token = link_resp.json()["token"]

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Facet B", "slug": "facet-b"},
        headers=headers,
    )
    facet_b_id = facet_resp.json()["id"]

    link_resp = await client.post(
        "/api/review/links",
        json={"facet_id": facet_b_id},
        headers=headers,
    )
    token_a = link_resp.json()["token"]

    comment_resp = await client.post(
        f"/api/review/{token}/comments",
        json={"content": "Comment on A"},
    )
    parent_id = comment_resp.json()["id"]

    resp = await client.post(
        f"/api/review/{token_a}/comments",
        json={"content": "Reply to A from B", "parent_id": parent_id},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_resolve_comment_not_owner(client: AsyncClient, auth_tokens, db_session):
    from app.core.security import create_access_token
    from app.models.user import User as UserModel

    access_token, _ = auth_tokens
    headers = _headers(access_token)

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

    comment_resp = await client.post(
        f"/api/review/{token}/comments",
        json={"content": "Comment by guest"},
    )
    comment_id = comment_resp.json()["id"]

    other_user = UserModel(
        email="other@example.com",
        hashed_password="nope",
        is_active=True,
    )
    db_session.add(other_user)
    await db_session.commit()

    other_access = create_access_token(str(other_user.id))
    other_headers = {"Authorization": f"Bearer {other_access}"}

    resp = await client.patch(
        f"/api/comments/{comment_id}/resolve",
        headers=other_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_resolve_comment_not_found(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    resp = await client.patch(
        f"/api/comments/{uuid.uuid4()}/resolve",
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_deactivate_inactive_link_noop(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

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
    link_id = link_resp.json()["id"]

    await client.delete(f"/api/review-links/{link_id}", headers=headers)
    resp = await client.delete(f"/api/review-links/{link_id}", headers=headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_list_comments_no_facet(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    resp = await client.get(f"/api/facets/{uuid.uuid4()}/comments", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_review_links_no_facet(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    resp = await client.get(f"/api/facets/{uuid.uuid4()}/review-links", headers=headers)
    assert resp.status_code == 404
