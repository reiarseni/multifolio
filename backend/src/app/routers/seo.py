from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.seo import (
    SEOConfigResponse,
    SEOSuggestResponse,
    SEOUpdateRequest,
    SEOUpdateResponse,
)
from app.services import seo_service

router = APIRouter(prefix="/facets", tags=["seo"])


@router.post("/{facet_id}/seo/suggest", response_model=SEOSuggestResponse)
async def suggest_seo(
    facet_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    variants = await seo_service.suggest_seo(
        db=db,
        facet_id=facet_id,
        current_user_id=current_user.id,
    )
    return SEOSuggestResponse(variants=variants)


@router.put("/{facet_id}/seo", response_model=SEOUpdateResponse)
async def update_seo(
    facet_id: uuid.UUID,
    body: SEOUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await seo_service.update_seo(
        db=db,
        facet_id=facet_id,
        current_user_id=current_user.id,
        meta_title=body.meta_title,
        meta_description=body.meta_description,
    )


@router.get("/{facet_id}/seo", response_model=SEOConfigResponse)
async def get_seo_config(
    facet_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await seo_service.get_seo_config(
        db=db,
        facet_id=facet_id,
        current_user_id=current_user.id,
    )
