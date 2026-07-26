import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "application/pdf",
}

_MAGIC_BYTES: dict[str, list[bytes]] = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],
    "image/gif": [b"GIF87a", b"GIF89a"],
    "application/pdf": [b"%PDF"],
}

_EXT_MAP = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
    "application/pdf": "pdf",
}


def _verify_magic_bytes(data: bytes, content_type: str) -> bool:
    prefixes = _MAGIC_BYTES.get(content_type)
    if not prefixes:
        return False
    return any(data.startswith(prefix) for prefix in prefixes)


async def save_upload_file(file: UploadFile) -> str:
    settings = get_settings()

    content_type = file.content_type or ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Tipo de archivo no permitido. Tipos aceptados: "
                f"{', '.join(sorted(ALLOWED_CONTENT_TYPES))}"
            ),
        )

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    data = await file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el límite de {settings.max_upload_size_mb} MB",
        )

    if not _verify_magic_bytes(data, content_type):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo no coincide con el tipo de contenido declarado",
        )

    ext = _EXT_MAP[content_type]
    filename = f"{uuid.uuid4()}.{ext}"

    uploads_dir = Path(settings.media_dir) / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    dest = uploads_dir / filename
    dest.write_bytes(data)

    return f"/media/uploads/{filename}"
