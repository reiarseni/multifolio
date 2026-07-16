import pytest
import pytest_asyncio
from httpx import AsyncClient


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

    resp = await client.get(
        f"/api/facets/{facet_data['id']}/review-links", headers=headers
    )
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

    list_resp = await client.get(
        f"/api/facets/{facet_data['id']}/review-links", headers=headers
    )
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
