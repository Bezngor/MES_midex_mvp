"""initial_schema

Revision ID: 20240101000000
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20240101000000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types (if they don't exist)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE orderstatus AS ENUM ('PLANNED', 'RELEASED', 'IN_PROGRESS', 'COMPLETED', 'ON_HOLD', 'CANCELLED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE taskstatus AS ENUM ('QUEUED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE workcenterstatus AS ENUM ('AVAILABLE', 'BUSY', 'MAINTENANCE', 'DOWN');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE qualitystatus AS ENUM ('PENDING', 'PASSED', 'FAILED', 'REWORK');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create work_centers table
    op.create_table(
        'work_centers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('resource_type', sa.String(), nullable=False),
        sa.Column('status', postgresql.ENUM('AVAILABLE', 'BUSY', 'MAINTENANCE', 'DOWN', name='workcenterstatus', create_type=False), nullable=False),
        sa.Column('capacity_units_per_hour', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Create manufacturing_routes table
    op.create_table(
        'manufacturing_routes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('product_id', sa.String(), nullable=False),
        sa.Column('route_name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Create manufacturing_orders table
    op.create_table(
        'manufacturing_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('order_number', sa.String(), unique=True, nullable=False),
        sa.Column('product_id', sa.String(), nullable=False),
        sa.Column('quantity', sa.Numeric(10, 2), nullable=False),
        sa.Column('status', postgresql.ENUM('PLANNED', 'RELEASED', 'IN_PROGRESS', 'COMPLETED', 'ON_HOLD', 'CANCELLED', name='orderstatus', create_type=False), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('idx_manufacturing_orders_status', 'manufacturing_orders', ['status'])
    op.create_index('idx_manufacturing_orders_due_date', 'manufacturing_orders', ['due_date'])

    # Create route_operations table
    op.create_table(
        'route_operations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('route_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('operation_sequence', sa.Integer(), nullable=False),
        sa.Column('operation_name', sa.String(), nullable=False),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('estimated_duration_minutes', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['route_id'], ['manufacturing_routes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['work_center_id'], ['work_centers.id']),
    )

    # Create production_tasks table
    op.create_table(
        'production_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('operation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', postgresql.ENUM('QUEUED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED', name='taskstatus', create_type=False), nullable=False),
        sa.Column('assigned_to', sa.String(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['manufacturing_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['operation_id'], ['route_operations.id']),
        sa.ForeignKeyConstraint(['work_center_id'], ['work_centers.id']),
    )
    op.create_index('idx_production_tasks_status', 'production_tasks', ['status'])
    op.create_index('idx_production_tasks_work_center_id', 'production_tasks', ['work_center_id'])
    op.create_index('idx_production_tasks_task_id', 'production_tasks', ['id'])

    # Create genealogy_records table
    op.create_table(
        'genealogy_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('operator_id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['production_tasks.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_genealogy_records_task_id', 'genealogy_records', ['task_id'])

    # Create quality_inspections table
    op.create_table(
        'quality_inspections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('inspector_id', sa.String(), nullable=False),
        sa.Column('inspection_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('measurements', postgresql.JSONB(), nullable=True),
        sa.Column('status', postgresql.ENUM('PENDING', 'PASSED', 'FAILED', 'REWORK', name='qualitystatus', create_type=False), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['production_tasks.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_quality_inspections_task_id', 'quality_inspections', ['task_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('quality_inspections')
    op.drop_table('genealogy_records')
    op.drop_table('production_tasks')
    op.drop_table('route_operations')
    op.drop_table('manufacturing_orders')
    op.drop_table('manufacturing_routes')
    op.drop_table('work_centers')

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS qualitystatus")
    op.execute("DROP TYPE IF EXISTS workcenterstatus")
    op.execute("DROP TYPE IF EXISTS taskstatus")
    op.execute("DROP TYPE IF EXISTS orderstatus")
