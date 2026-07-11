import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.open_to_role import OpenToRoleResponse, OpenToRoleUpdate
from app.services import open_to_role_service

router = APIRouter(prefix="/facets", tags=["open-to-role"])


@router.patch("/{facet_id}/open-to-role", response_model=OpenToRoleResponse)
async def upsert_open_to_role(
    facet_id: uuid.UUID,
    body: OpenToRoleUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await open_to_role_service.upsert_open_to_role(db, current_user.id, facet_id, body)


@router.get("/{facet_id}/open-to-role", response_model=OpenToRoleResponse | None)
async def get_open_to_role(
    facet_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await open_to_role_service.get_open_to_role(db, current_user.id, facet_id)


@router.delete("/{facet_id}/open-to-role", status_code=204)
async def delete_open_to_role(
    facet_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await open_to_role_service.delete_open_to_role(db, current_user.id, facet_id)
