import copy

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import BaseProfile, Facet, FacetThemeConfig, Project
from app.models.user import User


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
            selectinload(Facet.theme_config).selectinload(FacetThemeConfig.theme),
            selectinload(Facet.open_to_role),
        )
    )
    facet = result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    profile_result = await db.execute(
        select(BaseProfile).where(BaseProfile.user_id == facet.user_id)
    )
    profile = profile_result.scalar_one_or_none()

    user_result = await db.execute(select(User).where(User.id == facet.user_id))
    user = user_result.scalar_one_or_none()

    # Merge tokens with overrides
    theme_tokens: dict = {}
    if facet.theme_config and facet.theme_config.theme:
        theme_tokens = copy.deepcopy(facet.theme_config.theme.tokens or {})
        if facet.theme_config.theme_overrides:
            theme_tokens.update(facet.theme_config.theme_overrides)

    return {
        "slug": facet.slug,
        "title": facet.title,
        "bio": facet.bio,
        "meta_title": facet.meta_title,
        "meta_description": facet.meta_description,
        "pdf_template": facet.pdf_template,
        "pdf_layout": facet.theme_config.pdf_layout if facet.theme_config else "classic",
        "web_layout": facet.theme_config.web_layout if facet.theme_config else "single-column",
        "show_photo_web": facet.theme_config.show_photo_web if facet.theme_config else True,
        "show_photo_pdf": facet.theme_config.show_photo_pdf if facet.theme_config else True,
        "photo_shape": facet.theme_config.photo_shape if facet.theme_config else "circle",
        "theme_tokens": theme_tokens,
        "full_name": profile.full_name if profile else "",
        "email": user.email if user else "",
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
        "open_to_role": facet.open_to_role,
    }
