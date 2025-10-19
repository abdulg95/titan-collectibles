"""add_athlete_qualifications_table

Revision ID: 410df16580e8
Revises: fabfb4e646cb
Create Date: 2025-10-14 02:36:03.146872

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '410df16580e8'
down_revision = 'fabfb4e646cb'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('athlete_qualifications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('athlete_id', sa.UUID(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('score', sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column('event', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['athlete_id'], ['athletes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('athlete_qualifications')
