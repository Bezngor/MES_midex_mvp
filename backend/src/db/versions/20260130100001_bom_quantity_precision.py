"""increase BOM quantity precision for small proportions (e.g. 0.00002)

Revision ID: 20260130100001
Revises: 20260130100000
Create Date: 2026-01-30 10:00:01.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '20260130100001'
down_revision = '20260130100000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'bill_of_materials',
        'quantity',
        existing_type=sa.Numeric(10, 4),
        type_=sa.Numeric(18, 14),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'bill_of_materials',
        'quantity',
        existing_type=sa.Numeric(18, 14),
        type_=sa.Numeric(10, 4),
        existing_nullable=False,
    )
