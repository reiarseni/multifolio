import uuid

from fastapi import HTTPException, status
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import (
    BaseProfile,
    Certification,
    Education,
    Facet,
    FacetThemeConfig,
    Project,
    Skill,
    Theme,
    WorkExperience,
    facet_certifications,
    facet_educations,
    facet_projects,
    facet_skills,
    facet_work_experiences,
)
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


async def _resolve_ids(
    db: AsyncSession,
    profile_id: uuid.UUID,
    item_ids: list[uuid.UUID],
    model,
) -> list[uuid.UUID]:
    """Returns the IDs of items that belong to this profile, filtering out invalid ones."""
    if not item_ids:
        return []
    result = await db.execute(
        select(model.id).where(
            model.id.in_(item_ids),
            model.profile_id == profile_id,
        )
    )
    return [row[0] for row in result.all()]


def _facet_options():
    return [
        selectinload(Facet.selected_experiences),
        selectinload(Facet.selected_educations),
        selectinload(Facet.selected_skills),
        selectinload(Facet.selected_certifications),
        selectinload(Facet.selected_projects),
        selectinload(Facet.theme_config).selectinload(FacetThemeConfig.theme),
    ]


async def _load_facet(db: AsyncSession, user_id: uuid.UUID, facet_id: uuid.UUID) -> Facet:
    result = await db.execute(
        select(Facet)
        .where(Facet.id == facet_id, Facet.user_id == user_id)
        .options(*_facet_options())
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
        .options(*_facet_options())
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

    _profile_res = await db.execute(select(BaseProfile).where(BaseProfile.user_id == user_id))
    profile = _profile_res.scalar_one_or_none()

    if profile:
        # Use direct inserts to association tables to avoid lazy-loading back-references
        # (ORM relationship assignment would trigger back-ref load on persistent objects)

        if data.experience_ids:
            valid_ids = await _resolve_ids(db, profile.id, data.experience_ids, WorkExperience)
            if valid_ids:
                await db.execute(
                    insert(facet_work_experiences),
                    [{"facet_id": facet.id, "work_experience_id": eid} for eid in valid_ids],
                )

        if data.education_ids:
            valid_ids = await _resolve_ids(db, profile.id, data.education_ids, Education)
            if valid_ids:
                await db.execute(
                    insert(facet_educations),
                    [{"facet_id": facet.id, "education_id": eid} for eid in valid_ids],
                )

        # Pre-include transversal skills union with explicit skill_ids
        transversal_result = await db.execute(
            select(Skill.id).where(Skill.profile_id == profile.id, Skill.is_transversal.is_(True))
        )
        transversal_ids = {row[0] for row in transversal_result.all()}

        explicit_ids: set[uuid.UUID] = set()
        if data.skill_ids:
            explicit_id_rows = await _resolve_ids(db, profile.id, data.skill_ids, Skill)
            explicit_ids = set(explicit_id_rows)

        all_skill_ids = list(transversal_ids | explicit_ids)
        if all_skill_ids:
            await db.execute(
                insert(facet_skills),
                [{"facet_id": facet.id, "skill_id": sid} for sid in all_skill_ids],
            )

        if data.certification_ids:
            valid_ids = await _resolve_ids(db, profile.id, data.certification_ids, Certification)
            if valid_ids:
                await db.execute(
                    insert(facet_certifications),
                    [{"facet_id": facet.id, "certification_id": cid} for cid in valid_ids],
                )

        if data.project_ids:
            valid_ids = await _resolve_ids(db, profile.id, data.project_ids, Project)
            if valid_ids:
                await db.execute(
                    insert(facet_projects),
                    [{"facet_id": facet.id, "project_id": pid} for pid in valid_ids],
                )

    # Create default FacetThemeConfig using the minimal theme
    minimal_theme_result = await db.execute(
        select(Theme).where(Theme.name == "minimal", Theme.owner_id.is_(None))
    )
    minimal_theme = minimal_theme_result.scalar_one_or_none()
    if minimal_theme:
        config = FacetThemeConfig(
            facet_id=facet.id,
            theme_id=minimal_theme.id,
        )
        db.add(config)

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
