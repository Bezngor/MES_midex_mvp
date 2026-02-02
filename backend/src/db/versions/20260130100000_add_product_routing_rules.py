"""add product_routing_rules table

Revision ID: 20260130100000
Revises: 20260130000001
Create Date: 2026-01-30 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20260130100000'
down_revision = '20260130000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'product_routing_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('product_code', sa.String(), nullable=False),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('priority_order', sa.Integer(), nullable=False),
        sa.Column('min_quantity', sa.Integer(), nullable=True),
        sa.Column('max_quantity', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['work_center_id'], ['work_centers.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_product_routing_rules_product_code', 'product_routing_rules', ['product_code'])
    op.create_index('idx_product_routing_rules_work_center_id', 'product_routing_rules', ['work_center_id'])
    op.create_unique_constraint(
        'uq_product_routing_rules_product_work_center',
        'product_routing_rules',
        ['product_code', 'work_center_id'],
    )


def downgrade() -> None:
    op.drop_table('product_routing_rules')
