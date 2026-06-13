import pytest
import pytest_asyncio
from httpx import AsyncClient


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


_PROJECT = {"title": "My Portfolio", "description": "A personal portfolio site"}


@pytest_asyncio.fixture
async def created_project(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    resp = await client.post("/api/projects", json=_PROJECT, headers=_headers(token))
    assert resp.status_code == 201
    return resp.json(), _headers(token)


# ── CREATE ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    resp = await client.post("/api/projects", json=_PROJECT, headers=_headers(token))
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My Portfolio"
    assert data["description"] == "A personal portfolio site"
    assert "id" in data
    assert data["images"] == []
    assert data["attachments"] == []


@pytest.mark.asyncio
async def test_create_project_requires_auth(client: AsyncClient):
    resp = await client.post("/api/projects", json=_PROJECT)
    assert resp.status_code == 401


# ── LIST ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_projects_empty(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    resp = await client.get("/api/projects", headers=_headers(token))
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient, auth_tokens, created_project):
    _, h = created_project
    resp = await client.get("/api/projects", headers=h)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


# ── GET ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, created_project):
    project, h = created_project
    resp = await client.get(f"/api/projects/{project['id']}", headers=h)
    assert resp.status_code == 200
    assert resp.json()["id"] == project["id"]


@pytest.mark.asyncio
async def test_get_project_not_found(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = await client.get(f"/api/projects/{fake_id}", headers=_headers(token))
    assert resp.status_code == 404


# ── UPDATE ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, created_project):
    project, h = created_project
    resp = await client.put(
        f"/api/projects/{project['id']}",
        json={"title": "Updated Title", "github_url": "https://github.com/user/repo"},
        headers=h,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated Title"
    assert data["github_url"] == "https://github.com/user/repo"


# ── DELETE ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient, created_project):
    project, h = created_project
    resp = await client.delete(f"/api/projects/{project['id']}", headers=h)
    assert resp.status_code == 200

    resp = await client.get(f"/api/projects/{project['id']}", headers=h)
    assert resp.status_code == 404


# ── ISOLATION between users ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_project_isolation(client: AsyncClient, created_project):
    project, _ = created_project
    # second user registers and logs in
    await client.post("/auth/register", json={"email": "other@example.com", "password": "OtherPass1!"})
    login = await client.post("/auth/login", json={"email": "other@example.com", "password": "OtherPass1!"})
    other_token = login.json()["access_token"]
    other_h = _headers(other_token)

    # other user cannot see first user's project
    resp = await client.get(f"/api/projects/{project['id']}", headers=other_h)
    assert resp.status_code == 404

    # other user list is empty
    resp = await client.get("/api/projects", headers=other_h)
    assert resp.json() == []
