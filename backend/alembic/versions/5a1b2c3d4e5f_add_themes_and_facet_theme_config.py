"""add_themes_and_facet_theme_config

Revision ID: 5a1b2c3d4e5f
Revises: 4cb2bcd314b4
Create Date: 2026-06-10 16:00:00.000000

"""

import json
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "5a1b2c3d4e5f"
down_revision: str | Sequence[str] | None = "4cb2bcd314b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MINIMAL_THEME_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
FORMAL_THEME_ID = "c273c882-ef8b-4a4a-862c-cd5a2e9e6b7c"
BOLD_THEME_ID = "9a8b7c6d-5e4f-3a2b-1c0d-e9f8a7b6c5d4"

MINIMAL_TOKENS = {
    "color": {
        "primary": "#2c2c2c",
        "background": "#ffffff",
        "surface": "#f8f8f8",
        "text_heading": "#1a1a1a",
        "text_body": "#333333",
        "text_muted": "#888888",
        "border": "#e0e0e0",
        "accent": "#4a90e2",
    },
    "typography": {
        "font_heading": "Georgia, serif",
        "font_body": "system-ui, sans-serif",
        "size_base": "1rem",
    },
    "spacing": {"section_gap": "2rem", "item_gap": "1rem"},
    "shape": {"radius_md": "0.25rem"},
}

FORMAL_TOKENS = {
    "color": {
        "primary": "#1a3a5c",
        "background": "#ffffff",
        "surface": "#f5f7fa",
        "text_heading": "#0d2137",
        "text_body": "#2d2d2d",
        "text_muted": "#6b7280",
        "border": "#d1d9e0",
        "accent": "#2563eb",
    },
    "typography": {
        "font_heading": "'Times New Roman', Times, serif",
        "font_body": "'Gill Sans', Calibri, sans-serif",
        "size_base": "1rem",
    },
    "spacing": {"section_gap": "2.5rem", "item_gap": "1.25rem"},
    "shape": {"radius_md": "0.125rem"},
}

BOLD_TOKENS = {
    "color": {
        "primary": "#7c3aed",
        "background": "#0f0f0f",
        "surface": "#1a1a1a",
        "text_heading": "#ffffff",
        "text_body": "#e5e5e5",
        "text_muted": "#9ca3af",
        "border": "#2d2d2d",
        "accent": "#f59e0b",
    },
    "typography": {
        "font_heading": "'Inter', 'Helvetica Neue', sans-serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "size_base": "1rem",
    },
    "spacing": {"section_gap": "2rem", "item_gap": "1rem"},
    "shape": {"radius_md": "0.75rem"},
}


def upgrade() -> None:
    op.create_table(
        "themes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("tokens", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "facet_theme_configs",
        sa.Column("facet_id", sa.UUID(), nullable=False),
        sa.Column("theme_id", sa.UUID(), nullable=False),
        sa.Column("theme_overrides", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column(
            "web_layout", sa.String(length=50),
            nullable=False, server_default="single-column",
        ),
        sa.Column("pdf_layout", sa.String(length=50), nullable=False, server_default="classic"),
        sa.Column("show_photo_web", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("show_photo_pdf", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("photo_shape", sa.String(length=50), nullable=False, server_default="circle"),
        sa.ForeignKeyConstraint(["facet_id"], ["facets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["theme_id"], ["themes.id"]),
        sa.PrimaryKeyConstraint("facet_id"),
    )

    # Seed predefined themes
    for theme_id, name, tokens in [
        (MINIMAL_THEME_ID, "minimal", MINIMAL_TOKENS),
        (FORMAL_THEME_ID, "formal", FORMAL_TOKENS),
        (BOLD_THEME_ID, "bold", BOLD_TOKENS),
    ]:
        op.execute(
            sa.text(
                "INSERT INTO themes (id, owner_id, name, tokens, is_public) "
                "VALUES (CAST(:tid AS uuid), NULL, :name, CAST(:tokens AS jsonb), true)"
            ).bindparams(
                sa.bindparam("tid"),
                sa.bindparam("name"),
                sa.bindparam("tokens"),
                tid=theme_id,
                name=name,
                tokens=json.dumps(tokens),
            )
        )

    # Backfill: create default theme_config for all existing facets
    op.execute(
        sa.text(
            "INSERT INTO facet_theme_configs "
            "(facet_id, theme_id, web_layout, pdf_layout, "
            "show_photo_web, show_photo_pdf, photo_shape) "
            "SELECT id, CAST(:theme_id AS uuid), 'single-column', 'classic', true, true, 'circle' "
            "FROM facets "
            "WHERE NOT EXISTS ("
            "  SELECT 1 FROM facet_theme_configs WHERE facet_theme_configs.facet_id = facets.id"
            ")"
        ).bindparams(sa.bindparam("theme_id"), theme_id=MINIMAL_THEME_ID)
    )


def downgrade() -> None:
    op.drop_table("facet_theme_configs")
    op.drop_table("themes")
