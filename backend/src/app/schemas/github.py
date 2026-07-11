import uuid
from datetime import datetime

from pydantic import BaseModel


class GitHubRepoCreate(BaseModel):
    repo_url: str


class GitHubRepoResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    repo_url: str
    name: str
    full_name: str
    description: str | None
    stars: int
    forks: int
    language: str | None
    languages: dict | None
    last_commit: datetime | None
    is_archived: bool
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
