from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Facet
from app.models.review_link import ReviewLink
from app.schemas.review_link import ReviewLinkCreate


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


async def create_link(
    db: AsyncSession,
    user_id: uuid.UUID,
    facet_id: uuid.UUID,
    data: ReviewLinkCreate,
) -> ReviewLink:
    result = await db.execute(select(Facet).where(Facet.id == facet_id, Facet.user_id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facet not found")

    link = ReviewLink(
        facet_id=facet_id,
        token=secrets.token_urlsafe(32),
        label=data.label,
        requires_password=bool(data.password),
        password_hash=_hash_password(data.password) if data.password else None,
        expires_at=datetime.now(UTC) + timedelta(hours=data.expires_in_hours)
        if data.expires_in_hours
        else None,
        single_use=False,
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def list_links(
    db: AsyncSession,
    user_id: uuid.UUID,
    facet_id: uuid.UUID,
) -> list[ReviewLink]:
    result = await db.execute(select(Facet).where(Facet.id == facet_id, Facet.user_id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facet not found")

    result = await db.execute(
        select(ReviewLink)
        .where(ReviewLink.facet_id == facet_id)
        .order_by(ReviewLink.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_link(
    db: AsyncSession,
    user_id: uuid.UUID,
    link_id: uuid.UUID,
) -> None:
    result = await db.execute(select(ReviewLink).where(ReviewLink.id == link_id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    result = await db.execute(
        select(Facet).where(Facet.id == link.facet_id, Facet.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your facet")

    await db.delete(link)
    await db.commit()


async def validate_link(
    db: AsyncSession,
    token: str,
    password: str | None,
) -> tuple[bool, uuid.UUID]:
    result = await db.execute(select(ReviewLink).where(ReviewLink.token == token))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    if link.expires_at and link.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Link expired")

    if link.single_use and link.is_used:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Link already used")

    if link.requires_password:
        if not password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password required")
        if not link.password_hash or not _verify_password(password, link.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    if link.single_use:
        link.is_used = True
        await db.commit()

    return True, link.facet_id


async def access_link(
    db: AsyncSession,
    token: str,
) -> ReviewLink:
    result = await db.execute(select(ReviewLink).where(ReviewLink.token == token))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    if link.expires_at and link.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Link expired")

    if link.single_use and link.is_used:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Link already used")

    return link
