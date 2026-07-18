from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.job_fit import (
    JobFitDeleteResponse,
    JobFitHistoryItem,
    JobFitHistoryResponse,
    JobFitRequest,
    JobFitResponse,
)
from app.services import job_fit_service

router = APIRouter(prefix="/facets", tags=["job-fit"])


@router.post("/{facet_id}/job-fit", response_model=JobFitResponse)
async def analyze_facet_job_fit(
    facet_id: uuid.UUID,
    body: JobFitRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await job_fit_service.analyze_facet_fit(
        db=db,
        facet_id=facet_id,
        job_posting=body.job_posting,
        current_user_id=current_user.id,
    )


@router.get("/{facet_id}/job-fit/history", response_model=JobFitHistoryResponse)
async def get_job_fit_history(
    facet_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    analyses = await job_fit_service.get_analysis_history(
        db=db,
        facet_id=facet_id,
        current_user_id=current_user.id,
    )
    return JobFitHistoryResponse(
        analyses=[JobFitHistoryItem.model_validate(a) for a in analyses]
    )


@router.delete("/job-fit/{analysis_id}", response_model=JobFitDeleteResponse)
async def delete_job_fit_analysis(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await job_fit_service.delete_analysis(
        db=db,
        analysis_id=analysis_id,
        current_user_id=current_user.id,
    )
    return JobFitDeleteResponse(message="Analysis deleted successfully")
