from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment
from app.models.profile import Facet
from app.models.review_link import ReviewLink
from app.schemas.comment import CommentCreate


async def _get_facet_by_link(db: AsyncSession, token: str) -> Facet:
    result = await db.execute(
        select(ReviewLink).where(ReviewLink.token == token, ReviewLink.is_active)
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or inactive link",
        )

    result = await db.execute(select(Facet).where(Facet.id == link.facet_id))
    facet = result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facet not found")

    return facet


async def create_comment_by_token(db: AsyncSession, token: str, data: CommentCreate) -> Comment:
    facet = await _get_facet_by_link(db, token)

    if data.parent_id:
        result = await db.execute(
            select(Comment).where(
                Comment.id == data.parent_id,
                Comment.facet_id == facet.id,
            )
        )
        parent = result.scalar_one_or_none()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found",
            )

    comment = Comment(
        facet_id=facet.id,
        parent_id=data.parent_id,
        content=data.content,
        section_ref=data.section_ref,
        author_name=data.author_name,
        author_email=data.author_email,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    # eagerly load replies for serialization
    result = await db.execute(
        select(Comment).where(Comment.id == comment.id).options(selectinload(Comment.replies))
    )
    return result.scalar_one()


async def get_comments_by_token(db: AsyncSession, token: str) -> list[Comment]:
    facet = await _get_facet_by_link(db, token)

    result = await db.execute(
        select(Comment)
        .where(Comment.facet_id == facet.id)
        .options(selectinload(Comment.replies))
        .order_by(Comment.created_at.asc())
    )
    return list(result.scalars().all())


async def get_comments_by_facet_id(db: AsyncSession, facet_id: uuid.UUID) -> list[Comment]:
    result = await db.execute(
        select(Comment)
        .where(Comment.facet_id == facet_id)
        .options(selectinload(Comment.replies))
        .order_by(Comment.created_at.asc())
    )
    return list(result.scalars().all())


async def resolve_comment(db: AsyncSession, user_id: uuid.UUID, comment_id: uuid.UUID) -> Comment:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    result = await db.execute(
        select(Facet).where(
            Facet.id == comment.facet_id,
            Facet.user_id == user_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your facet")

    comment.status = "resolved"
    await db.commit()
    await db.refresh(comment)
    result = await db.execute(
        select(Comment).where(Comment.id == comment.id).options(selectinload(Comment.replies))
    )
    return result.scalar_one()


async def get_unread_count(db: AsyncSession, user_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count(Comment.id))
        .select_from(Comment)
        .join(Facet, Comment.facet_id == Facet.id)
        .where(Facet.user_id == user_id, Comment.status == "pending")
    )
    return result.scalar() or 0
