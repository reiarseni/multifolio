from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.story import (
    StoryReorderRequest,
    StorySectionCreate,
    StorySectionResponse,
    StorySectionUpdate,
)
from app.services import story_service

router = APIRouter(tags=["stories"])


@router.get("/facets/{facet_id}/story", response_model=list[StorySectionResponse])
async def get_story(
    facet_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await story_service.get_story(db, current_user.id, facet_id)


@router.post(
    "/facets/{facet_id}/story/sections",
    response_model=StorySectionResponse,
    status_code=201,
)
async def create_section(
    facet_id: uuid.UUID,
    body: StorySectionCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await story_service.upsert_section(db, current_user.id, facet_id, body)


@router.patch("/story/sections/{section_id}", response_model=StorySectionResponse)
async def update_section(
    section_id: uuid.UUID,
    body: StorySectionUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await story_service.update_section(db, current_user.id, section_id, body)


@router.put(
    "/facets/{facet_id}/story/reorder",
    response_model=list[StorySectionResponse],
)
async def reorder_sections(
    facet_id: uuid.UUID,
    body: StoryReorderRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await story_service.reorder_sections(db, current_user.id, facet_id, body.section_ids)


@router.delete("/story/sections/{section_id}", status_code=204)
async def delete_section(
    section_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await story_service.delete_section(db, current_user.id, section_id)
