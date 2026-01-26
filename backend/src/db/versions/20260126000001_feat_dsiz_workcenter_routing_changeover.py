"""feat: dsiz workcenter_routing changeover_matrix workforce_requirements

Revision ID: 20260126000001
Revises: 20260114171052
Create Date: 2026-01-26 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260126000001'
down_revision = '20260114171052'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Добавить DSIZ таблицы: work_center_modes, product_work_center_routing, changeover_matrix, base_rates, workforce_requirements."""
    
    # 1. dsiz_work_center_modes - Режимы реактора
    op.create_table(
        'dsiz_work_center_modes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mode_name', sa.String(length=50), nullable=False),
        sa.Column('min_load_kg', sa.Numeric(10, 2), nullable=False),
        sa.Column('max_load_kg', sa.Numeric(10, 2), nullable=False),
        sa.Column('cycle_duration_hours', sa.Integer(), nullable=False),
        sa.Column('max_cycles_per_shift', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['work_center_id'], ['work_centers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('work_center_id', 'mode_name', name='uq_dsiz_wc_modes_wc_mode')
    )
    op.create_index('idx_dsiz_wc_modes_work_center', 'dsiz_work_center_modes', ['work_center_id'])
    
    # 2. dsiz_changeover_matrix - Матрица совместимости продуктов
    op.create_table(
        'dsiz_changeover_matrix',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('from_compatibility_group', sa.String(length=100), nullable=False),
        sa.Column('to_compatibility_group', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),  # 'COMPATIBLE', 'INCOMPATIBLE', 'UNIVERSAL'
        sa.Column('setup_time_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('from_compatibility_group', 'to_compatibility_group', name='uq_dsiz_changeover_from_to')
    )
    op.create_index('idx_dsiz_changeover_from', 'dsiz_changeover_matrix', ['from_compatibility_group'])
    op.create_index('idx_dsiz_changeover_to', 'dsiz_changeover_matrix', ['to_compatibility_group'])
    
    # 3. dsiz_product_work_center_routing - Маршрутизация продуктов по рабочим центрам
    op.create_table(
        'dsiz_product_work_center_routing',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_sku', sa.String(length=50), nullable=False),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_allowed', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('min_quantity_for_wc', sa.Integer(), nullable=True),
        sa.Column('priority_order', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['work_center_id'], ['work_centers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_sku', 'work_center_id', name='uq_dsiz_routing_product_wc')
    )
    op.create_index('idx_dsiz_routing_product', 'dsiz_product_work_center_routing', ['product_sku'])
    op.create_index('idx_dsiz_routing_work_center', 'dsiz_product_work_center_routing', ['work_center_id'])
    
    # 4. dsiz_base_rates - Базовые скорости операций
    op.create_table(
        'dsiz_base_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_sku', sa.String(length=50), nullable=False),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('base_rate_units_per_hour', sa.Numeric(10, 2), nullable=False),
        sa.Column('is_human_dependent', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['work_center_id'], ['work_centers.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_dsiz_base_rates_product', 'dsiz_base_rates', ['product_sku'])
    op.create_index('idx_dsiz_base_rates_work_center', 'dsiz_base_rates', ['work_center_id'])
    
    # 5. dsiz_workforce_requirements - Нормы укомплектованности персонала
    op.create_table(
        'dsiz_workforce_requirements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('role_name', sa.String(length=50), nullable=False),  # 'OPERATOR', 'PACKER'
        sa.Column('required_count', sa.Integer(), nullable=False),
        sa.Column('is_mandatory', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('min_count_for_degraded_mode', sa.Integer(), nullable=True),
        sa.Column('degradation_factor', sa.Numeric(3, 2), nullable=True),  # 0.5 при 3/4 операторах
        sa.ForeignKeyConstraint(['work_center_id'], ['work_centers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('work_center_id', 'role_name', name='uq_dsiz_workforce_wc_role')
    )
    op.create_index('idx_dsiz_workforce_work_center', 'dsiz_workforce_requirements', ['work_center_id'])
    op.create_index('idx_dsiz_workforce_role', 'dsiz_workforce_requirements', ['role_name'])


def downgrade() -> None:
    """Откатить изменения: удалить DSIZ таблицы."""
    op.drop_index('idx_dsiz_workforce_role', table_name='dsiz_workforce_requirements')
    op.drop_index('idx_dsiz_workforce_work_center', table_name='dsiz_workforce_requirements')
    op.drop_table('dsiz_workforce_requirements')
    
    op.drop_index('idx_dsiz_base_rates_work_center', table_name='dsiz_base_rates')
    op.drop_index('idx_dsiz_base_rates_product', table_name='dsiz_base_rates')
    op.drop_table('dsiz_base_rates')
    
    op.drop_index('idx_dsiz_routing_work_center', table_name='dsiz_product_work_center_routing')
    op.drop_index('idx_dsiz_routing_product', table_name='dsiz_product_work_center_routing')
    op.drop_table('dsiz_product_work_center_routing')
    
    op.drop_index('idx_dsiz_changeover_to', table_name='dsiz_changeover_matrix')
    op.drop_index('idx_dsiz_changeover_from', table_name='dsiz_changeover_matrix')
    op.drop_table('dsiz_changeover_matrix')
    
    op.drop_index('idx_dsiz_wc_modes_work_center', table_name='dsiz_work_center_modes')
    op.drop_table('dsiz_work_center_modes')
