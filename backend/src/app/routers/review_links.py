from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.comment import ReviewLinkCreate, ReviewLinkResponse
from app.services import review_link_service

router = APIRouter(tags=["review-links"])


@router.post(
    "/review/links",
    response_model=ReviewLinkResponse,
    status_code=201,
)
async def create_review_link(
    body: ReviewLinkCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await review_link_service.create_link(db, current_user.id, body.facet_id)


@router.get(
    "/review/{token}/validate",
    response_model=ReviewLinkResponse,
)
async def validate_review_link(
    token: str,
    db: AsyncSession = Depends(get_db_session),
):
    return await review_link_service.validate_link(db, token)


@router.delete(
    "/review-links/{link_id}",
    status_code=204,
)
async def deactivate_review_link(
    link_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await review_link_service.deactivate_link(db, current_user.id, link_id)


@router.get(
    "/facets/{facet_id}/review-links",
    response_model=list[ReviewLinkResponse],
)
async def list_review_links(
    facet_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await review_link_service.list_links(db, current_user.id, facet_id)
