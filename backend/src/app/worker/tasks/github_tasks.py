from sqlalchemy import select

from app.db.session import async_session
from app.models.github_repo import GitHubRepo
from app.services.github_service import sync_repo_stats
from app.worker.celery_app import celery_app


@celery_app.task(name="sync_all_github_repos")
def sync_all_github_repos() -> dict:
    import asyncio

    async def _sync():
        async with async_session() as db:
            result = await db.execute(select(GitHubRepo))
            repos = list(result.scalars().all())
            synced = 0
            errors = 0
            for repo in repos:
                try:
                    await sync_repo_stats(db, repo.id)
                    synced += 1
                except Exception:
                    errors += 1
            return {"synced": synced, "errors": errors, "total": len(repos)}

    return asyncio.run(_sync())


@celery_app.task(name="sync_single_github_repo")
def sync_single_github_repo(repo_id: str) -> dict:
    import asyncio
    import uuid

    async def _sync():
        async with async_session() as db:
            await sync_repo_stats(db, uuid.UUID(repo_id))
            return {"status": "ok"}

    return asyncio.run(_sync())
