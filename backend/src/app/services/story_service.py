from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Facet
from app.models.story_section import StorySection
from app.schemas.story import StorySectionCreate, StorySectionUpdate


async def _load_facet(db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID) -> Facet:
    result = await db.execute(select(Facet).where(Facet.id == facet_id, Facet.user_id == user_id))
    facet = result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return facet


async def get_story(
    db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID
) -> list[StorySection]:
    await _load_facet(db, user_id, facet_id)
    result = await db.execute(
        select(StorySection).where(StorySection.facet_id == facet_id).order_by(StorySection.order)
    )
    return list(result.scalars().all())


async def upsert_section(
    db: AsyncSession,
    user_id: uuid.UUID,
    facet_id: uuid.UUID,
    data: StorySectionCreate,
) -> StorySection:
    await _load_facet(db, user_id, facet_id)

    section = StorySection(
        facet_id=facet_id,
        section_type=data.section_type,
        title=data.title,
        content=data.content,
        media_urls=data.media_urls,
        order=data.order,
        is_visible=data.is_visible,
    )
    db.add(section)
    await db.commit()
    await db.refresh(section)
    return section


async def update_section(
    db: AsyncSession,
    user_id: uuid.UUID,
    section_id: uuid.UUID,
    data: StorySectionUpdate,
) -> StorySection:
    result = await db.execute(select(StorySection).where(StorySection.id == section_id))
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await _load_facet(db, user_id, section.facet_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(section, field, value)

    await db.commit()
    await db.refresh(section)
    return section


async def reorder_sections(
    db: AsyncSession,
    user_id: uuid.UUID,
    facet_id: uuid.UUID,
    section_ids: list[uuid.UUID],
) -> list[StorySection]:
    await _load_facet(db, user_id, facet_id)

    result = await db.execute(select(StorySection).where(StorySection.facet_id == facet_id))
    sections = {s.id: s for s in result.scalars().all()}

    for idx, sid in enumerate(section_ids):
        if sid in sections:
            sections[sid].order = idx

    await db.commit()

    result = await db.execute(
        select(StorySection).where(StorySection.facet_id == facet_id).order_by(StorySection.order)
    )
    return list(result.scalars().all())


async def delete_section(
    db: AsyncSession,
    user_id: uuid.UUID,
    section_id: uuid.UUID,
) -> None:
    result = await db.execute(select(StorySection).where(StorySection.id == section_id))
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await _load_facet(db, user_id, section.facet_id)

    await db.delete(section)
    await db.commit()
