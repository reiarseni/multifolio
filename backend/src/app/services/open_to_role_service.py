import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.open_to_role import OpenToRole
from app.models.profile import Facet
from app.schemas.open_to_role import OpenToRoleUpdate


async def _load_facet(db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID) -> Facet:
    result = await db.execute(select(Facet).where(Facet.id == facet_id, Facet.user_id == user_id))
    facet = result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return facet


async def _load_open_to_role(db: AsyncSession, facet_id: uuid.UUID) -> OpenToRole | None:
    result = await db.execute(select(OpenToRole).where(OpenToRole.facet_id == facet_id))
    return result.scalar_one_or_none()


async def upsert_open_to_role(
    db: AsyncSession,
    user_id: uuid.UUID,
    facet_id: uuid.UUID,
    data: OpenToRoleUpdate,
) -> OpenToRole:
    await _load_facet(db, user_id, facet_id)
    existing = await _load_open_to_role(db, facet_id)

    if existing:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing, field, value)
        await db.commit()
        return existing

    new_role = OpenToRole(
        facet_id=facet_id,
        status=data.status or "not_available",
        role_type=data.role_type,
        modality=data.modality,
        location=data.location,
        timezone=data.timezone,
    )
    db.add(new_role)
    await db.commit()
    return new_role


async def get_open_to_role(
    db: AsyncSession,
    user_id: uuid.UUID,
    facet_id: uuid.UUID,
) -> OpenToRole | None:
    await _load_facet(db, user_id, facet_id)
    return await _load_open_to_role(db, facet_id)


async def delete_open_to_role(
    db: AsyncSession,
    user_id: uuid.UUID,
    facet_id: uuid.UUID,
) -> None:
    await _load_facet(db, user_id, facet_id)
    existing = await _load_open_to_role(db, facet_id)
    if existing:
        await db.delete(existing)
        await db.commit()
