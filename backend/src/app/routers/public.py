from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.public import PublicFacetResponse
from app.services import public as public_service
from app.services.pdf_generator import generate_facet_pdf

router = APIRouter(tags=["public"])


@router.get("/{slug}", response_model=PublicFacetResponse)
async def get_public_facet(
    slug: str,
    db: AsyncSession = Depends(get_db_session),
):
    return await public_service.get_published_facet(db, slug)


@router.get("/{slug}/pdf")
async def get_public_facet_pdf(
    slug: str,
    db: AsyncSession = Depends(get_db_session),
):
    pdf_bytes = await generate_facet_pdf(db, slug)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{slug}.pdf"'},
    )
