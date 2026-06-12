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

_EXT_MAP = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
    "application/pdf": "pdf",
}


async def save_upload_file(file: UploadFile) -> str:
    settings = get_settings()

    content_type = file.content_type or ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        allowed = ", ".join(sorted(ALLOWED_CONTENT_TYPES))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Tipo de archivo no permitido. Tipos aceptados: {allowed}",
        )

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    data = await file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el límite de {settings.max_upload_size_mb} MB",
        )

    ext = _EXT_MAP[content_type]
    filename = f"{uuid.uuid4()}.{ext}"

    uploads_dir = Path(settings.media_dir) / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    dest = uploads_dir / filename
    dest.write_bytes(data)

    return f"/media/uploads/{filename}"
