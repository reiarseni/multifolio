"""add_notifications

Revision ID: 9f0a1b2c3d4e
Revises: 8e9f0a1b2c3d
Create Date: 2026-07-18 15:00:00.000000

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
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "facet_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("facets.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("referrer_domain", sa.String(500), nullable=True),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("extra_data", postgresql.JSON, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("notifications")
