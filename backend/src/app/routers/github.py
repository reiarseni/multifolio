import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.github_repo import GitHubRepo
from app.models.user import User
from app.schemas.github import GitHubRepoCreate, GitHubRepoResponse
from app.services import github_service

router = APIRouter(prefix="/github", tags=["github"])


@router.get("/repos", response_model=list[GitHubRepoResponse])
async def list_repos(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(GitHubRepo)
        .where(GitHubRepo.user_id == current_user.id)
        .order_by(GitHubRepo.created_at)
    )
    return list(result.scalars().all())


@router.post("/repos", response_model=GitHubRepoResponse, status_code=201)
async def link_repo(
    body: GitHubRepoCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await github_service.link_repo(db, current_user.id, body.repo_url)


@router.post("/repos/sync", response_model=list[GitHubRepoResponse])
async def sync_repos(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(GitHubRepo).where(GitHubRepo.user_id == current_user.id))
    repos = list(result.scalars().all())
    synced = []
    for repo in repos:
        try:
            updated = await github_service.sync_repo_stats(db, repo.id)
            synced.append(updated)
        except Exception:
            synced.append(repo)
    return synced


@router.delete("/repos/{repo_id}", status_code=204)
async def unlink_repo(
    repo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await github_service.unlink_repo(db, current_user.id, repo_id)
