from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.models.facet_analysis import FacetAnalysis
from app.models.profile import Facet
from app.prompts.job_fit import (
    COMPARE_WITH_FACET_PROMPT,
    EXTRACT_ENTRIES_PROMPT,
    SUGGEST_REORDER_PROMPT,
)
from app.schemas.job_fit import GapItem, JobFitResponse, ReorderSuggestion

settings = get_settings()


def _build_facet_dict(facet: Facet) -> dict:
    return {
        "id": str(facet.id),
        "name": facet.name,
        "slug": facet.slug,
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
                "start_date": str(e.start_date),
                "end_date": str(e.end_date) if e.end_date else None,
                "is_current": e.is_current,
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
        temperature=0.3,
        max_tokens=2000,
    )
    return response.choices[0].message.content or ""


async def analyze_facet_fit(
    db: AsyncSession,
    facet_id: uuid.UUID,
    job_posting: str,
    current_user_id: uuid.UUID,
) -> JobFitResponse:
    result = await db.execute(
        select(Facet)
        .where(Facet.id == facet_id)
        .options(
            selectinload(Facet.selected_skills),
            selectinload(Facet.selected_experiences),
            selectinload(Facet.selected_educations),
            selectinload(Facet.selected_projects),
            selectinload(Facet.user),
        )
    )
    facet = result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facet not found")
    if str(facet.user_id) != str(current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your facet")

    facet_dict = _build_facet_dict(facet)

    entities_raw = await _call_llm(EXTRACT_ENTRIES_PROMPT.format(job_posting=job_posting))
    import json

    try:
        cleaned = entities_raw.strip().removeprefix("```json").removesuffix("```").strip()
        entities = json.loads(cleaned)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse LLM response for entity extraction",
        )

    comparison_raw = await _call_llm(
        COMPARE_WITH_FACET_PROMPT.format(
            facet_json=json.dumps(facet_dict), entities_json=json.dumps(entities)
        )
    )
    try:
        cleaned = comparison_raw.strip().removeprefix("```json").removesuffix("```").strip()
        comparison = json.loads(cleaned)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse LLM response for comparison",
        )

    reorder_raw = await _call_llm(
        SUGGEST_REORDER_PROMPT.format(
            facet_json=json.dumps(facet_dict), gaps_json=json.dumps(comparison.get("gaps", []))
        )
    )
    reorder = None
    try:
        cleaned = reorder_raw.strip().removeprefix("```json").removesuffix("```").strip()
        parsed = json.loads(cleaned)
        reorder = ReorderSuggestion(
            rationale=parsed["rationale"], proposed_order=parsed["proposed_order"]
        )
    except (json.JSONDecodeError, KeyError):
        pass

    gaps_data = comparison.get("gaps", [])
    gaps = [GapItem(**g) for g in gaps_data]

    analysis = FacetAnalysis(
        facet_id=facet.id,
        job_title=entities.get("title"),
        job_company=entities.get("company"),
        overall_score=comparison.get("overall_score", 0),
        skills_score=comparison.get("skills_score", 0),
        experience_score=comparison.get("experience_score", 0),
        stack_score=comparison.get("stack_score", 0),
        tone_score=comparison.get("tone_score", 0),
        gaps=[g.model_dump() for g in gaps],
        suggestions=comparison.get("suggestions", []),
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    return JobFitResponse(
        id=analysis.id,
        job_title=analysis.job_title,
        job_company=analysis.job_company,
        overall_score=analysis.overall_score,
        skills_score=analysis.skills_score,
        experience_score=analysis.experience_score,
        stack_score=analysis.stack_score,
        tone_score=analysis.tone_score,
        gaps=gaps,
        suggestions=comparison.get("suggestions", []),
        reorder_suggestion=reorder,
        created_at=analysis.created_at,
    )


async def get_analysis_history(
    db: AsyncSession,
    facet_id: uuid.UUID,
    current_user_id: uuid.UUID,
) -> list[FacetAnalysis]:
    result = await db.execute(select(Facet).where(Facet.id == facet_id))
    facet = result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facet not found")
    if str(facet.user_id) != str(current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your facet")

    analyses_result = await db.execute(
        select(FacetAnalysis)
        .where(FacetAnalysis.facet_id == facet_id)
        .order_by(FacetAnalysis.created_at.desc())
    )
    return list(analyses_result.scalars().all())


async def delete_analysis(
    db: AsyncSession,
    analysis_id: uuid.UUID,
    current_user_id: uuid.UUID,
) -> None:
    result = await db.execute(
        select(FacetAnalysis)
        .where(FacetAnalysis.id == analysis_id)
        .options(selectinload(FacetAnalysis.facet))
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    if str(analysis.facet.user_id) != str(current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your facet")

    await db.delete(analysis)
    await db.commit()
