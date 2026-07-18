from __future__ import annotations

import json
import uuid

from fastapi import HTTPException, status
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.models.profile import Facet
from app.prompts.seo import EXTRACT_KEYWORDS_PROMPT, GENERATE_META_PROMPT
from app.schemas.seo import SEOConfigResponse, SEOUpdateResponse, SEOVariant

settings = get_settings()


def _build_facet_dict(facet: Facet) -> dict:
    return {
        "title": facet.title,
        "bio": facet.bio,
        "skills": [
            {"name": s.name, "category": s.category, "level": s.level}
            for s in facet.selected_skills
        ],
        "experiences": [
            {
                "company": e.company,
                "position": e.position,
                "description": e.description,
            }
            for e in facet.selected_experiences
        ],
        "education": [
            {
                "institution": e.institution,
                "degree": e.degree,
                "field": e.field,
            }
            for e in facet.selected_educations
        ],
        "projects": [
            {
                "title": p.title,
                "description": p.description,
            }
            for p in facet.selected_projects
        ],
    }


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


async def suggest_seo(
    db: AsyncSession,
    facet_id: uuid.UUID,
    current_user_id: uuid.UUID,
) -> list[SEOVariant]:
    result = await db.execute(
        select(Facet)
        .where(Facet.id == facet_id)
        .options(
            selectinload(Facet.selected_skills),
            selectinload(Facet.selected_experiences),
            selectinload(Facet.selected_educations),
            selectinload(Facet.selected_projects),
        )
    )
    facet = result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facet not found")
    if str(facet.user_id) != str(current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your facet")

    facet_dict = _build_facet_dict(facet)

    prompt = EXTRACT_KEYWORDS_PROMPT.format(facet_json=json.dumps(facet_dict))
    keywords_raw = await _call_llm(prompt)
    try:
        keywords_data = json.loads(_clean_json(keywords_raw))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse keyword extraction response",
        )

    meta_raw = await _call_llm(
        GENERATE_META_PROMPT.format(
            role=keywords_data.get("role", ""),
            keywords=json.dumps(keywords_data.get("keywords", [])),
            seniority_level=keywords_data.get("seniority_level", "mid"),
            industry=keywords_data.get("industry", ""),
            facet_json=json.dumps(facet_dict),
        )
    )
    try:
        meta_data = json.loads(_clean_json(meta_raw))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse meta generation response",
        )

    return [SEOVariant(**v) for v in meta_data.get("variants", [])]


async def update_seo(
    db: AsyncSession,
    facet_id: uuid.UUID,
    current_user_id: uuid.UUID,
    meta_title: str | None,
    meta_description: str | None,
) -> SEOUpdateResponse:
    result = await db.execute(select(Facet).where(Facet.id == facet_id))
    facet = result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facet not found")
    if str(facet.user_id) != str(current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your facet")

    facet.meta_title = meta_title
    facet.meta_description = meta_description
    await db.commit()

    return SEOUpdateResponse(message="SEO metadata updated")


async def get_seo_config(
    db: AsyncSession,
    facet_id: uuid.UUID,
    current_user_id: uuid.UUID,
) -> SEOConfigResponse:
    result = await db.execute(select(Facet).where(Facet.id == facet_id))
    facet = result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facet not found")
    if str(facet.user_id) != str(current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your facet")

    return SEOConfigResponse(
        meta_title=facet.meta_title,
        meta_description=facet.meta_description,
    )
