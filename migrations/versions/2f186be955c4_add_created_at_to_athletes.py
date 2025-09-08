"""add created_at to athletes

Revision ID: 2f186be955c4
Revises: 4312a61d695d
Create Date: 2025-09-06 17:55:33.261249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f186be955c4'
down_revision = '4312a61d695d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'athletes',
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
    )
    # optional: remove default going forward, if you only wanted it for backfill
    op.alter_column('athletes', 'created_at', server_default=None)

def downgrade():
    op.drop_column('athletes', 'created_at')