"""add_review_link_security

Revision ID: a1b2c3d4e5f6
Revises: 9f0a1b2c3d4e
Create Date: 2026-07-16 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "9f0a1b2c3d4e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("review_links", sa.Column("label", sa.String(255), nullable=True))
    op.add_column("review_links", sa.Column("password_hash", sa.String(255), nullable=True))
    op.add_column("review_links", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("review_links", sa.Column("single_use", sa.Boolean, nullable=False, server_default="false"))
    op.add_column("review_links", sa.Column("used_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("review_links", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))


def downgrade() -> None:
    op.drop_column("review_links", "updated_at")
    op.drop_column("review_links", "used_at")
    op.drop_column("review_links", "single_use")
    op.drop_column("review_links", "expires_at")
    op.drop_column("review_links", "password_hash")
    op.drop_column("review_links", "label")
