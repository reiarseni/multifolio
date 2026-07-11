"""add_social_auth_fields

Revision ID: 7c4d5e6f7a8b
Revises: 6b3c4d5e6f7a
Create Date: 2026-07-11 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "7c4d5e6f7a8b"
down_revision: str | None = "6b3c4d5e6f7a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("auth_provider", sa.String(50), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("provider_user_id", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "provider_user_id")
    op.drop_column("users", "auth_provider")
