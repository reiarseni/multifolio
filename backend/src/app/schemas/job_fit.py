from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class GapItem(BaseModel):
    category: str
    description: str
    severity: str  # high, medium, low
    suggestion: str


class ReorderSuggestion(BaseModel):
    rationale: str
    proposed_order: list[str]


class JobFitResponse(BaseModel):
    id: uuid.UUID
    job_title: str | None
    job_company: str | None
    overall_score: float
    skills_score: float
    experience_score: float
    stack_score: float
    tone_score: float
    gaps: list[GapItem]
    suggestions: list[str]
    reorder_suggestion: ReorderSuggestion | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobFitHistoryItem(BaseModel):
    id: uuid.UUID
    job_title: str | None
    job_company: str | None
    overall_score: float
    skills_score: float
    experience_score: float
    stack_score: float
    tone_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class JobFitHistoryResponse(BaseModel):
    analyses: list[JobFitHistoryItem]


class JobFitDeleteResponse(BaseModel):
    message: str


class JobFitRequest(BaseModel):
    job_posting: str = Field(..., max_length=10000)


class DimensionScores(BaseModel):
    skills: float
    experience: float
    stack: float
    tone: float
