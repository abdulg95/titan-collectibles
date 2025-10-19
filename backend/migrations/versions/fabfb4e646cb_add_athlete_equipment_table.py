"""add_athlete_equipment_table

Revision ID: fabfb4e646cb
Revises: 45658664cca1
Create Date: 2025-10-14 02:30:32.146533

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fabfb4e646cb'
down_revision = '45658664cca1'
branch_labels = None
depends_on = None


def upgrade():
    # Check if table already exists before creating it
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'athlete_equipment' not in tables:
        op.create_table('athlete_equipment',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('athlete_id', sa.UUID(), nullable=False),
            sa.Column('category', sa.String(), nullable=False),
            sa.Column('brand', sa.String(), nullable=True),
            sa.Column('model', sa.String(), nullable=True),
            sa.Column('url', sa.Text(), nullable=True),
            sa.Column('notes', sa.String(), nullable=True),
            sa.Column('display_order', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['athlete_id'], ['athletes.id'], ),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade():
    op.drop_table('athlete_equipment')
