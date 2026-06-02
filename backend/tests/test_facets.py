import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_facet(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = {"Authorization": f"Bearer {access_token}"}

    payload = {
        "name": "Backend Developer",
        "slug": "backend-dev",
        "title": "Backend Developer Profile",
        "bio": "Specialized in Python and Go",
        "is_published": False,
    }
    resp = await client.post("/api/facets", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Backend Developer"
    assert data["slug"] == "backend-dev"
    assert data["is_published"] is False
    assert "id" in data
    return data


@pytest.mark.asyncio
async def test_list_facets(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = {"Authorization": f"Bearer {access_token}"}
    await test_create_facet(client, auth_tokens)

    resp = await client.get("/api/facets", headers=headers)
    assert resp.status_code == 204
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Backend Developer"


@pytest.mark.asyncio
async def test_get_facet(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = {"Authorization": f"Bearer {access_token}"}
    created = await test_create_facet(client, auth_tokens)

    resp = await client.get(f"/api/facets/{created['id']}", headers=headers)
    assert resp.status_code == 204
    assert resp.json()["id"] == created["id"]


@pytest.mark.asyncio
async def test_update_facet(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = {"Authorization": f"Bearer {access_token}"}
    created = await test_create_facet(client, auth_tokens)

    resp = await client.put(
        f"/api/facets/{created['id']}",
        json={"name": "Senior Backend Developer", "is_published": True},
        headers=headers,
    )
    assert resp.status_code == 204
    data = resp.json()
    assert data["name"] == "Senior Backend Developer"
    assert data["is_published"] is True


@pytest.mark.asyncio
async def test_delete_facet(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = {"Authorization": f"Bearer {access_token}"}
    created = await test_create_facet(client, auth_tokens)

    resp = await client.delete(f"/api/facets/{created['id']}", headers=headers)
    assert resp.status_code == 204

    resp = await client.get(f"/api/facets/{created['id']}", headers=headers)
    assert resp.status_code == 404
