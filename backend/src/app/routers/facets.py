import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.facet import FacetCreate, FacetResponse, FacetUpdate
from app.schemas.theme import FacetThemeConfigResponse, FacetThemeConfigUpdate
from app.services import facets as facets_service
from app.services import facet_theme as facet_theme_service

router = APIRouter(prefix="/facets", tags=["facets"])


@router.get("", response_model=list[FacetResponse])
async def list_facets(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await facets_service.list_facets(db, current_user.id)


@router.get("/{facet_id}", response_model=FacetResponse)
async def get_facet(
    facet_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await facets_service.get_facet(db, current_user.id, facet_id)


@router.post("", response_model=FacetResponse, status_code=201)
async def create_facet(
    body: FacetCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await facets_service.create_facet(db, current_user.id, body)


@router.put("/{facet_id}", response_model=FacetResponse)
async def update_facet(
    facet_id: uuid.UUID,
    body: FacetUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await facets_service.update_facet(db, current_user.id, facet_id, body)


@router.delete("/{facet_id}", status_code=204)
async def delete_facet(
    facet_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await facets_service.delete_facet(db, current_user.id, facet_id)


@router.put("/{facet_id}/theme", response_model=FacetThemeConfigResponse)
async def update_facet_theme(
    facet_id: uuid.UUID,
    body: FacetThemeConfigUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await facet_theme_service.update_facet_theme_config(db, current_user.id, facet_id, body)
