from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_review_link_facet_not_found(client: AsyncClient, auth_tokens, db_session):
    """Test that when a link references a deleted facet, validation returns 404."""
    from sqlalchemy import select

    from app.models.profile import Facet

    access_token, _ = auth_tokens
    headers = {"Authorization": f"Bearer {access_token}"}

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Link Facet", "slug": "link-facet"},
        headers=headers,
    )
    facet_id = uuid.UUID(facet_resp.json()["id"])

    link_resp = await client.post(
        "/api/review/links",
        json={"facet_id": str(facet_id)},
        headers=headers,
    )
    token = link_resp.json()["token"]

    result = await db_session.execute(select(Facet).where(Facet.id == facet_id))
    facet = result.scalar_one()
    await db_session.delete(facet)
    await db_session.commit()

    resp = await client.get(f"/api/review/{token}/validate")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_deactivate_link_not_found(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = {"Authorization": f"Bearer {access_token}"}

    import uuid

    resp = await client.delete(f"/api/review-links/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_deactivate_link_not_owner(client: AsyncClient, auth_tokens, db_session):
    from app.core.security import create_access_token
    from app.models.user import User as UserModel

    access_token, _ = auth_tokens
    headers = {"Authorization": f"Bearer {access_token}"}

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Owner Facet", "slug": "owner-facet"},
        headers=headers,
    )
    facet_id = facet_resp.json()["id"]

    link_resp = await client.post(
        "/api/review/links",
        json={"facet_id": facet_id},
        headers=headers,
    )
    link_id = link_resp.json()["id"]

    other_user = UserModel(
        email="other2@example.com",
        hashed_password="nope",
        is_active=True,
    )
    db_session.add(other_user)
    await db_session.commit()

    other_access = create_access_token(str(other_user.id))
    other_headers = {"Authorization": f"Bearer {other_access}"}

    resp = await client.delete(f"/api/review-links/{link_id}", headers=other_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_review_links_no_facet_owner(client: AsyncClient, auth_tokens, db_session):
    from app.core.security import create_access_token
    from app.models.user import User as UserModel

    access_token, _ = auth_tokens
    headers = {"Authorization": f"Bearer {access_token}"}

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "My Facet", "slug": "my-facet"},
        headers=headers,
    )
    facet_id = facet_resp.json()["id"]

    other_user = UserModel(
        email="other3@example.com",
        hashed_password="nope",
        is_active=True,
    )
    db_session.add(other_user)
    await db_session.commit()

    other_access = create_access_token(str(other_user.id))
    other_headers = {"Authorization": f"Bearer {other_access}"}

    resp = await client.get(f"/api/facets/{facet_id}/review-links", headers=other_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_comments_multiple_roots_and_replies(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = {"Authorization": f"Bearer {access_token}"}

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Comments Facet", "slug": "comments-facet"},
        headers=headers,
    )
    facet_id = facet_resp.json()["id"]

    link_resp = await client.post(
        "/api/review/links",
        json={"facet_id": facet_id},
        headers=headers,
    )
    token = link_resp.json()["token"]

    r1 = await client.post(
        f"/api/review/{token}/comments",
        json={"content": "Root 1"},
    )
    r1_id = r1.json()["id"]

    await client.post(
        f"/api/review/{token}/comments",
        json={"content": "Root 2"},
    )

    await client.post(
        f"/api/review/{token}/comments",
        json={"content": "Reply to Root 1", "parent_id": r1_id},
    )

    resp = await client.get(f"/api/review/{token}/comments")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
