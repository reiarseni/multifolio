from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Theme

MOCK_LLM_RESPONSE = """
{
  "title": "Test Repository - A Portfolio Project",
  "description": "A test repository showcase for portfolio.",
  "markdown_content": "# Overview\\nA test project."
}
"""

MOCK_GITHUB_REPO = {
    "name": "test-repo",
    "full_name": "testuser/test-repo",
    "description": "A test repository",
    "stargazers_count": 42,
    "forks_count": 7,
    "language": "Python",
    "pushed_at": "2026-07-10T12:00:00Z",
    "archived": False,
}

MOCK_GITHUB_LANGUAGES = {"Python": 8000, "JavaScript": 2000}

MOCK_GITHUB_README = {
    "content": "IyB0ZXN0LXJlcG8KTXkgdGVzdCByZXBvc2l0b3J5",
    "encoding": "base64",
}


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


def _make_response(status_code: int, json_data: dict | list | None = None):
    import json as json_mod

    from httpx import Request, Response

    content = json_mod.dumps(json_data or {}).encode()
    return Response(
        status_code=status_code,
        content=content,
        headers={"content-type": "application/json"},
        request=Request("GET", "https://api.github.com/test"),
    )


class MockAsyncClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self._call_count = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def get(self, url, **kwargs):
        if self._call_count < len(self._responses):
            resp = self._responses[self._call_count]
            self._call_count += 1
            return resp
        return _make_response(404)


@pytest_asyncio.fixture
async def seeded_themes(db_session: AsyncSession):
    themes = [
        Theme(
            name="minimal",
            tokens={"color": {"primary": "#2c2c2c"}, "typography": {}, "spacing": {}, "shape": {}},
            is_public=True,
        ),
        Theme(
            name="formal",
            tokens={"color": {"primary": "#1a3a5c"}, "typography": {}, "spacing": {}, "shape": {}},
            is_public=True,
        ),
        Theme(
            name="bold",
            tokens={"color": {"primary": "#7c3aed"}, "typography": {}, "spacing": {}, "shape": {}},
            is_public=True,
        ),
    ]
    for t in themes:
        db_session.add(t)
    await db_session.commit()
    for t in themes:
        await db_session.refresh(t)
    return themes


@pytest_asyncio.fixture
async def created_facet(client: AsyncClient, auth_tokens, seeded_themes):
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
    return resp.json(), headers


@pytest_asyncio.fixture
async def linked_repo(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = {"Authorization": f"Bearer {access_token}"}
    mock_client = MockAsyncClient(
        [
            _make_response(200, MOCK_GITHUB_REPO),
            _make_response(200, MOCK_GITHUB_LANGUAGES),
        ]
    )
    with patch("app.services.github_service.httpx.AsyncClient", return_value=mock_client):
        resp = await client.post(
            "/api/github/repos",
            json={"repo_url": "https://github.com/testuser/test-repo"},
            headers=headers,
        )
    assert resp.status_code == 201
    return resp.json(), headers


# ── POST /api/github/import/analyze ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_analyze_import_success(client: AsyncClient, auth_tokens, created_facet, linked_repo):
    facet, headers = created_facet
    repo, _ = linked_repo

    with patch(
        "app.services.github_import_service._call_llm",
        return_value=MOCK_LLM_RESPONSE,
    ):
        with patch(
            "app.services.github_import_service._fetch_readme",
            return_value="# test-repo\nMy test repository",
        ):
            resp = await client.post(
                "/api/github/import/analyze",
                json={"repo_ids": [repo["id"]], "facet_id": facet["id"]},
                headers=headers,
            )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["projects"]) == 1
    assert data["projects"][0]["title"] == "Test Repository - A Portfolio Project"
    assert data["projects"][0]["repo_id"] == repo["id"]


