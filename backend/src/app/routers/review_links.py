import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.review_link import (
    ReviewLinkCreate,
    ReviewLinkResponse,
    ReviewLinkValidateRequest,
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
    links = await review_link_service.list_review_links(db, current_user.id, facet_id)
    return [
        ReviewLinkResponse(
            id=link.id,
            facet_id=link.facet_id,
            token=link.token,
            label=link.label,
            requires_password=link.password_hash is not None,
            expires_at=link.expires_at,
            single_use=link.single_use,
            is_used=link.used_at is not None,
            created_at=link.created_at,
            updated_at=link.updated_at,
        )
        for link in links
    ]


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
    link = await review_link_service.create_review_link(db, current_user.id, facet_id, body)
    return ReviewLinkResponse(
        id=link.id,
        facet_id=link.facet_id,
        token=link.token,
        label=link.label,
        requires_password=link.password_hash is not None,
        expires_at=link.expires_at,
        single_use=link.single_use,
        is_used=link.used_at is not None,
        created_at=link.created_at,
        updated_at=link.updated_at,
    )


@router.delete("/review-links/{link_id}", status_code=204)
async def delete_link(
    link_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await review_link_service.delete_review_link(db, current_user.id, link_id)


@router.post("/review/{token}/validate")
async def validate_link(
    token: str,
    body: ReviewLinkValidateRequest,
    db: AsyncSession = Depends(get_db_session),
):
    link = await review_link_service.validate_link_access(db, token, body.password)
    if link.single_use and not link.used_at:
        await review_link_service.mark_as_used(db, link.id)
    return {"valid": True, "facet_id": str(link.facet_id)}


@router.get("/review/{token}/access")
async def access_link(
    token: str,
    db: AsyncSession = Depends(get_db_session),
):
    link = await review_link_service.validate_link_access(db, token)
    if link.single_use and not link.used_at:
        await review_link_service.mark_as_used(db, link.id)
    return {"facet_id": str(link.facet_id), "token": link.token, "label": link.label}
