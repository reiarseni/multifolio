"""fix facet models — slug validation, back_populates, certifications, unique email

Revision ID: 4cb2bcd314b4
Revises: 4cb2bcd314b3
Create Date: 2026-06-01 18:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '4cb2bcd314b4'
down_revision: str | Sequence[str] | None = '4cb2bcd314b3'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create facet_certifications junction table
    op.create_table('facet_certifications',
        sa.Column('facet_id', sa.UUID(), nullable=False),
        sa.Column('certification_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['certification_id'], ['certifications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['facet_id'], ['facets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('facet_id', 'certification_id')
    )

    # Add updated_at to skills
    op.add_column('skills',
        sa.Column('updated_at', sa.DateTime(timezone=True),
                   server_default=sa.text('now()'), nullable=False)
    )

    # Add updated_at to certifications
    op.add_column('certifications',
        sa.Column('updated_at', sa.DateTime(timezone=True),
                   server_default=sa.text('now()'), nullable=False)
    )

    # Add unique constraint on base_profiles.email
    op.create_unique_constraint('uq_base_profile_email', 'base_profiles', ['email'])


def downgrade() -> None:
    op.drop_constraint('uq_base_profile_email', 'base_profiles', type_='unique')
    op.drop_column('certifications', 'updated_at')
    op.drop_column('skills', 'updated_at')
    op.drop_table('facet_certifications')
