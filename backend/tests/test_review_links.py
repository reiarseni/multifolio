import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Facet
from app.schemas.review_link import ReviewLinkCreate
from app.services import review_link_service


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def created_facet(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    payload = {
        "name": "Test Facet Review",
        "slug": "test-facet-review",
        "title": "Test",
        "bio": "Test bio",
        "is_published": False,
    }
    resp = await client.post("/api/facets", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json(), headers


@pytest.mark.asyncio
async def test_create_review_link(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet
    resp = await client.post(
        f"/api/facets/{facet_data['id']}/review-links",
        json={},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "token" in data
    assert data["requires_password"] is False
    assert data["is_used"] is False


@pytest.mark.asyncio
async def test_create_review_link_with_password(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet
    resp = await client.post(
        f"/api/facets/{facet_data['id']}/review-links",
        json={"password": "secret123", "label": "Test link"},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["requires_password"] is True
    assert data["label"] == "Test link"


@pytest.mark.asyncio
async def test_create_review_link_with_expiration(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet
    resp = await client.post(
        f"/api/facets/{facet_data['id']}/review-links",
        json={"expires_in_hours": 72},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["expires_at"] is not None
    assert data["single_use"] is True


@pytest.mark.asyncio
async def test_list_review_links(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet

    await client.post(
        f"/api/facets/{facet_data['id']}/review-links",
        json={"label": "Link 1"},
        headers=headers,
    )
    await client.post(
        f"/api/facets/{facet_data['id']}/review-links",
        json={"label": "Link 2"},
        headers=headers,
    )

    resp = await client.get(f"/api/facets/{facet_data['id']}/review-links", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_delete_review_link(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet

    create_resp = await client.post(
        f"/api/facets/{facet_data['id']}/review-links",
        json={"label": "To delete"},
        headers=headers,
    )
    link_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/review-links/{link_id}", headers=headers)
    assert resp.status_code == 204

    list_resp = await client.get(f"/api/facets/{facet_data['id']}/review-links", headers=headers)
    assert len(list_resp.json()) == 0


@pytest.mark.asyncio
async def test_access_link_without_password(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet

    create_resp = await client.post(
        f"/api/facets/{facet_data['id']}/review-links",
        json={},
        headers=headers,
    )
    token = create_resp.json()["token"]

    resp = await client.get(f"/api/review/{token}/access")
    assert resp.status_code == 200
    data = resp.json()
    assert data["facet_id"] == facet_data["id"]


@pytest.mark.asyncio
async def test_access_link_with_password(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet

    create_resp = await client.post(
        f"/api/facets/{facet_data['id']}/review-links",
        json={"password": "secret123"},
        headers=headers,
    )
    token = create_resp.json()["token"]

    resp = await client.get(f"/api/review/{token}/access")
    assert resp.status_code == 401

    resp = await client.post(
        f"/api/review/{token}/validate",
        json={"password": "wrong"},
    )
    assert resp.status_code == 401

    resp = await client.post(
        f"/api/review/{token}/validate",
        json={"password": "secret123"},
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.asyncio
async def test_single_use_link(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet

    create_resp = await client.post(
        f"/api/facets/{facet_data['id']}/review-links",
        json={"password": "secret123"},
        headers=headers,
    )
    token = create_resp.json()["token"]

    resp = await client.post(
        f"/api/review/{token}/validate",
        json={"password": "secret123"},
    )
    assert resp.status_code == 200

    resp = await client.post(
        f"/api/review/{token}/validate",
        json={"password": "secret123"},
    )
    assert resp.status_code == 410


@pytest.mark.asyncio
async def test_invalid_token(client: AsyncClient):
    resp = await client.get("/api/review/invalid-token/access")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_password_too_short(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet
    resp = await client.post(
        f"/api/facets/{facet_data['id']}/review-links",
        json={"password": "123"},
        headers=headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_delete_nonexistent_link(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    resp = await client.delete(f"/api/review-links/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_link_with_password_and_expiration(
    client: AsyncClient, auth_tokens, created_facet
):
    facet_data, headers = created_facet
    resp = await client.post(
        f"/api/facets/{facet_data['id']}/review-links",
        json={"password": "secret123", "expires_in_hours": 24},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["requires_password"] is True
    assert data["expires_at"] is not None
    assert data["single_use"] is True


@pytest.mark.asyncio
async def test_list_links_empty(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet
    resp = await client.get(f"/api/facets/{facet_data['id']}/review-links", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_access_link_requires_password_no_password_given(
    client: AsyncClient, auth_tokens, created_facet
):
    facet_data, headers = created_facet

    create_resp = await client.post(
        f"/api/facets/{facet_data['id']}/review-links",
        json={"password": "secret123"},
        headers=headers,
    )
    token = create_resp.json()["token"]

    resp = await client.post(
        f"/api/review/{token}/validate",
        json={"password": "secret123"},
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.asyncio
async def test_create_link_label_optional(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet
    resp = await client.post(
        f"/api/facets/{facet_data['id']}/review-links",
        json={"label": "My Link"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["label"] == "My Link"


@pytest.mark.asyncio
async def test_service_create_review_link(db_session: AsyncSession):
    user_id = uuid.uuid4()
    facet = Facet(user_id=user_id, name="Test", slug="test-service")
    db_session.add(facet)
    await db_session.commit()
    await db_session.refresh(facet)

    data = ReviewLinkCreate(password="test123", expires_in_hours=24)
    link = await review_link_service.create_review_link(db_session, user_id, facet.id, data)
    assert link.password_hash is not None
    assert link.expires_at is not None
    assert link.single_use is True


@pytest.mark.asyncio
async def test_service_validate_link_not_found(db_session: AsyncSession):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        await review_link_service.validate_link_access(db_session, "invalid-token")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_service_mark_as_used(db_session: AsyncSession):
    user_id = uuid.uuid4()
    facet = Facet(user_id=user_id, name="Test", slug="test-mark")
    db_session.add(facet)
    await db_session.commit()
    await db_session.refresh(facet)

    data = ReviewLinkCreate(password="test123")
    link = await review_link_service.create_review_link(db_session, user_id, facet.id, data)

    await review_link_service.mark_as_used(db_session, link.id)

    from sqlalchemy import select

    from app.models.review_link import ReviewLink

    result = await db_session.execute(select(ReviewLink).where(ReviewLink.id == link.id))
    updated_link = result.scalar_one()
    assert updated_link.used_at is not None
