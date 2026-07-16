from __future__ import annotations

import secrets
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Facet
from app.models.review_link import ReviewLink


async def create_link(db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID) -> ReviewLink:
    result = await db.execute(select(Facet).where(Facet.id == facet_id, Facet.user_id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facet not found")

    link = ReviewLink(
        facet_id=facet_id,
        created_by=user_id,
        token=secrets.token_urlsafe(32),
        is_active=True,
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def validate_link(db: AsyncSession, token: str) -> ReviewLink:
    result = await db.execute(
        select(ReviewLink).where(ReviewLink.token == token, ReviewLink.is_active)
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or inactive link",
        )
    return link


async def deactivate_link(db: AsyncSession, user_id: uuid.UUID, link_id: uuid.UUID) -> None:
    result = await db.execute(select(ReviewLink).where(ReviewLink.id == link_id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    if link.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your link")

    link.is_active = False
    await db.commit()


async def list_links(db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID) -> list[ReviewLink]:
    result = await db.execute(select(Facet).where(Facet.id == facet_id, Facet.user_id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facet not found")

    result = await db.execute(
        select(ReviewLink)
        .where(ReviewLink.facet_id == facet_id)
        .order_by(ReviewLink.created_at.desc())
    )
    return list(result.scalars().all())
