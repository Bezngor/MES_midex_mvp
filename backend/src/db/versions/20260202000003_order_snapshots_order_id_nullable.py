"""order_snapshots.order_id nullable and ON DELETE SET NULL

При удалении заказа (manufacturing_orders) снимки сохраняются с order_id=NULL,
чтобы можно было выявлять удалённые заказы по order_number.

Revision ID: 20260202000003
Revises: 20260202000002
Create Date: 2026-02-02 00:00:03.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20260202000003'
down_revision = '20260202000002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Удаляем внешний ключ (без CASCADE, просто снимаем ограничение)
    op.drop_constraint(
        'order_snapshots_order_id_fkey',
        'order_snapshots',
        type_='foreignkey'
    )
    # 2. Делаем order_id nullable
    op.alter_column(
        'order_snapshots',
        'order_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True
    )
    # 3. Добавляем внешний ключ с ON DELETE SET NULL
    op.create_foreign_key(
        'order_snapshots_order_id_fkey',
        'order_snapshots',
        'manufacturing_orders',
        ['order_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint(
        'order_snapshots_order_id_fkey',
        'order_snapshots',
        type_='foreignkey'
    )
    op.alter_column(
        'order_snapshots',
        'order_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False
    )
    op.create_foreign_key(
        'order_snapshots_order_id_fkey',
        'order_snapshots',
        'manufacturing_orders',
        ['order_id'],
        ['id']
    )
