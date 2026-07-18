from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.comment import (
    CommentCreate,
    CommentResponse,
    CommentUnreadCount,
)
from app.services import comment_service

router = APIRouter(tags=["comments"])


@router.get(
    "/review/{token}/comments",
    response_model=list[CommentResponse],
)
async def list_comments_by_token(
    token: str,
    db: AsyncSession = Depends(get_db_session),
):
    return await comment_service.get_comments_by_token(db, token)


@router.post(
    "/review/{token}/comments",
    response_model=CommentResponse,
    status_code=201,
)
async def create_comment_by_token(
    token: str,
    body: CommentCreate,
    db: AsyncSession = Depends(get_db_session),
):
    return await comment_service.create_comment_by_token(db, token, body)


@router.patch(
    "/comments/{comment_id}/resolve",
    response_model=CommentResponse,
)
async def resolve_comment(
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await comment_service.resolve_comment(db, current_user.id, comment_id)


@router.get(
    "/dashboard/comments/unread",
    response_model=CommentUnreadCount,
)
async def get_unread_count(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    count = await comment_service.get_unread_count(db, current_user.id)
    return CommentUnreadCount(count=count)


@router.get(
    "/facets/{facet_id}/comments",
    response_model=list[CommentResponse],
)
async def list_comments_by_facet(
    facet_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await comment_service.get_comments_by_facet_id(db, facet_id)
