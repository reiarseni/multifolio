from __future__ import annotations

from unittest.mock import patch

import pytest
from httpx import AsyncClient


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


@pytest.mark.asyncio
async def test_suggest_improvements(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    assert facet_resp.status_code == 201
    facet_id = facet_resp.json()["id"]

    section_resp = await client.post(
        f"/api/facets/{facet_id}/story/sections",
        json={
            "section_type": "proceso",
            "title": "Mi Proyecto",
            "content": "Hice un proyecto",
        },
        headers=headers,
    )
    assert section_resp.status_code == 201
    section_id = section_resp.json()["id"]

    with patch("app.services.ai_story_service.llm_improve_content") as mock_improve:
        mock_improve.return_value = "Lideré un proyecto que mejoró la eficiencia en un 40%"
        resp = await client.post(f"/api/ai/story/sections/{section_id}/improve", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["original"] == "Hice un proyecto"
        assert "40%" in data["suggested"]


@pytest.mark.asyncio
async def test_expand_narrative(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    assert facet_resp.status_code == 201
    facet_id = facet_resp.json()["id"]

    section_resp = await client.post(
        f"/api/facets/{facet_id}/story/sections",
        json={
            "section_type": "impact",
            "title": "Impacto",
            "content": "Tuve impacto",
        },
        headers=headers,
    )
    assert section_resp.status_code == 201
    section_id = section_resp.json()["id"]

    with patch("app.services.ai_story_service.llm_expand_section") as mock_expand:
        mock_expand.return_value = "El proyecto tuvo un impacto significativo en la organización"
        resp = await client.post(f"/api/ai/story/sections/{section_id}/expand", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["original"] == "Tuve impacto"
        assert "significativo" in data["suggested"]


@pytest.mark.asyncio
async def test_suggest_headline(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet", "title": "Dev"},
        headers=headers,
    )
    assert facet_resp.status_code == 201
    facet_id = facet_resp.json()["id"]

    with patch("app.services.ai_story_service.llm_suggest_headline") as mock_headline:
        mock_headline.return_value = {
            "title": "Senior Software Engineer",
            "bio": "10+ años construyendo apps escalables",
        }
        resp = await client.post(
            f"/api/ai/facets/{facet_id}/suggest-headline",
            json={"target_role": "Senior Backend Developer"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Senior Software Engineer"
        assert "escalables" in data["bio"]


@pytest.mark.asyncio
async def test_apply_suggestion(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    assert facet_resp.status_code == 201
    facet_id = facet_resp.json()["id"]

    section_resp = await client.post(
        f"/api/facets/{facet_id}/story/sections",
        json={
            "section_type": "proceso",
            "title": "Test",
            "content": "Original content",
        },
        headers=headers,
    )
    assert section_resp.status_code == 201
    section_id = section_resp.json()["id"]

    with patch("app.services.ai_story_service.llm_apply_suggestion") as mock_apply:
        mock_apply.return_value = "Improved content with metrics"
        resp = await client.post(
            "/api/ai/apply-suggestion",
            json={"section_id": section_id, "suggestion": "Make it better"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["content"] == "Improved content with metrics"


@pytest.mark.asyncio
async def test_suggest_improvements_empty_content(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    assert facet_resp.status_code == 201
    facet_id = facet_resp.json()["id"]

    section_resp = await client.post(
        f"/api/facets/{facet_id}/story/sections",
        json={
            "section_type": "proceso",
            "title": "Empty",
            "content": "",
        },
        headers=headers,
    )
    assert section_resp.status_code == 201
    section_id = section_resp.json()["id"]

    resp = await client.post(f"/api/ai/story/sections/{section_id}/improve", headers=headers)
    assert resp.status_code == 400
    assert "no content" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_expand_narrative_empty_content(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": "test-facet"},
        headers=headers,
    )
    assert facet_resp.status_code == 201
    facet_id = facet_resp.json()["id"]

    section_resp = await client.post(
        f"/api/facets/{facet_id}/story/sections",
        json={
            "section_type": "proceso",
            "title": "Empty",
            "content": "   ",
        },
        headers=headers,
    )
    assert section_resp.status_code == 201
    section_id = section_resp.json()["id"]

    resp = await client.post(f"/api/ai/story/sections/{section_id}/expand", headers=headers)
    assert resp.status_code == 400
    assert "no content" in resp.json()["detail"]
