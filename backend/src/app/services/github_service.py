import re
from datetime import UTC, datetime

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.github_repo import GitHubRepo

GITHUB_API_BASE = "https://api.github.com"


def _parse_repo_url(url: str) -> tuple[str, str]:
    patterns = [
        r"github\.com/([^/]+)/([^/]+?)(?:\.git)?$",
        r"github\.com/([^/]+)/([^/]+)/?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url.rstrip("/"))
        if match:
            return match.group(1), match.group(2)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid GitHub URL. Format: https://github.com/owner/repo",
    )


async def get_public_repo_stats(owner: str, repo: str) -> dict:
    async with httpx.AsyncClient() as client:
        repo_resp = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}")
        if repo_resp.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository {owner}/{repo} not found or is private",
            )
        repo_resp.raise_for_status()
        repo_data = repo_resp.json()

        langs_resp = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages")
        languages = {}
        if langs_resp.status_code == 200:
            lang_bytes = langs_resp.json()
            total = sum(lang_bytes.values()) or 1
            languages = {
                lang: round(bytes_count / total * 100, 1)
                for lang, bytes_count in lang_bytes.items()
            }

        return {
            "name": repo_data["name"],
            "full_name": repo_data["full_name"],
            "description": repo_data.get("description"),
            "stars": repo_data["stargazers_count"],
            "forks": repo_data["forks_count"],
            "language": repo_data.get("language"),
            "languages": languages,
            "last_commit": repo_data["pushed_at"],
            "is_archived": repo_data.get("archived", False),
        }


async def get_user_repos(token: str | None = None) -> list[dict]:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    repos = []
    page = 1
    async with httpx.AsyncClient() as client:
        while page <= 2:
            resp = await client.get(
                f"{GITHUB_API_BASE}/user/repos",
                headers=headers,
                params={"per_page": 100, "page": page, "sort": "pushed"},
            )
            resp.raise_for_status()
            data = resp.json()
            if not data:
                break
            repos.extend(data)
            if len(data) < 100:
                break
            page += 1

    return repos[:20]


async def sync_repo_stats(db: AsyncSession, repo_id) -> GitHubRepo:
    result = await db.execute(select(GitHubRepo).where(GitHubRepo.id == repo_id))
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    owner, name = _parse_repo_url(repo.repo_url)
    stats = await get_public_repo_stats(owner, name)

    repo.name = stats["name"]
    repo.full_name = stats["full_name"]
    repo.description = stats["description"]
    repo.stars = stats["stars"]
    repo.forks = stats["forks"]
    repo.language = stats["language"]
    repo.languages = stats["languages"]
    repo.last_commit = datetime.fromisoformat(stats["last_commit"].replace("Z", "+00:00"))
    repo.is_archived = stats["is_archived"]
    repo.last_synced_at = datetime.now(UTC)

    await db.commit()
    return repo


async def link_repo(db: AsyncSession, user_id, repo_url: str) -> GitHubRepo:
    owner, name = _parse_repo_url(repo_url)
    full_url = f"https://github.com/{owner}/{name}"

    existing = await db.execute(
        select(GitHubRepo).where(
            GitHubRepo.user_id == user_id,
            GitHubRepo.repo_url == full_url,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Repository already linked",
        )

    stats = await get_public_repo_stats(owner, name)

    repo = GitHubRepo(
        user_id=user_id,
        repo_url=full_url,
        name=stats["name"],
        full_name=stats["full_name"],
        description=stats["description"],
        stars=stats["stars"],
        forks=stats["forks"],
        language=stats["language"],
        languages=stats["languages"],
        last_commit=datetime.fromisoformat(stats["last_commit"].replace("Z", "+00:00")),
        is_archived=stats["is_archived"],
        last_synced_at=datetime.now(UTC),
    )
    db.add(repo)
    await db.commit()
    return repo


async def unlink_repo(db: AsyncSession, user_id, repo_id) -> None:
    result = await db.execute(
        select(GitHubRepo).where(
            GitHubRepo.id == repo_id,
            GitHubRepo.user_id == user_id,
        )
    )
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(repo)
    await db.commit()
