import io

import pytest
from httpx import AsyncClient
from PIL import Image


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


@pytest.mark.asyncio
async def test_upload_image_invalid_type(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    headers = _headers(access_token)

    resp = await client.post(
        "/api/upload",
        files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
        headers=headers,
    )
    assert resp.status_code in (400, 422)


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
