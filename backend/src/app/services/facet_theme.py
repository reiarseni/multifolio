import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import Facet, FacetThemeConfig
from app.schemas.theme import FacetThemeConfigUpdate
from app.services.themes import get_theme_or_404

VALID_WEB_LAYOUTS = {"single-column", "sidebar", "modular"}
VALID_PDF_LAYOUTS = {"classic", "two-column", "compact"}
VALID_PHOTO_SHAPES = {"circle", "rounded", "square"}


async def update_facet_theme_config(
    db: AsyncSession,
    user_id: uuid.UUID,
    facet_id: uuid.UUID,
    data: FacetThemeConfigUpdate,
) -> FacetThemeConfig:
    # Verify facet ownership
    facet_result = await db.execute(
        select(Facet)
        .where(Facet.id == facet_id, Facet.user_id == user_id)
        .options(selectinload(Facet.theme_config).selectinload(FacetThemeConfig.theme))
    )
    facet = facet_result.scalar_one_or_none()
    if not facet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faceta no encontrada")

    config = facet.theme_config
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Configuración de tema no encontrada"
        )

    if data.theme_id is not None:
        await get_theme_or_404(db, data.theme_id)
        config.theme_id = data.theme_id

    if data.theme_overrides is not None:
        config.theme_overrides = data.theme_overrides

    if data.web_layout is not None:
        if data.web_layout not in VALID_WEB_LAYOUTS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "web_layout inválido. Valores aceptados: "
                    + ", ".join(sorted(VALID_WEB_LAYOUTS))
                ),
            )
        config.web_layout = data.web_layout

    if data.pdf_layout is not None:
        if data.pdf_layout not in VALID_PDF_LAYOUTS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "pdf_layout inválido. Valores aceptados: "
                    + ", ".join(sorted(VALID_PDF_LAYOUTS))
                ),
            )
        config.pdf_layout = data.pdf_layout

    if data.show_photo_web is not None:
        config.show_photo_web = data.show_photo_web

    if data.show_photo_pdf is not None:
        config.show_photo_pdf = data.show_photo_pdf

    if data.photo_shape is not None:
        if data.photo_shape not in VALID_PHOTO_SHAPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "photo_shape inválido. Valores aceptados: "
                    + ", ".join(sorted(VALID_PHOTO_SHAPES))
                ),
            )
        config.photo_shape = data.photo_shape

    await db.commit()

    result = await db.execute(
        select(FacetThemeConfig)
        .where(FacetThemeConfig.facet_id == facet_id)
        .options(selectinload(FacetThemeConfig.theme))
    )
    return result.scalar_one()
