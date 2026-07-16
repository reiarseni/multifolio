from __future__ import annotations

import uuid

from app.schemas.story import StorySectionResponse
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.ai import (
    AIHeadlineRequest,
    AIHeadlineResponse,
    AISuggestionResponse,
    ApplySuggestionRequest,
)
from app.services import ai_story_service

router = APIRouter(tags=["ai"])


@router.post(
    "/ai/story/sections/{section_id}/improve",
    response_model=AISuggestionResponse,
)
async def improve_section(
    section_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await ai_story_service.suggest_improvements(db, current_user.id, section_id)


@router.post(
    "/ai/story/sections/{section_id}/expand",
    response_model=AISuggestionResponse,
)
async def expand_section(
    section_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await ai_story_service.expand_narrative(db, current_user.id, section_id)


@router.post(
    "/ai/facets/{facet_id}/suggest-headline",
    response_model=AIHeadlineResponse,
)
async def suggest_headline(
    facet_id: uuid.UUID,
    body: AIHeadlineRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await ai_story_service.suggest_headline(db, current_user.id, facet_id, body.target_role)


@router.post(
    "/ai/apply-suggestion",
    response_model=StorySectionResponse,
)
async def apply_suggestion(
    body: ApplySuggestionRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await ai_story_service.apply_suggestion(
        db, current_user.id, body.section_id, body.suggestion
    )
