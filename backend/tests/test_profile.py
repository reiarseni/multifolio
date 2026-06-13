import pytest
from httpx import AsyncClient


# ── helpers ─────────────────────────────────────────────────────────────────

def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


# ── GET /api/profile ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_profile_auto_creates(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    resp = await client.get("/api/profile", headers=_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "user@example.com"
    assert data["full_name"] == ""
    assert data["experiences"] == []
    assert data["educations"] == []
    assert data["skills"] == []
    assert data["certifications"] == []


@pytest.mark.asyncio
async def test_get_profile_idempotent(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    h = _headers(token)
    r1 = await client.get("/api/profile", headers=h)
    r2 = await client.get("/api/profile", headers=h)
    assert r1.json()["id"] == r2.json()["id"]


@pytest.mark.asyncio
async def test_get_profile_requires_auth(client: AsyncClient):
    resp = await client.get("/api/profile")
    assert resp.status_code == 401


# ── PUT /api/profile ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    h = _headers(token)
    resp = await client.put(
        "/api/profile",
        json={"full_name": "Jane Doe", "title": "Software Engineer", "location": "Madrid"},
        headers=h,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Jane Doe"
    assert data["title"] == "Software Engineer"
    assert data["location"] == "Madrid"

    # Verify persisted
    get_resp = await client.get("/api/profile", headers=h)
    assert get_resp.json()["full_name"] == "Jane Doe"


# ── Experiences ──────────────────────────────────────────────────────────────

_EXP = {
    "company": "Acme Corp",
    "position": "Backend Engineer",
    "start_date": "2020-01-01",
    "is_current": True,
}


@pytest.mark.asyncio
async def test_add_experience(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    h = _headers(token)
    resp = await client.post("/api/profile/experiences", json=_EXP, headers=h)
    assert resp.status_code == 200
    data = resp.json()
    assert data["company"] == "Acme Corp"
    assert data["position"] == "Backend Engineer"
    assert "id" in data


@pytest.mark.asyncio
async def test_delete_experience(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    h = _headers(token)
    exp = (await client.post("/api/profile/experiences", json=_EXP, headers=h)).json()
    resp = await client.delete(f"/api/profile/experiences/{exp['id']}", headers=h)
    assert resp.status_code == 204

    profile = (await client.get("/api/profile", headers=h)).json()
    assert all(e["id"] != exp["id"] for e in profile["experiences"])


# ── Education ────────────────────────────────────────────────────────────────

_EDU = {
    "institution": "MIT",
    "degree": "B.Sc. Computer Science",
    "start_date": "2015-09-01",
    "end_date": "2019-06-30",
    "is_current": False,
}


@pytest.mark.asyncio
async def test_add_education(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    resp = await client.post("/api/profile/education", json=_EDU, headers=_headers(token))
    assert resp.status_code == 200
    assert resp.json()["institution"] == "MIT"


@pytest.mark.asyncio
async def test_delete_education(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    h = _headers(token)
    edu = (await client.post("/api/profile/education", json=_EDU, headers=h)).json()
    resp = await client.delete(f"/api/profile/education/{edu['id']}", headers=h)
    assert resp.status_code == 204


# ── Skills ───────────────────────────────────────────────────────────────────

_SKILL = {"name": "Python", "level": "expert", "is_transversal": True}


@pytest.mark.asyncio
async def test_add_skill(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    resp = await client.post("/api/profile/skills", json=_SKILL, headers=_headers(token))
    assert resp.status_code == 200
    assert resp.json()["name"] == "Python"


@pytest.mark.asyncio
async def test_delete_skill(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    h = _headers(token)
    skill = (await client.post("/api/profile/skills", json=_SKILL, headers=h)).json()
    resp = await client.delete(f"/api/profile/skills/{skill['id']}", headers=h)
    assert resp.status_code == 204


# ── Certifications ───────────────────────────────────────────────────────────

_CERT = {"name": "AWS Solutions Architect", "issuer": "Amazon", "issue_date": "2023-03-15"}


@pytest.mark.asyncio
async def test_add_certification(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    resp = await client.post("/api/profile/certifications", json=_CERT, headers=_headers(token))
    assert resp.status_code == 200
    assert resp.json()["name"] == "AWS Solutions Architect"


@pytest.mark.asyncio
async def test_delete_certification(client: AsyncClient, auth_tokens):
    token, _ = auth_tokens
    h = _headers(token)
    cert = (await client.post("/api/profile/certifications", json=_CERT, headers=h)).json()
    resp = await client.delete(f"/api/profile/certifications/{cert['id']}", headers=h)
    assert resp.status_code == 204
