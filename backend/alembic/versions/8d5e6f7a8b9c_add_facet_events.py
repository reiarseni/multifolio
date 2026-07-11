"""add_facet_events

Revision ID: 8d5e6f7a8b9c
Revises: 6b3c4d5e6f7a
Create Date: 2026-07-11 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "8d5e6f7a8b9c"
down_revision: str | None = "6b3c4d5e6f7a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "facet_events",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "facet_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("facets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("visitor_ip_hash", sa.String(64), nullable=False),
        sa.Column("referrer", sa.Text, nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("time_on_page", sa.Integer, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_facet_events_facet_id", "facet_events", ["facet_id"])
    op.create_index("ix_facet_events_created_at", "facet_events", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_facet_events_created_at", table_name="facet_events")
    op.drop_index("ix_facet_events_facet_id", table_name="facet_events")
    op.drop_table("facet_events")
