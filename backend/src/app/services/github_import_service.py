from __future__ import annotations

import base64
import json
import uuid

import httpx
from fastapi import HTTPException, status
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.models.github_repo import GitHubRepo
from app.models.profile import Facet, Project
from app.prompts.github_import import ANALYZE_REPO_PROMPT
from app.schemas.github_import import AIGeneratedProject, ImportConfirmResponse
from app.services.github_service import _parse_repo_url

settings = get_settings()
GITHUB_API_BASE = "https://api.github.com"


async def _fetch_readme(owner: str, repo: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/readme",
            headers={"Accept": "application/vnd.github.v3+json"},
        )
        if resp.status_code == 404:
            return ""
        resp.raise_for_status()
        data = resp.json()
        if data.get("encoding") == "base64":
            content = data.get("content", "")
            return base64.b64decode(content).decode("utf-8", errors="replace")
        return data.get("content", "")


async def _call_llm(prompt: str) -> str:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2000,
    )
    return response.choices[0].message.content or ""


def _clean_json(raw: str) -> str:
    return raw.strip().removeprefix("```json").removesuffix("```").strip()


async def _get_profile(db: AsyncSession, user_id: uuid.UUID):
    from app.models.profile import BaseProfile

    result = await db.execute(select(BaseProfile).where(BaseProfile.user_id == user_id))
    return result.scalar_one_or_none()


async def _ensure_profile(db: AsyncSession, user_id: uuid.UUID):
    from app.models.profile import BaseProfile

    profile = await _get_profile(db, user_id)
    if profile is None:
        profile = BaseProfile(user_id=user_id, full_name="")
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


async def analyze_repos(
    db: AsyncSession,
    user_id: uuid.UUID,
    repo_ids: list[uuid.UUID],
    facet_id: uuid.UUID,
) -> list[AIGeneratedProject]:
    result = await db.execute(
        select(Facet).where(Facet.id == facet_id).options(selectinload(Facet.selected_projects))
    )
    facet = result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facet not found")
    if str(facet.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your facet")

    repo_result = await db.execute(
        select(GitHubRepo).where(
            GitHubRepo.id.in_(repo_ids),
            GitHubRepo.user_id == user_id,
        )
    )
    repos = list(repo_result.scalars().all())
    if len(repos) != len(repo_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more repos not found or not owned by user",
        )

    generated: list[AIGeneratedProject] = []
    for repo in repos:
        owner, name = _parse_repo_url(repo.repo_url)
        readme_content = await _fetch_readme(owner, name)

        prompt = ANALYZE_REPO_PROMPT.format(
            repo_name=repo.name,
            repo_full_name=repo.full_name,
            repo_description=repo.description or "",
            repo_language=repo.language or "",
            repo_stars=repo.stars,
            repo_forks=repo.forks,
            repo_topics="",
            readme_content=readme_content[:5000] if readme_content else "",
        )

        raw = await _call_llm(prompt)
        try:
            data = json.loads(_clean_json(raw))
        except json.JSONDecodeError:
            data = {
                "title": repo.name,
                "description": repo.description or "",
                "markdown_content": "",
            }

        generated.append(
            AIGeneratedProject(
                repo_id=repo.id,
                title=data.get("title", repo.name),
                description=data.get("description", repo.description),
                markdown_content=data.get("markdown_content", ""),
                github_url=repo.repo_url,
            )
        )

    return generated


async def confirm_import(
    db: AsyncSession,
    user_id: uuid.UUID,
    facet_id: uuid.UUID,
    projects: list[AIGeneratedProject],
) -> ImportConfirmResponse:
    result = await db.execute(
        select(Facet).where(Facet.id == facet_id).options(selectinload(Facet.selected_projects))
    )
    facet = result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facet not found")
    if str(facet.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your facet")

    profile = await _ensure_profile(db, user_id)

    project_ids: list[uuid.UUID] = []
    for p in projects:
        project = Project(
            profile_id=profile.id,
            title=p.title,
            description=p.description,
            markdown_content=p.markdown_content,
            github_url=p.github_url,
        )
        db.add(project)
        await db.flush()
        project_ids.append(project.id)

        facet.selected_projects.append(project)

    await db.commit()

    return ImportConfirmResponse(
        message=f"{len(projects)} proyecto(s) importado(s) correctamente",
        count=len(projects),
        project_ids=project_ids,
    )
