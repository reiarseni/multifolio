from unittest.mock import patch

import pytest
from httpx import AsyncClient, Request, Response


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


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

MOCK_GITHUB_LANGUAGES = {
    "Python": 8000,
    "JavaScript": 2000,
}


def _make_response(status_code: int, json_data: dict | list | None = None) -> Response:
    import json as json_mod

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


# ── GET /api/github/repos ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_repos_empty(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    resp = await client.get("/api/github/repos", headers=_headers(access_token))
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_repos_requires_auth(client: AsyncClient):
    resp = await client.get("/api/github/repos")
    assert resp.status_code == 401


# ── POST /api/github/repos (link) ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_link_repo_success(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
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
            headers=_headers(access_token),
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "test-repo"
    assert data["stars"] == 42
    assert data["forks"] == 7


@pytest.mark.asyncio
async def test_link_repo_invalid_url(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    resp = await client.post(
        "/api/github/repos",
        json={"repo_url": "https://notgithub.com/user/repo"},
        headers=_headers(access_token),
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_link_repo_not_found(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    mock_client = MockAsyncClient(
        [
            _make_response(404),
        ]
    )

    with patch("app.services.github_service.httpx.AsyncClient", return_value=mock_client):
        resp = await client.post(
            "/api/github/repos",
            json={"repo_url": "https://github.com/user/nonexistent"},
            headers=_headers(access_token),
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_link_repo_duplicate(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    mock_client = MockAsyncClient(
        [
            _make_response(200, MOCK_GITHUB_REPO),
            _make_response(200, MOCK_GITHUB_LANGUAGES),
        ]
    )

    with patch("app.services.github_service.httpx.AsyncClient", return_value=mock_client):
        resp1 = await client.post(
            "/api/github/repos",
            json={"repo_url": "https://github.com/testuser/test-repo"},
            headers=_headers(access_token),
        )
    assert resp1.status_code == 201

    mock_client2 = MockAsyncClient(
        [
            _make_response(200, MOCK_GITHUB_REPO),
            _make_response(200, MOCK_GITHUB_LANGUAGES),
        ]
    )

    with patch("app.services.github_service.httpx.AsyncClient", return_value=mock_client2):
        resp2 = await client.post(
            "/api/github/repos",
            json={"repo_url": "https://github.com/testuser/test-repo"},
            headers=_headers(access_token),
        )
    assert resp2.status_code == 409


# ── DELETE /api/github/repos/{id} ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_unlink_repo(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    mock_client = MockAsyncClient(
        [
            _make_response(200, MOCK_GITHUB_REPO),
            _make_response(200, MOCK_GITHUB_LANGUAGES),
        ]
    )

    with patch("app.services.github_service.httpx.AsyncClient", return_value=mock_client):
        link_resp = await client.post(
            "/api/github/repos",
            json={"repo_url": "https://github.com/testuser/test-repo"},
            headers=_headers(access_token),
        )
    repo_id = link_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/github/repos/{repo_id}",
        headers=_headers(access_token),
    )
    assert del_resp.status_code == 204

    list_resp = await client.get("/api/github/repos", headers=_headers(access_token))
    assert len(list_resp.json()) == 0


@pytest.mark.asyncio
async def test_unlink_repo_not_found(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = await client.delete(
        f"/api/github/repos/{fake_id}",
        headers=_headers(access_token),
    )
    assert resp.status_code == 404


# ── POST /api/github/repos/sync ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_sync_repos(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    mock_client = MockAsyncClient(
        [
            _make_response(200, MOCK_GITHUB_REPO),
            _make_response(200, MOCK_GITHUB_LANGUAGES),
        ]
    )

    with patch("app.services.github_service.httpx.AsyncClient", return_value=mock_client):
        await client.post(
            "/api/github/repos",
            json={"repo_url": "https://github.com/testuser/test-repo"},
            headers=_headers(access_token),
        )

    updated_repo = {**MOCK_GITHUB_REPO, "stargazers_count": 100}
    mock_client2 = MockAsyncClient(
        [
            _make_response(200, updated_repo),
            _make_response(200, MOCK_GITHUB_LANGUAGES),
        ]
    )

    with patch("app.services.github_service.httpx.AsyncClient", return_value=mock_client2):
        sync_resp = await client.post(
            "/api/github/repos/sync",
            headers=_headers(access_token),
        )
    assert sync_resp.status_code == 200
    data = sync_resp.json()
    assert len(data) == 1
    assert data[0]["stars"] == 100