@pytest.mark.asyncio
async def test_analyze_import_requires_auth(client: AsyncClient):
    resp = await client.post(
        "/api/github/import/analyze",
        json={"repo_ids": [], "facet_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_analyze_import_facet_not_found(client: AsyncClient, auth_tokens, linked_repo):
    access_token, _ = auth_tokens
    headers = {"Authorization": f"Bearer {access_token}"}
    repo, _ = linked_repo

    fake_facet_id = "00000000-0000-0000-0000-000000000000"
    resp = await client.post(
        "/api/github/import/analyze",
        json={"repo_ids": [repo["id"]], "facet_id": fake_facet_id},
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_analyze_import_repo_not_found(client: AsyncClient, auth_tokens, created_facet):
    facet, headers = created_facet

    fake_repo_id = "00000000-0000-0000-0000-000000000000"
    resp = await client.post(
        "/api/github/import/analyze",
        json={"repo_ids": [fake_repo_id], "facet_id": facet["id"]},
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_analyze_import_llm_parse_error(
    client: AsyncClient, auth_tokens, created_facet, linked_repo
):
    facet, headers = created_facet
    repo, _ = linked_repo

    with patch(
        "app.services.github_import_service._call_llm",
        return_value="not valid json",
    ):
        with patch(
            "app.services.github_import_service._fetch_readme",
            return_value="# readme",
        ):
            resp = await client.post(
                "/api/github/import/analyze",
                json={"repo_ids": [repo["id"]], "facet_id": facet["id"]},
                headers=headers,
            )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["projects"]) == 1
    assert data["projects"][0]["title"] == repo["name"]


@pytest.mark.asyncio
async def test_confirm_import_creates_projects(client: AsyncClient, auth_tokens, created_facet):
    facet, headers = created_facet
    facet_id = facet["id"]

    await client.post(
        "/api/github/import/confirm",
        json={
            "facet_id": facet_id,
            "projects": [
                {
                    "repo_id": "00000000-0000-0000-0000-000000000001",
                    "title": "Project Alpha",
                    "description": "Alpha desc",
                    "markdown_content": "# Alpha",
                    "github_url": "https://github.com/user/alpha",
                },
                {
                    "repo_id": "00000000-0000-0000-0000-000000000002",
                    "title": "Project Beta",
                    "description": "Beta desc",
                    "markdown_content": "# Beta",
                    "github_url": "https://github.com/user/beta",
                },
            ],
        },
        headers=headers,
    )

    project_resp = await client.get("/api/projects", headers=headers)
    assert project_resp.status_code == 200
    projects = project_resp.json()
    assert len(projects) == 2
    titles = {p["title"] for p in projects}
    assert "Project Alpha" in titles
    assert "Project Beta" in titles


# ── POST /api/github/import/confirm ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_confirm_import_success(client: AsyncClient, auth_tokens, created_facet):
    facet, headers = created_facet

    resp = await client.post(
        "/api/github/import/confirm",
        json={
            "facet_id": facet["id"],
            "projects": [
                {
                    "repo_id": "00000000-0000-0000-0000-000000000001",
                    "title": "My Portfolio Project",
                    "description": "A great project",
                    "markdown_content": "# Details\nMore content here.",
                    "github_url": "https://github.com/testuser/test-repo",
                }
            ],
        },
        headers=headers,
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1
    assert len(data["project_ids"]) == 1
    assert "importado" in data["message"]


@pytest.mark.asyncio
async def test_confirm_import_requires_auth(client: AsyncClient):
    resp = await client.post(
        "/api/github/import/confirm",
        json={"facet_id": "00000000-0000-0000-0000-000000000000", "projects": []},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_confirm_import_facet_not_found(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = {"Authorization": f"Bearer {access_token}"}

    resp = await client.post(
        "/api/github/import/confirm",
        json={
            "facet_id": "00000000-0000-0000-0000-000000000000",
            "projects": [
                {
                    "repo_id": "00000000-0000-0000-0000-000000000001",
                    "title": "Test",
                    "description": "Test",
                    "markdown_content": "",
                    "github_url": "https://github.com/testuser/test-repo",
                }
            ],
        },
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_confirm_import_wrong_user(client: AsyncClient, auth_tokens, created_facet):
    facet, headers = created_facet

    resp = await client.post(
        "/auth/register",
        json={"email": "other@test.com", "password": "OtherPass123!"},
    )
    assert resp.status_code == 201
    login_resp = await client.post(
        "/auth/login",
        json={"email": "other@test.com", "password": "OtherPass123!"},
    )
    other_token = login_resp.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    resp = await client.post(
        "/api/github/import/confirm",
        json={
            "facet_id": facet["id"],
            "projects": [
                {
                    "repo_id": "00000000-0000-0000-0000-000000000001",
                    "title": "Test",
                    "description": "Test",
                    "markdown_content": "",
                    "github_url": "https://github.com/user/repo",
                }
            ],
        },
        headers=other_headers,
    )
    assert resp.status_code == 403
