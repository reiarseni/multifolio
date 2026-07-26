import pytest
import pytest_asyncio
from httpx import AsyncClient


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def created_facet(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    payload = {
        "name": "Backend Developer",
        "slug": "backend-dev-story",
        "title": "Backend Developer Profile",
        "bio": "Specialized in Python and Go",
        "is_published": False,
    }
    resp = await client.post("/api/facets", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json(), headers


@pytest.mark.asyncio
async def test_create_section(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet
    payload = {
        "section_type": "context",
        "title": "Contexto del Proyecto",
        "content": "El problema que resolvimos era...",
        "order": 0,
        "is_visible": True,
    }
    resp = await client.post(
        f"/api/facets/{facet_data['id']}/story/sections",
        json=payload,
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["section_type"] == "context"
    assert data["title"] == "Contexto del Proyecto"
    assert data["facet_id"] == facet_data["id"]


@pytest.mark.asyncio
async def test_get_story(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet

    await client.post(
        f"/api/facets/{facet_data['id']}/story/sections",
        json={"section_type": "context", "title": "Section 1", "order": 0},
        headers=headers,
    )
    await client.post(
        f"/api/facets/{facet_data['id']}/story/sections",
        json={"section_type": "process", "title": "Section 2", "order": 1},
        headers=headers,
    )

    resp = await client.get(f"/api/facets/{facet_data['id']}/story", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["title"] == "Section 1"
    assert data[1]["title"] == "Section 2"


@pytest.mark.asyncio
async def test_update_section(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet

    create_resp = await client.post(
        f"/api/facets/{facet_data['id']}/story/sections",
        json={"section_type": "context", "title": "Original", "order": 0},
        headers=headers,
    )
    section_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/story/sections/{section_id}",
        json={"title": "Actualizado", "content": "Nuevo contenido"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Actualizado"
    assert data["content"] == "Nuevo contenido"


@pytest.mark.asyncio
async def test_reorder_sections(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet

    resp1 = await client.post(
        f"/api/facets/{facet_data['id']}/story/sections",
        json={"section_type": "context", "title": "A", "order": 0},
        headers=headers,
    )
    resp2 = await client.post(
        f"/api/facets/{facet_data['id']}/story/sections",
        json={"section_type": "process", "title": "B", "order": 1},
        headers=headers,
    )

    id_a = resp1.json()["id"]
    id_b = resp2.json()["id"]

    resp = await client.put(
        f"/api/facets/{facet_data['id']}/story/reorder",
        json={"section_ids": [id_b, id_a]},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["id"] == id_b
    assert data[1]["id"] == id_a


@pytest.mark.asyncio
async def test_delete_section(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet

    create_resp = await client.post(
        f"/api/facets/{facet_data['id']}/story/sections",
        json={"section_type": "context", "title": "To Delete", "order": 0},
        headers=headers,
    )
    section_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/story/sections/{section_id}", headers=headers)
    assert resp.status_code == 204

    get_resp = await client.get(f"/api/facets/{facet_data['id']}/story", headers=headers)
    assert len(get_resp.json()) == 0


@pytest.mark.asyncio
async def test_create_section_invalid_facet(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    resp = await client.post(
        "/api/facets/00000000-0000-0000-0000-000000000000/story/sections",
        json={"section_type": "context", "title": "X", "order": 0},
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_story_empty(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet
    resp = await client.get(f"/api/facets/{facet_data['id']}/story", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_upload_media(client: AsyncClient, auth_tokens, created_facet):
    import io

    from PIL import Image

    facet_data, headers = created_facet

    create_resp = await client.post(
        f"/api/facets/{facet_data['id']}/story/sections",
        json={"section_type": "context", "title": "With Media", "order": 0},
        headers=headers,
    )
    section_id = create_resp.json()["id"]

    img = Image.new("RGB", (100, 100), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    resp = await client.post(
        f"/api/story/sections/{section_id}/media",
        files={"file": ("test.png", buf, "image/png")},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "url" in data
    assert data["url"].startswith("/media/images/")


@pytest.mark.asyncio
async def test_upload_media_invalid_type(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet

    create_resp = await client.post(
        f"/api/facets/{facet_data['id']}/story/sections",
        json={"section_type": "context", "title": "Bad Upload", "order": 0},
        headers=headers,
    )
    section_id = create_resp.json()["id"]

    resp = await client.post(
        f"/api/story/sections/{section_id}/media",
        files={"file": ("test.txt", b"hello", "text/plain")},
        headers=headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_section_not_found(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    resp = await client.patch(
        "/api/story/sections/00000000-0000-0000-0000-000000000000",
        json={"title": "X"},
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_section_not_found(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    resp = await client.delete(
        "/api/story/sections/00000000-0000-0000-0000-000000000000",
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_reorder_partial_ids(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet

    resp1 = await client.post(
        f"/api/facets/{facet_data['id']}/story/sections",
        json={"section_type": "context", "title": "A", "order": 0},
        headers=headers,
    )
    await client.post(
        f"/api/facets/{facet_data['id']}/story/sections",
        json={"section_type": "process", "title": "B", "order": 1},
        headers=headers,
    )

    id_a = resp1.json()["id"]

    resp = await client.put(
        f"/api/facets/{facet_data['id']}/story/reorder",
        json={"section_ids": [id_a]},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["id"] == id_a


@pytest.mark.asyncio
async def test_section_types(client: AsyncClient, auth_tokens, created_facet):
    facet_data, headers = created_facet
    section_types = ["context", "process", "solution", "impact"]

    for stype in section_types:
        resp = await client.post(
            f"/api/facets/{facet_data['id']}/story/sections",
            json={"section_type": stype, "title": f"Section {stype}", "order": 0},
            headers=headers,
        )
        assert resp.status_code == 201
        assert resp.json()["section_type"] == stype
