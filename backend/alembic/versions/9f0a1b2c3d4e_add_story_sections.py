"""add_story_sections

Revision ID: 9f0a1b2c3d4e
Revises: 8e9f0a1b2c3d
Create Date: 2026-07-11 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "9f0a1b2c3d4e"
down_revision: str | None = "8e9f0a1b2c3d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "story_sections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "facet_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("facets.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("section_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("media_urls", postgresql.JSON, nullable=True),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_visible", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("story_sections")
