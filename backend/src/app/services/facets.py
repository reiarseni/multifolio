import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import BaseProfile, Education, Facet, Project, Skill, WorkExperience
from app.schemas.facet import FacetCreate, FacetUpdate


async def _get_or_create_profile(db: AsyncSession, user_id: uuid.UUID) -> BaseProfile:
    result = await db.execute(select(BaseProfile).where(BaseProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = BaseProfile(user_id=user_id, full_name="", email="")
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


async def _resolve_selected(
    db: AsyncSession,
    profile_id: uuid.UUID,
    item_ids: list[uuid.UUID],
    model,
):
    if not item_ids:
        return []
    result = await db.execute(
        select(model).where(
            model.id.in_(item_ids),
            model.profile_id == profile_id,
        )
    )
    return list(result.scalars().all())


async def _load_facet(db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID) -> Facet:
    result = await db.execute(
        select(Facet)
        .where(Facet.id == facet_id, Facet.user_id == user_id)
        .options(
            selectinload(Facet.selected_experiences),
            selectinload(Facet.selected_educations),
            selectinload(Facet.selected_skills),
            selectinload(Facet.selected_projects),
        )
    )
    facet = result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return facet


async def list_facets(db: AsyncSession, user_id: uuid.UUID) -> list[Facet]:
    result = await db.execute(
        select(Facet)
        .where(Facet.user_id == user_id)
        .order_by(Facet.created_at)
        .options(
            selectinload(Facet.selected_experiences),
            selectinload(Facet.selected_educations),
            selectinload(Facet.selected_skills),
            selectinload(Facet.selected_projects),
        )
    )
    return list(result.scalars().all())


async def get_facet(db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID) -> Facet:
    return await _load_facet(db, user_id, facet_id)


async def create_facet(db: AsyncSession, user_id: uuid.UUID, data: FacetCreate) -> Facet:
    profile = await _get_or_create_profile(db, user_id)
    facet = Facet(
        user_id=user_id,
        name=data.name,
        slug=data.slug,
        title=data.title,
        bio=data.bio,
        meta_title=data.meta_title,
        meta_description=data.meta_description,
        pdf_template=data.pdf_template,
        is_published=data.is_published,
    )
    db.add(facet)
    await db.flush()

    if data.experience_ids:
        items = await _resolve_selected(db, profile.id, data.experience_ids, WorkExperience)
        await db.run_sync(lambda _: setattr(facet, "selected_experiences", items))
    if data.education_ids:
        items = await _resolve_selected(db, profile.id, data.education_ids, Education)
        await db.run_sync(lambda _: setattr(facet, "selected_educations", items))
    if data.skill_ids:
        items = await _resolve_selected(db, profile.id, data.skill_ids, Skill)
        await db.run_sync(lambda _: setattr(facet, "selected_skills", items))
    if data.project_ids:
        items = await _resolve_selected(db, profile.id, data.project_ids, Project)
        await db.run_sync(lambda _: setattr(facet, "selected_projects", items))

    await db.commit()
    return await _load_facet(db, user_id, facet.id)


async def update_facet(
    db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID, data: FacetUpdate
) -> Facet:
    facet = await _load_facet(db, user_id, facet_id)
    profile = await _get_or_create_profile(db, user_id)

    scalar_fields = data.model_dump(
        exclude={"experience_ids", "education_ids", "skill_ids", "project_ids"},
        exclude_unset=True,
    )
    for field, value in scalar_fields.items():
        setattr(facet, field, value)

    if data.experience_ids is not None:
        items = await _resolve_selected(db, profile.id, data.experience_ids, WorkExperience)
        await db.run_sync(lambda _: setattr(facet, "selected_experiences", items))
    if data.education_ids is not None:
        items = await _resolve_selected(db, profile.id, data.education_ids, Education)
        await db.run_sync(lambda _: setattr(facet, "selected_educations", items))
    if data.skill_ids is not None:
        items = await _resolve_selected(db, profile.id, data.skill_ids, Skill)
        await db.run_sync(lambda _: setattr(facet, "selected_skills", items))
    if data.project_ids is not None:
        items = await _resolve_selected(db, profile.id, data.project_ids, Project)
        await db.run_sync(lambda _: setattr(facet, "selected_projects", items))

    await db.commit()
    return await _load_facet(db, user_id, facet.id)


async def delete_facet(db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID) -> None:
    facet = await _load_facet(db, user_id, facet_id)
    await db.delete(facet)
    await db.commit()
