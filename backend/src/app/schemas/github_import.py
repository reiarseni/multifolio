import uuid

from pydantic import BaseModel


class AIGeneratedProject(BaseModel):
    repo_id: uuid.UUID
    title: str
    description: str | None = None
    markdown_content: str | None = None
    github_url: str


class ImportAnalyzeRequest(BaseModel):
    repo_ids: list[uuid.UUID]
    facet_id: uuid.UUID


class ImportAnalyzeResponse(BaseModel):
    projects: list[AIGeneratedProject]


class ImportConfirmRequest(BaseModel):
    facet_id: uuid.UUID
    projects: list[AIGeneratedProject]


class ImportConfirmResponse(BaseModel):
    message: str
    count: int
    project_ids: list[uuid.UUID]
