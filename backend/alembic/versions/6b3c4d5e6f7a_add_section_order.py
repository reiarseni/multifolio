"""add_section_order

Revision ID: 6b3c4d5e6f7a
Revises: 5a1b2c3d4e5f
Create Date: 2026-06-13 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "6b3c4d5e6f7a"
down_revision: str | None = "5a1b2c3d4e5f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    default_order = '["experiencias", "habilidades", "estudios", "proyectos", "certificaciones"]'
    op.add_column(
        "facet_theme_configs",
        sa.Column(
            "section_order",
            sa.JSON,
            nullable=True,
            server_default=default_order,
        ),
    )


def downgrade() -> None:
    op.drop_column("facet_theme_configs", "section_order")
