from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.github_import import (
    ImportAnalyzeRequest,
    ImportAnalyzeResponse,
    ImportConfirmRequest,
    ImportConfirmResponse,
)
from app.services import github_import_service

router = APIRouter(prefix="/github/import", tags=["github-import"])


@router.post("/analyze", response_model=ImportAnalyzeResponse)
async def analyze_import(
    body: ImportAnalyzeRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    projects = await github_import_service.analyze_repos(
        db=db,
        user_id=current_user.id,
        repo_ids=body.repo_ids,
        facet_id=body.facet_id,
    )
    return ImportAnalyzeResponse(projects=projects)


@router.post("/confirm", response_model=ImportConfirmResponse)
async def confirm_import(
    body: ImportConfirmRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await github_import_service.confirm_import(
        db=db,
        user_id=current_user.id,
        facet_id=body.facet_id,
        projects=body.projects,
    )
