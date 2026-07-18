from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.profile import Facet


class FacetAnalysis(Base):
    __tablename__ = "facet_analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("facets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    job_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    skills_score: Mapped[float] = mapped_column(Float, nullable=False)
    experience_score: Mapped[float] = mapped_column(Float, nullable=False)
    stack_score: Mapped[float] = mapped_column(Float, nullable=False)
    tone_score: Mapped[float] = mapped_column(Float, nullable=False)
    gaps: Mapped[dict] = mapped_column(JSON, nullable=False, default=[])
    suggestions: Mapped[dict] = mapped_column(JSON, nullable=False, default=[])
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    facet: Mapped[Facet] = relationship(back_populates="analyses")
