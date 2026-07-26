from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm_client import (
    apply_suggestion as llm_apply_suggestion,
)
from app.core.llm_client import (
    expand_section as llm_expand_section,
)
from app.core.llm_client import (
    improve_content as llm_improve_content,
)
from app.core.llm_client import (
    suggest_headline as llm_suggest_headline,
)
from app.models.profile import Facet
from app.models.story_section import StorySection
from app.schemas.ai import (
    AIHeadlineResponse,
    AISuggestionResponse,
)


async def _load_section(
    db: AsyncSession, user_id: uuid.UUID, section_id: uuid.UUID
) -> StorySection:
    result = await db.execute(select(StorySection).where(StorySection.id == section_id))
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

    result = await db.execute(
        select(Facet).where(Facet.id == section.facet_id, Facet.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your facet")

    return section


async def _load_facet(db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID) -> Facet:
    result = await db.execute(select(Facet).where(Facet.id == facet_id, Facet.user_id == user_id))
    facet = result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facet not found")
    return facet


async def suggest_improvements(
    db: AsyncSession, user_id: uuid.UUID, section_id: uuid.UUID
) -> AISuggestionResponse:
    section = await _load_section(db, user_id, section_id)

    if not section.content or not section.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Section has no content to improve",
        )

    suggested = await llm_improve_content(section.content, section.section_type, section.title)

    return AISuggestionResponse(
        original=section.content,
        suggested=suggested,
        changes_summary="Contenido mejorado con verbos de acción y métricas.",
    )


async def expand_narrative(
    db: AsyncSession, user_id: uuid.UUID, section_id: uuid.UUID
) -> AISuggestionResponse:
    section = await _load_section(db, user_id, section_id)

    if not section.content or not section.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Section has no content to expand",
        )

    suggested = await llm_expand_section(section.content, section.section_type, section.title)

    return AISuggestionResponse(
        original=section.content,
        suggested=suggested,
        changes_summary="Narrativa expandida con más contexto y detalles.",
    )


async def suggest_headline(
    db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID, target_role: str
) -> AIHeadlineResponse:
    facet = await _load_facet(db, user_id, facet_id)

    result = await llm_suggest_headline(
        title=facet.title or facet.name,
        bio=facet.bio or "",
        target_role=target_role,
    )

    return AIHeadlineResponse(title=result["title"], bio=result["bio"])


async def apply_suggestion(
    db: AsyncSession,
    user_id: uuid.UUID,
    section_id: uuid.UUID,
    suggestion: str,
) -> StorySection:
    section = await _load_section(db, user_id, section_id)

    final_content = await llm_apply_suggestion(section.content or "", suggestion)

    section.content = final_content
    await db.commit()
    await db.refresh(section)
    return section
