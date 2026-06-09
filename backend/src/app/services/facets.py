import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import Certification, Education, Facet, Project, Skill, WorkExperience
from app.schemas.facet import FacetCreate, FacetUpdate
from app.services.utils import get_profile_or_404


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
            selectinload(Facet.selected_certifications),
            selectinload(Facet.selected_projects),
            selectinload(Facet.selected_projects),
            selectinload(Facet.selected_certifications),
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
            selectinload(Facet.selected_certifications),
        )
    )
    return list(result.scalars().all())


async def get_facet(db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID) -> Facet:
    return await _load_facet(db, user_id, facet_id)


async def create_facet(db: AsyncSession, user_id: uuid.UUID, data: FacetCreate) -> Facet:
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

    if (
        data.experience_ids
        or data.education_ids
        or data.skill_ids
        or data.project_ids
        or data.certification_ids
    ):
        profile = await get_profile_or_404(db, user_id)
    if data.experience_ids:
        items = await _resolve_selected(db, profile.id, data.experience_ids, WorkExperience)
        facet.selected_experiences = items
    if data.education_ids:
        items = await _resolve_selected(db, profile.id, data.education_ids, Education)
        facet.selected_educations = items
    if data.skill_ids:
        items = await _resolve_selected(db, profile.id, data.skill_ids, Skill)
        facet.selected_skills = items
    if data.project_ids:
        items = await _resolve_selected(db, profile.id, data.project_ids, Project)
        facet.selected_projects = items
    if data.certification_ids:
        items = await _resolve_selected(db, profile.id, data.certification_ids, Certification)
        facet.selected_certifications = items

    await db.commit()
    return await _load_facet(db, user_id, facet.id)


async def update_facet(
    db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID, data: FacetUpdate
) -> Facet:
    facet = await _load_facet(db, user_id, facet_id)

    scalar_fields = data.model_dump(
        exclude={
            "experience_ids",
            "education_ids",
            "skill_ids",
            "project_ids",
            "certification_ids",
        },
        exclude_unset=True,
    )
    for field, value in scalar_fields.items():
        setattr(facet, field, value)

    m2m_fields = [
        data.experience_ids,
        data.education_ids,
        data.skill_ids,
        data.project_ids,
        data.certification_ids,
    ]
    if any(x is not None for x in m2m_fields):
        profile = await get_profile_or_404(db, user_id)
    if data.experience_ids is not None:
        items = await _resolve_selected(db, profile.id, data.experience_ids, WorkExperience)
        facet.selected_experiences = items
    if data.education_ids is not None:
        items = await _resolve_selected(db, profile.id, data.education_ids, Education)
        facet.selected_educations = items
    if data.skill_ids is not None:
        items = await _resolve_selected(db, profile.id, data.skill_ids, Skill)
        facet.selected_skills = items
    if data.project_ids is not None:
        items = await _resolve_selected(db, profile.id, data.project_ids, Project)
        facet.selected_projects = items
    if data.certification_ids is not None:
        items = await _resolve_selected(db, profile.id, data.certification_ids, Certification)
        facet.selected_certifications = items

    await db.commit()
    return await _load_facet(db, user_id, facet.id)


async def delete_facet(db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID) -> None:
    facet = await _load_facet(db, user_id, facet_id)
    await db.delete(facet)
    await db.commit()
