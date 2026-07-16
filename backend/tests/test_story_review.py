from __future__ import annotations

import pytest
from httpx import AsyncClient


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


@pytest.mark.asyncio
async def test_create_story_section(client: AsyncClient, auth_tokens):
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
        f"/api/facets/{facet_id}/story/sections",
        json={
            "section_type": "proceso",
            "title": "Mi Proceso",
            "content": "Descripción del proceso",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Mi Proceso"
    assert data["section_type"] == "proceso"


@pytest.mark.asyncio
async def test_get_story(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    facet_id = facet_resp.json()["id"]

    await client.post(
        f"/api/facets/{facet_id}/story/sections",
        json={"section_type": "proceso", "title": "S1", "content": "C1"},
        headers=headers,
    )

    resp = await client.get(f"/api/facets/{facet_id}/story", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_update_story_section(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    facet_id = facet_resp.json()["id"]

    section_resp = await client.post(
        f"/api/facets/{facet_id}/story/sections",
        json={"section_type": "proceso", "title": "Old", "content": "Old content"},
        headers=headers,
    )
    section_id = section_resp.json()["id"]

    resp = await client.patch(
        f"/api/story/sections/{section_id}",
        json={"title": "New Title"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "New Title"


@pytest.mark.asyncio
async def test_delete_story_section(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    facet_id = facet_resp.json()["id"]

    section_resp = await client.post(
        f"/api/facets/{facet_id}/story/sections",
        json={"section_type": "proceso", "title": "To Delete", "content": "Delete me"},
        headers=headers,
    )
    section_id = section_resp.json()["id"]

    resp = await client.delete(f"/api/story/sections/{section_id}", headers=headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_reorder_story_sections(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    facet_id = facet_resp.json()["id"]

    s1 = await client.post(
        f"/api/facets/{facet_id}/story/sections",
        json={"section_type": "proceso", "title": "S1", "content": "C1", "order": 0},
        headers=headers,
    )
    s2 = await client.post(
        f"/api/facets/{facet_id}/story/sections",
        json={"section_type": "solucion", "title": "S2", "content": "C2", "order": 1},
        headers=headers,
    )

    resp = await client.put(
        f"/api/facets/{facet_id}/story/reorder",
        json={"section_ids": [s2.json()["id"], s1.json()["id"]]},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["title"] == "S2"
    assert data[1]["title"] == "S1"


@pytest.mark.asyncio
async def test_create_review_link(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    facet_id = facet_resp.json()["id"]

    resp = await client.post(
        f"/api/facets/{facet_id}/review-links",
        json={"label": "Recruiter Link"},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["label"] == "Recruiter Link"
    assert data["requires_password"] is False


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
        f"/api/facets/{facet_id}/review-links",
        json={"label": "Link 1"},
        headers=headers,
    )

    resp = await client.get(f"/api/facets/{facet_id}/review-links", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_delete_review_link(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    facet_id = facet_resp.json()["id"]

    link_resp = await client.post(
        f"/api/facets/{facet_id}/review-links",
        json={"label": "To Delete"},
        headers=headers,
    )
    link_id = link_resp.json()["id"]

    resp = await client.delete(f"/api/review-links/{link_id}", headers=headers)
    assert resp.status_code == 204


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
        f"/api/facets/{facet_id}/review-links",
        json={"label": "Valid Link"},
        headers=headers,
    )
    token = link_resp.json()["token"]

    resp = await client.post(
        f"/api/review/{token}/validate",
        json={},
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.asyncio
async def test_access_review_link(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    facet_id = facet_resp.json()["id"]

    link_resp = await client.post(
        f"/api/facets/{facet_id}/review-links",
        json={"label": "Access Link"},
        headers=headers,
    )
    token = link_resp.json()["token"]

    resp = await client.get(f"/api/review/{token}/access")
    assert resp.status_code == 200
    assert resp.json()["label"] == "Access Link"
