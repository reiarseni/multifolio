from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


_KEYWORDS_RESPONSE = """{
  "role": "Backend Developer",
  "keywords": ["Python", "FastAPI", "PostgreSQL"],
  "industry": "Technology",
  "seniority_level": "mid"
}"""

_META_RESPONSE = """{
  "variants": [
    {
      "title": "Backend Developer | Python & FastAPI",
      "description": "Backend Developer with 5+ years building APIs with Python and FastAPI.",
      "rationale": "Direct title with primary keywords upfront"
    },
    {
      "title": "Senior Backend Developer | Python, FastAPI, PostgreSQL",
      "description": "Backend specialist experienced in Python, FastAPI, and PostgreSQL.",
      "rationale": "More detailed, targets senior roles"
    }
  ]
}"""


@pytest_asyncio.fixture
async def created_facet(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    payload = {
        "name": "Backend Developer",
        "slug": "backend-dev",
        "title": "Backend Developer Profile",
        "bio": "Specialized in Python and Go",
        "is_published": False,
    }
    resp = await client.post("/api/facets", json=payload, headers=_headers(token))
    assert resp.status_code == 201
    return resp.json(), _headers(token)


@pytest.mark.asyncio
async def test_get_seo_config_requires_auth(client: AsyncClient, created_facet):
    facet, _ = created_facet
    resp = await client.get(f"/api/facets/{facet['id']}/seo")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_seo_config_empty(client: AsyncClient, auth_tokens, created_facet):
    facet, headers = created_facet
    resp = await client.get(f"/api/facets/{facet['id']}/seo", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["meta_title"] is None
    assert data["meta_description"] is None


@pytest.mark.asyncio
async def test_update_seo(client: AsyncClient, auth_tokens, created_facet):
    facet, headers = created_facet
    payload = {"meta_title": "Test Title", "meta_description": "Test description for SEO"}
    resp = await client.put(f"/api/facets/{facet['id']}/seo", json=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "SEO metadata updated"


@pytest.mark.asyncio
async def test_update_seo_persists(client: AsyncClient, auth_tokens, created_facet):
    facet, headers = created_facet
    payload = {"meta_title": "Persisted Title", "meta_description": "Persisted desc"}
    await client.put(f"/api/facets/{facet['id']}/seo", json=payload, headers=headers)
    resp = await client.get(f"/api/facets/{facet['id']}/seo", headers=headers)
    assert resp.json()["meta_title"] == "Persisted Title"
    assert resp.json()["meta_description"] == "Persisted desc"


@pytest.mark.asyncio
async def test_suggest_seo_requires_auth(client: AsyncClient, created_facet):
    facet, _ = created_facet
    resp = await client.post(f"/api/facets/{facet['id']}/seo/suggest")
    assert resp.status_code == 401


@pytest.mark.asyncio
@patch("app.services.seo_service.AsyncOpenAI")
async def test_suggest_seo_full_flow(mock_openai, client: AsyncClient, auth_tokens, created_facet):
    facet, headers = created_facet

    mock_client = AsyncMock()
    mock_openai.return_value = mock_client

    responses = [_KEYWORDS_RESPONSE, _META_RESPONSE]

    async def mock_create(*args, **kwargs):
        content = responses.pop(0)
        completion = AsyncMock()
        completion.choices = [AsyncMock(message=AsyncMock(content=content))]
        return completion

    mock_client.chat = AsyncMock()
    mock_client.chat.completions = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=mock_create)

    resp = await client.post(
        f"/api/facets/{facet['id']}/seo/suggest",
        json={},
        headers=headers,
    )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["variants"]) == 2
    assert data["variants"][0]["title"] == "Backend Developer | Python & FastAPI"
    assert data["variants"][0]["rationale"] is not None


@pytest_asyncio.fixture
async def other_user_auth(client: AsyncClient):
    await client.post(
        "/auth/register", json={"email": "other@example.com", "password": "SecurePass123!"}
    )
    resp = await client.post(
        "/auth/login",
        json={"email": "other@example.com", "password": "SecurePass123!"},
    )
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def other_user_facet(client: AsyncClient, other_user_auth):
    token = other_user_auth
    payload = {
        "name": "Other Dev",
        "slug": "other-dev",
        "title": "Other Dev Profile",
        "bio": "Other bio",
        "is_published": False,
    }
    resp = await client.post("/api/facets", json=payload, headers=_headers(token))
    assert resp.status_code == 201
    return resp.json(), _headers(token)


@pytest.mark.asyncio
async def test_update_seo_403(created_facet, client: AsyncClient, other_user_auth):
    facet, _ = created_facet
    resp = await client.put(
        f"/api/facets/{facet['id']}/seo",
        json={"meta_title": "Hack", "meta_description": "Evil"},
        headers=_headers(other_user_auth),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_seo_403(created_facet, client: AsyncClient, other_user_auth):
    facet, _ = created_facet
    resp = await client.get(
        f"/api/facets/{facet['id']}/seo",
        headers=_headers(other_user_auth),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_suggest_seo_403(created_facet, client: AsyncClient, other_user_auth):
    facet, _ = created_facet
    resp = await client.post(
        f"/api/facets/{facet['id']}/seo/suggest",
        json={},
        headers=_headers(other_user_auth),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
@patch("app.services.seo_service.AsyncOpenAI")
async def test_suggest_seo_parse_error(
    mock_openai, client: AsyncClient, auth_tokens, created_facet
):
    facet, headers = created_facet

    mock_client = AsyncMock()
    mock_openai.return_value = mock_client

    async def mock_create(*args, **kwargs):
        completion = AsyncMock()
        completion.choices = [AsyncMock(message=AsyncMock(content="not valid json"))]
        return completion

    mock_client.chat = AsyncMock()
    mock_client.chat.completions = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=mock_create)

    resp = await client.post(
        f"/api/facets/{facet['id']}/seo/suggest",
        json={},
        headers=headers,
    )
    assert resp.status_code == 500


@pytest.mark.asyncio
async def test_suggest_seo_404(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    resp = await client.post(
        "/api/facets/00000000-0000-0000-0000-000000000000/seo/suggest",
        json={},
        headers=_headers(token),
    )
    assert resp.status_code == 404
