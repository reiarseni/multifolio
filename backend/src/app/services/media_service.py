import io
import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from PIL import Image

from app.core.config import get_settings

settings = get_settings()

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_WIDTH = 1920
MAX_HEIGHT = 1080


def _get_media_dir() -> Path:
    media_dir = Path(settings.media_dir)
    media_dir.mkdir(parents=True, exist_ok=True)
    return media_dir


async def upload_image(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}",
        )

    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image too large. Maximum size is 10MB",
        )

    img = Image.open(io.BytesIO(contents))

    if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
        img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    buffer = io.BytesIO()
    img.save(buffer, format="WEBP", quality=85)
    buffer.seek(0)

    filename = f"{uuid.uuid4().hex}.webp"
    media_dir = _get_media_dir() / "images"
    media_dir.mkdir(parents=True, exist_ok=True)
    filepath = media_dir / filename

    with open(filepath, "wb") as f:
        f.write(buffer.getvalue())

    return f"/media/images/{filename}"


def validate_video_embed(url: str) -> str:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    allowed_domains = {
        "youtube.com",
        "www.youtube.com",
        "youtu.be",
        "vimeo.com",
        "www.vimeo.com",
    }

    if parsed.hostname not in allowed_domains:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid video embed URL. Only YouTube and Vimeo are supported.",
        )

    return url


def delete_media(url: str) -> None:
    if url.startswith("/media/"):
        media_path = Path(settings.media_dir) / url.removeprefix("/media/")
        if media_path.exists():
            os.remove(media_path)
