import io
import uuid
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import AsyncClient
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Theme
from app.services.media_service import delete_media, validate_video_embed


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
    headers = _headers(access_token)
    payload = {
        "name": "Test Facet Coverage",
        "slug": f"test-facet-cov-{uuid.uuid4().hex[:8]}",
        "title": "Test",
        "bio": "Test bio",
        "is_published": False,
    }
    resp = await client.post("/api/facets", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json(), headers


@pytest.mark.asyncio
async def test_profile_get(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    resp = await client.get("/api/profile", headers=headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_open_to_role_upsert_and_get(client: AsyncClient, auth_tokens, created_facet):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    facet_data, _ = created_facet

    payload = {"status": "available", "role_type": "backend", "modality": "remote"}
    resp = await client.put(
        f"/api/facets/{facet_data['id']}/open-to-role",
        json=payload,
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "available"
    assert data["role_type"] == "backend"

    resp = await client.get(f"/api/facets/{facet_data['id']}/open-to-role", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "available"


@pytest.mark.asyncio
async def test_open_to_role_delete(client: AsyncClient, auth_tokens, created_facet):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    facet_data, _ = created_facet

    await client.put(
        f"/api/facets/{facet_data['id']}/open-to-role",
        json={"status": "available"},
        headers=headers,
    )

    resp = await client.delete(f"/api/facets/{facet_data['id']}/open-to-role", headers=headers)
    assert resp.status_code == 204

    resp = await client.get(f"/api/facets/{facet_data['id']}/open-to-role", headers=headers)
    assert resp.status_code == 200
    assert resp.json() is None


@pytest.mark.asyncio
async def test_theme_not_found_returns_404(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/api/themes/{fake_id}", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_upload_image_large_file(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    large_content = b"x" * (11 * 1024 * 1024)
    resp = await client.post(
        "/api/upload",
        files={"file": ("large.png", io.BytesIO(large_content), "image/png")},
        headers=headers,
    )
    assert resp.status_code in (400, 413)


@pytest.mark.asyncio
async def test_upload_image_rgba_conversion(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    resp = await client.post(
        "/api/upload",
        files={"file": ("rgba.png", buf, "image/png")},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["url"].startswith("/media/")


@pytest.mark.asyncio
async def test_upload_image_palette_mode(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    img = Image.new("P", (100, 100))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    resp = await client.post(
        "/api/upload",
        files={"file": ("palette.png", buf, "image/png")},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["url"].startswith("/media/")


@pytest.mark.asyncio
async def test_upload_image_thumbnail(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    img = Image.new("RGB", (3000, 2000), color="green")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    resp = await client.post(
        "/api/upload",
        files={"file": ("large.png", buf, "image/png")},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["url"].startswith("/media/")


@pytest.mark.asyncio
async def test_story_section_media_upload(client: AsyncClient, auth_tokens, created_facet):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    facet_data, _ = created_facet

    create_resp = await client.post(
        f"/api/facets/{facet_data['id']}/story/sections",
        json={"section_type": "context", "title": "Media Test", "order": 0},
        headers=headers,
    )
    section_id = create_resp.json()["id"]

    img = Image.new("RGB", (100, 100), color="yellow")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    resp = await client.post(
        f"/api/story/sections/{section_id}/media",
        files={"file": ("test.png", buf, "image/png")},
        headers=headers,
    )
    assert resp.status_code == 200
    assert "url" in resp.json()


@pytest.mark.asyncio
async def test_story_update_section(client: AsyncClient, auth_tokens, created_facet):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    facet_data, _ = created_facet

    create_resp = await client.post(
        f"/api/facets/{facet_data['id']}/story/sections",
        json={"section_type": "context", "title": "Original", "order": 0},
        headers=headers,
    )
    section_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/story/sections/{section_id}",
        json={"title": "Updated", "content": "New content"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated"
    assert data["content"] == "New content"


@pytest.mark.asyncio
async def test_story_reorder(client: AsyncClient, auth_tokens, created_facet):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    facet_data, _ = created_facet

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
async def test_story_delete_section(client: AsyncClient, auth_tokens, created_facet):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    facet_data, _ = created_facet

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
async def test_facet_create_and_list(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    resp = await client.post(
        "/api/facets",
        json={"name": "Test Facet", "slug": f"test-{uuid.uuid4().hex[:8]}"},
        headers=headers,
    )
    assert resp.status_code == 201

    resp = await client.get("/api/facets", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_facet_update(client: AsyncClient, auth_tokens, created_facet):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    facet_data, _ = created_facet

    resp = await client.put(
        f"/api/facets/{facet_data['id']}",
        json={"name": "Updated Facet", "bio": "Updated bio"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Facet"


@pytest.mark.asyncio
async def test_facet_delete(client: AsyncClient, auth_tokens, created_facet):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    facet_data, _ = created_facet

    resp = await client.delete(f"/api/facets/{facet_data['id']}", headers=headers)
    assert resp.status_code == 204

    resp = await client.get(f"/api/facets/{facet_data['id']}", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_project_create_and_list(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    resp = await client.post(
        "/api/projects",
        json={
            "title": "Test Project",
            "description": "A test project",
            "tech_stack": ["Python", "FastAPI"],
        },
        headers=headers,
    )
    assert resp.status_code == 201

    resp = await client.get("/api/projects", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_project_update(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    create_resp = await client.post(
        "/api/projects",
        json={"title": "Original", "description": "Original desc"},
        headers=headers,
    )
    project_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/projects/{project_id}",
        json={"title": "Updated Project", "description": "Updated desc"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Project"


@pytest.mark.asyncio
async def test_project_delete(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    create_resp = await client.post(
        "/api/projects",
        json={"title": "To Delete", "description": "Delete me"},
        headers=headers,
    )
    project_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/projects/{project_id}", headers=headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_facet_theme_invalid_layout(
    client: AsyncClient, auth_tokens, seeded_themes, created_facet
):
    access_token, _ = auth_tokens
    headers = _headers(access_token)
    facet_data, _ = created_facet
    theme = seeded_themes[0]

    await client.put(
        f"/api/facets/{facet_data['id']}/theme",
        json={"theme_id": str(theme.id)},
        headers=headers,
    )

    resp = await client.put(
        f"/api/facets/{facet_data['id']}/theme",
        json={"web_layout": "invalid-layout"},
        headers=headers,
    )
    assert resp.status_code == 422


def test_validate_video_embed_youtube():
    url = "https://www.youtube.com/watch?v=abc123"
    assert validate_video_embed(url) == url


def test_validate_video_embed_youtu_be():
    url = "https://youtu.be/abc123"
    assert validate_video_embed(url) == url


def test_validate_video_embed_vimeo():
    url = "https://vimeo.com/123456"
    assert validate_video_embed(url) == url


def test_validate_video_embed_vimeo_www():
    url = "https://www.vimeo.com/123456"
    assert validate_video_embed(url) == url


def test_validate_video_embed_invalid():
    with pytest.raises(Exception) as exc_info:
        validate_video_embed("https://example.com/video.mp4")
    assert exc_info.value.status_code == 400


def test_delete_media_existing_file(tmp_path):
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    test_file = media_dir / "test.webp"
    test_file.write_bytes(b"fake image data")

    with patch("app.services.media_service.settings") as mock_settings:
        mock_settings.media_dir = str(media_dir)
        delete_media("/media/test.webp")

    assert not test_file.exists()


def test_delete_media_nonexistent_file(tmp_path):
    media_dir = tmp_path / "media"
    media_dir.mkdir()

    with patch("app.services.media_service.settings") as mock_settings:
        mock_settings.media_dir = str(media_dir)
        delete_media("/media/nonexistent.webp")


def test_delete_media_non_media_url():
    delete_media("https://example.com/image.jpg")


@pytest.mark.asyncio
async def test_get_profile_or_404_not_found(client: AsyncClient, auth_tokens, db_session):
    from fastapi import HTTPException

    from app.services.utils import get_profile_or_404

    user_id = uuid.uuid4()
    with pytest.raises(HTTPException) as exc_info:
        await get_profile_or_404(db_session, user_id)
    assert exc_info.value.status_code == 404
