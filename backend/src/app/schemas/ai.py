from __future__ import annotations

import uuid

from pydantic import BaseModel


class AISuggestionRequest(BaseModel):
    section_id: uuid.UUID


class AIHeadlineRequest(BaseModel):
    target_role: str


class AISuggestionResponse(BaseModel):
    original: str
    suggested: str
    changes_summary: str


class AIHeadlineResponse(BaseModel):
    title: str
    bio: str


class AIBulkSuggestionResponse(BaseModel):
    suggestions: list[AISuggestionResponse]


class ApplySuggestionRequest(BaseModel):
    section_id: uuid.UUID
    suggestion: str
