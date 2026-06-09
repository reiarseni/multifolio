from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import BaseProfile, Facet, Project


async def get_published_facet(db: AsyncSession, slug: str) -> dict:
    result = await db.execute(
        select(Facet)
        .where(Facet.slug == slug, Facet.is_published.is_(True))
        .options(
            selectinload(Facet.selected_experiences),
            selectinload(Facet.selected_educations),
            selectinload(Facet.selected_skills),
            selectinload(Facet.selected_certifications),
            selectinload(Facet.selected_projects).selectinload(Project.images),
        )
    )
    facet = result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    profile_result = await db.execute(
        select(BaseProfile).where(BaseProfile.user_id == facet.user_id)
    )
    profile = profile_result.scalar_one_or_none()

    return {
        "slug": facet.slug,
        "title": facet.title,
        "bio": facet.bio,
        "meta_title": facet.meta_title,
        "meta_description": facet.meta_description,
        "pdf_template": facet.pdf_template,
        "full_name": profile.full_name if profile else "",
        "email": profile.email if profile else "",
        "phone": profile.phone if profile else None,
        "photo_url": profile.photo_url if profile else None,
        "website": profile.website if profile else None,
        "linkedin_url": profile.linkedin_url if profile else None,
        "github_url": profile.github_url if profile else None,
        "experiences": facet.selected_experiences or [],
        "educations": facet.selected_educations or [],
        "skills": facet.selected_skills or [],
        "certifications": facet.selected_certifications or [],
        "projects": facet.selected_projects or [],
    }
