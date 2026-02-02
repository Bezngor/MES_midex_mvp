"""add order_snapshots table for tracking order changes

Revision ID: 20260202000001
Revises: 20260130100002
Create Date: 2026-02-02 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20260202000001'
down_revision = '20260130100002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'order_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_number', sa.String(), nullable=False),
        sa.Column('product_id', sa.String(), nullable=False),
        sa.Column('quantity', sa.Numeric(10, 2), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('order_type', sa.String(50), nullable=False),
        sa.Column('priority', sa.String(50), nullable=True),
        sa.Column('source_status', sa.String(50), nullable=True),
        sa.Column('parent_order_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('source_order_ids', postgresql.JSONB(), nullable=True),
        sa.Column('is_consolidated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('snapshot_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('snapshot_type', sa.String(50), nullable=False, server_default='MANUAL'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('full_snapshot', postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['manufacturing_orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_order_snapshots_order_id', 'order_snapshots', ['order_id'])
    op.create_index('idx_order_snapshots_order_number', 'order_snapshots', ['order_number'])
    op.create_index('idx_order_snapshots_date', 'order_snapshots', ['snapshot_date'])
    op.create_index('idx_order_snapshots_type', 'order_snapshots', ['snapshot_type'])
    op.create_index('idx_order_snapshots_order_date', 'order_snapshots', ['order_id', 'snapshot_date'])


def downgrade() -> None:
    op.drop_index('idx_order_snapshots_order_date', table_name='order_snapshots')
    op.drop_index('idx_order_snapshots_type', table_name='order_snapshots')
    op.drop_index('idx_order_snapshots_date', table_name='order_snapshots')
    op.drop_index('idx_order_snapshots_order_number', table_name='order_snapshots')
    op.drop_index('idx_order_snapshots_order_id', table_name='order_snapshots')
    op.drop_table('order_snapshots')
