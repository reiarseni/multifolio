import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Theme


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


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
async def created_facet(client: AsyncClient, auth_tokens):
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


@pytest.mark.asyncio
async def test_list_facets(client: AsyncClient, auth_tokens, created_facet):
    _, headers = created_facet
    resp = await client.get("/api/facets", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Backend Developer"


@pytest.mark.asyncio
async def test_get_facet(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet
    resp = await client.get(f"/api/facets/{facet_data['id']}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == facet_data["id"]


@pytest.mark.asyncio
async def test_update_facet(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet
    resp = await client.put(
        f"/api/facets/{facet_data['id']}",
        json={"name": "Senior Backend Developer", "is_published": True},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Senior Backend Developer"
    assert data["is_published"] is True


@pytest.mark.asyncio
async def test_delete_facet(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet
    resp = await client.delete(f"/api/facets/{facet_data['id']}", headers=headers)
    assert resp.status_code == 204

    resp = await client.get(f"/api/facets/{facet_data['id']}", headers=headers)
    assert resp.status_code == 404


# ── GET /api/themes ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_themes_includes_predefined(
    client: AsyncClient, auth_tokens, seeded_themes
):
    token, _ = auth_tokens
    resp = await client.get("/api/themes", headers=_headers(token))
    assert resp.status_code == 200
    names = {t["name"] for t in resp.json()}
    assert {"minimal", "formal", "bold"} <= names


@pytest.mark.asyncio
async def test_list_themes_requires_auth(client: AsyncClient, seeded_themes):
    resp = await client.get("/api/themes")
    assert resp.status_code == 401


# ── PUT /api/facets/{id}/theme ────────────────────────────────────────────────

@pytest_asyncio.fixture
async def facet_with_theme(client: AsyncClient, auth_tokens, seeded_themes):
    token, _ = auth_tokens
    h = _headers(token)
    resp = await client.post(
        "/api/facets", json={"name": "TFacet", "slug": "tfacet"}, headers=h
    )
    assert resp.status_code == 201
    return resp.json(), h, seeded_themes


@pytest.mark.asyncio
async def test_update_facet_theme(client: AsyncClient, facet_with_theme):
    facet, h, themes = facet_with_theme
    formal_id = str(themes[1].id)
    resp = await client.put(
        f"/api/facets/{facet['id']}/theme",
        json={"theme_id": formal_id, "web_layout": "sidebar", "pdf_layout": "two-column"},
        headers=h,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["theme_id"] == formal_id
    assert data["web_layout"] == "sidebar"
    assert data["pdf_layout"] == "two-column"


@pytest.mark.asyncio
async def test_update_facet_theme_invalid_layout(client: AsyncClient, facet_with_theme):
    facet, h, _ = facet_with_theme
    resp = await client.put(
        f"/api/facets/{facet['id']}/theme",
        json={"web_layout": "invalid-layout"},
        headers=h,
    )
    assert resp.status_code == 422


# ── Transversal skills pre-selection ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_transversal_skills_pre_included(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    h = _headers(token)

    await client.get("/api/profile", headers=h)
    skill_resp = await client.post(
        "/api/profile/skills",
        json={"name": "Python", "is_transversal": True},
        headers=h,
    )
    assert skill_resp.status_code == 200
    skill_id = skill_resp.json()["id"]

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Trans Facet", "slug": "trans-facet"},
        headers=h,
    )
    assert facet_resp.status_code == 201
    assert skill_id in facet_resp.json()["skill_ids"]


@pytest.mark.asyncio
async def test_transversal_can_be_excluded_on_update(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    h = _headers(token)

    await client.get("/api/profile", headers=h)
    skill_resp = await client.post(
        "/api/profile/skills",
        json={"name": "Go", "is_transversal": True},
        headers=h,
    )
    skill_id = skill_resp.json()["id"]

    facet_resp = await client.post(
        "/api/facets",
        json={"name": "Facet X", "slug": "facet-x"},
        headers=h,
    )
    facet = facet_resp.json()
    assert skill_id in facet["skill_ids"]

    update_resp = await client.put(
        f"/api/facets/{facet['id']}",
        json={"skill_ids": []},
        headers=h,
    )
    assert update_resp.status_code == 200
    assert skill_id not in update_resp.json()["skill_ids"]
