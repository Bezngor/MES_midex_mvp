"""add batch posted_to_inventory_at

Revision ID: 20260130000001
Revises: 20260126000001
Create Date: 2026-01-30 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260130000001'
down_revision = '20260126000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'batches',
        sa.Column('posted_to_inventory_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('batches', 'posted_to_inventory_at')
