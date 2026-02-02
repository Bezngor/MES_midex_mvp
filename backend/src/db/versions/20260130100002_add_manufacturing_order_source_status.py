"""add manufacturing_orders.source_status for 1C status (Отгрузить / Образец / В работе)

Revision ID: 20260130100002
Revises: 20260130100001
Create Date: 2026-01-30 10:00:02.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '20260130100002'
down_revision = '20260130100001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'manufacturing_orders',
        sa.Column('source_status', sa.String(50), nullable=True),
    )
    op.create_index('idx_orders_source_status', 'manufacturing_orders', ['source_status'])


def downgrade() -> None:
    op.drop_index('idx_orders_source_status', table_name='manufacturing_orders')
    op.drop_column('manufacturing_orders', 'source_status')
