import redis.asyncio as aioredis
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> JSONResponse:
    settings = get_settings()
    db_status = "ok"
    redis_status = "ok"

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    try:
        r = aioredis.from_url(settings.redis_url)
        await r.ping()
        await r.aclose()
    except Exception:
        redis_status = "error"

    all_ok = db_status == "ok" and redis_status == "ok"
    body = {
        "status": "ok" if all_ok else "degraded",
        "database": db_status,
        "redis": redis_status,
    }
    return JSONResponse(content=body, status_code=200 if all_ok else 503)
