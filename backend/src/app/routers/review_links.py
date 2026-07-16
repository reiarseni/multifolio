from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.review_link import (
    ReviewLinkAccessResponse,
    ReviewLinkCreate,
    ReviewLinkResponse,
    ReviewLinkValidateRequest,
    ReviewLinkValidateResponse,
)
from app.services import review_link_service

router = APIRouter(tags=["review-links"])


@router.get(
    "/facets/{facet_id}/review-links",
    response_model=list[ReviewLinkResponse],
)
async def list_links(
    facet_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await review_link_service.list_links(db, current_user.id, facet_id)


@router.post(
    "/facets/{facet_id}/review-links",
    response_model=ReviewLinkResponse,
    status_code=201,
)
async def create_link(
    facet_id: uuid.UUID,
    body: ReviewLinkCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await review_link_service.create_link(db, current_user.id, facet_id, body)


@router.delete("/review-links/{link_id}", status_code=204)
async def delete_link(
    link_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await review_link_service.delete_link(db, current_user.id, link_id)


@router.post(
    "/review/{token}/validate",
    response_model=ReviewLinkValidateResponse,
)
async def validate_link(
    token: str,
    body: ReviewLinkValidateRequest,
    db: AsyncSession = Depends(get_db_session),
):
    valid, facet_id = await review_link_service.validate_link(db, token, body.password)
    return ReviewLinkValidateResponse(valid=valid, facet_id=facet_id)


@router.get(
    "/review/{token}/access",
    response_model=ReviewLinkAccessResponse,
)
async def access_link(
    token: str,
    db: AsyncSession = Depends(get_db_session),
):
    link = await review_link_service.access_link(db, token)
    return ReviewLinkAccessResponse(
        facet_id=link.facet_id,
        token=link.token,
        label=link.label,
    )
