from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.public import PublicFacetResponse
from app.services import public as public_service

router = APIRouter(tags=["public"])


@router.get("/{slug}", response_model=PublicFacetResponse)
async def get_public_facet(
    slug: str,
    db: AsyncSession = Depends(get_db_session),
):
    return await public_service.get_published_facet(db, slug)
