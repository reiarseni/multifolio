import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.profile import Facet
from app.models.review_link import ReviewLink
from app.schemas.review_link import ReviewLinkCreate


async def _load_facet(db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID) -> Facet:
    result = await db.execute(select(Facet).where(Facet.id == facet_id, Facet.user_id == user_id))
    facet = result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return facet


def _generate_token() -> str:
    return secrets.token_urlsafe(48)[:64]


async def create_review_link(
    db: AsyncSession,
    user_id: uuid.UUID,
    facet_id: uuid.UUID,
    data: ReviewLinkCreate,
) -> ReviewLink:
    await _load_facet(db, user_id, facet_id)

    password_hash = None
    if data.password:
        password_hash = hash_password(data.password)

    expires_at = None
    if data.expires_in_hours:
        expires_at = datetime.now(UTC) + timedelta(hours=data.expires_in_hours)

    link = ReviewLink(
        facet_id=facet_id,
        token=_generate_token(),
        created_by=user_id,
        label=data.label,
        password_hash=password_hash,
        expires_at=expires_at,
        single_use=password_hash is not None or expires_at is not None,
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def list_review_links(
    db: AsyncSession,
    user_id: uuid.UUID,
    facet_id: uuid.UUID,
) -> list[ReviewLink]:
    await _load_facet(db, user_id, facet_id)
    result = await db.execute(
        select(ReviewLink)
        .where(ReviewLink.facet_id == facet_id)
        .order_by(ReviewLink.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_review_link(
    db: AsyncSession,
    user_id: uuid.UUID,
    link_id: uuid.UUID,
) -> None:
    result = await db.execute(select(ReviewLink).where(ReviewLink.id == link_id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await _load_facet(db, user_id, link.facet_id)

    await db.delete(link)
    await db.commit()


async def validate_link_access(
    db: AsyncSession,
    token: str,
    password: str | None = None,
) -> ReviewLink:
    result = await db.execute(select(ReviewLink).where(ReviewLink.token == token))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link no encontrado o invalido",
        )

    if link.expires_at and datetime.now(UTC) > link.expires_at:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Este link ha expirado",
        )

    if link.used_at and link.single_use:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Este link ya fue utilizado",
        )

    if link.password_hash:
        if not password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Se requiere contraseña para acceder a este link",
            )
        if not verify_password(password, link.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Contraseña incorrecta",
            )

    return link


async def mark_as_used(db: AsyncSession, link_id: uuid.UUID) -> None:
    result = await db.execute(select(ReviewLink).where(ReviewLink.id == link_id))
    link = result.scalar_one_or_none()
    if link:
        link.used_at = datetime.now(UTC)
        await db.commit()
