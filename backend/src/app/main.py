from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.routers import (
    analytics,
    auth,
    facets,
    github,
    health,
    notifications,
    open_to_role,
    profile,
    projects,
    public,
    upload,
)
from app.routers import themes as themes_router

settings = get_settings()
Path(settings.media_dir).mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Multifolio API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(profile.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(facets.router, prefix="/api")
app.include_router(github.router, prefix="/api")
app.include_router(open_to_role.router, prefix="/api")
app.include_router(themes_router.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(public.router)

app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")
