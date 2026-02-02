"""add composite index on order_number and order_type for order_snapshots

Revision ID: 20260202000002
Revises: 20260202000001
Create Date: 2026-02-02 00:00:02.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '20260202000002'
down_revision = '20260202000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем составной индекс для эффективного поиска по бизнес-ключу (order_number + order_type)
    op.create_index(
        'idx_order_snapshots_order_number_type',
        'order_snapshots',
        ['order_number', 'order_type']
    )


def downgrade() -> None:
    op.drop_index('idx_order_snapshots_order_number_type', table_name='order_snapshots')
