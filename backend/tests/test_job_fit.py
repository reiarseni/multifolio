from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


_ENTITIES_RESPONSE = """{
  "title": "Senior Backend Engineer",
  "company": "TechCorp",
  "required_skills": ["Python", "SQL", "API Design"],
  "required_experience_years": 5,
  "tech_stack": ["FastAPI", "PostgreSQL", "Redis"],
  "preferred_skills": ["Docker", "AWS"],
  "responsibilities": ["Build APIs", "Design databases"]
}"""

_COMPARISON_RESPONSE = """{
  "overall_score": 75,
  "skills_score": 80,
  "experience_score": 70,
  "stack_score": 85,
  "tone_score": 65,
  "gaps": [
    {
      "category": "experience",
      "description": "Falta experiencia en dise\u00f1o de sistemas a gran escala",
      "severity": "medium",
      "suggestion": "Agregar proyectos que demuestren trabajo con sistemas distribuidos"
    }
  ],
  "suggestions": ["Destacar experiencia con FastAPI y PostgreSQL"]
}"""

_REORDER_RESPONSE = """{
  "rationale": "Poner skills y stack primero porque son el match m\u00e1s fuerte",
  "proposed_order": ["skills", "stack", "experience", "education", "projects"]
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
async def test_analyze_job_fit_requires_auth(client: AsyncClient, created_facet):
    facet, _ = created_facet
    resp = await client.post(
        f"/api/facets/{facet['id']}/job-fit",
        json={"job_posting": "We are looking for a Senior Backend Engineer..."},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_analyze_job_fit_returns_404_for_nonexistent_facet(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    resp = await client.post(
        "/api/facets/00000000-0000-0000-0000-000000000000/job-fit",
        json={"job_posting": "Test job posting"},
        headers=_headers(token),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_analyze_job_fit_rejects_long_posting(
    client: AsyncClient, auth_tokens, created_facet
):
    facet, headers = created_facet
    long_text = "x" * 10001
    resp = await client.post(
        f"/api/facets/{facet['id']}/job-fit",
        json={"job_posting": long_text},
        headers=headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
@patch("app.services.job_fit_service.AsyncOpenAI")
async def test_analyze_job_fit_full_flow(
    mock_openai, client: AsyncClient, auth_tokens, created_facet
):
    facet, headers = created_facet

    mock_client = AsyncMock()
    mock_openai.return_value = mock_client

    responses = [
        _ENTITIES_RESPONSE,
        _COMPARISON_RESPONSE,
        _REORDER_RESPONSE,
    ]

    async def mock_create(*args, **kwargs):
        content = responses.pop(0)
        completion = AsyncMock()
        completion.choices = [AsyncMock(message=AsyncMock(content=content))]
        return completion

    mock_client.chat = AsyncMock()
    mock_client.chat.completions = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=mock_create)

    resp = await client.post(
        f"/api/facets/{facet['id']}/job-fit",
        json={
            "job_posting": "We are looking for a Senior Backend Engineer "
            "with 5+ years of experience in Python, FastAPI, and PostgreSQL."
        },
        headers=headers,
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_score"] == 75
    assert data["skills_score"] == 80
    assert data["experience_score"] == 70
    assert data["stack_score"] == 85
    assert data["tone_score"] == 65
    assert len(data["gaps"]) == 1
    assert data["gaps"][0]["category"] == "experience"
    assert len(data["suggestions"]) == 1
    assert data["reorder_suggestion"] is not None
    assert data["reorder_suggestion"]["rationale"] is not None


@pytest.mark.asyncio
async def test_get_job_fit_history_empty(client: AsyncClient, auth_tokens, created_facet):
    facet, headers = created_facet
    resp = await client.get(
        f"/api/facets/{facet['id']}/job-fit/history",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["analyses"] == []
