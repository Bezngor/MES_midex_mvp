"""add_process_manufacturing_models

Revision ID: 20260114000001
Revises: 20240101000000
Create Date: 2026-01-14

"""

from __future__ import annotations

from typing import Any

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260114000001"
down_revision = "20240101000000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Выполнить миграцию: добавить модели для процессного производства."""
    # Create products table
    op.create_table(
        "products",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("product_code", sa.String(100), nullable=False, unique=True),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("product_type", sa.String(50), nullable=False),
        sa.Column("unit_of_measure", sa.String(20), nullable=False),
        sa.Column("min_batch_size_kg", sa.Numeric(10, 2), nullable=True),
        sa.Column("batch_size_step_kg", sa.Numeric(10, 2), nullable=True),
        sa.Column("shelf_life_days", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_products_code", "products", ["product_code"])
    op.create_index("idx_products_type", "products", ["product_type"])

    # Create bill_of_materials table
    op.create_table(
        "bill_of_materials",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("parent_product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("child_product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 4), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("sequence", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_product_id"],
            ["products.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["child_product_id"],
            ["products.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "parent_product_id",
            "child_product_id",
            name="uq_bom_parent_child",
        ),
    )
    op.create_index("idx_bom_parent", "bill_of_materials", ["parent_product_id"])
    op.create_index("idx_bom_child", "bill_of_materials", ["child_product_id"])

    # Create batches table
    op.create_table(
        "batches",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("batch_number", sa.String(100), nullable=False, unique=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quantity_kg", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("work_center_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("operator_id", sa.String(100), nullable=True),
        sa.Column("planned_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("storage_location_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("parent_order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["work_center_id"],
            ["work_centers.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["parent_order_id"],
            ["manufacturing_orders.id"],
        ),
    )
    op.create_index("idx_batches_number", "batches", ["batch_number"])
    op.create_index("idx_batches_product", "batches", ["product_id"])
    op.create_index("idx_batches_status", "batches", ["status"])
    op.create_index("idx_batches_parent_order", "batches", ["parent_order_id"])

    # Create inventory_balances table
    op.create_table(
        "inventory_balances",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("location", sa.String(100), nullable=False),
        sa.Column(
            "quantity",
            sa.Numeric(12, 2),
            nullable=False,
            server_default="0",
        ),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column(
            "product_status",
            sa.String(50),
            nullable=False,
            server_default="FINISHED",
        ),
        sa.Column("production_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expiry_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "reserved_quantity",
            sa.Numeric(12, 2),
            nullable=False,
            server_default="0",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.UniqueConstraint(
            "product_id",
            "location",
            "product_status",
            name="uq_inventory_product_location_status",
        ),
    )
    op.create_index("idx_inventory_product", "inventory_balances", ["product_id"])
    op.create_index("idx_inventory_location", "inventory_balances", ["location"])
    op.create_index("idx_inventory_status", "inventory_balances", ["product_status"])

    # Create work_center_capacities table
    op.create_table(
        "work_center_capacities",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("work_center_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("capacity_per_shift", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["work_center_id"],
            ["work_centers.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "work_center_id",
            "product_id",
            name="uq_wc_product",
        ),
    )
    op.create_index("idx_wc_capacity_wc", "work_center_capacities", ["work_center_id"])
    op.create_index(
        "idx_wc_capacity_product",
        "work_center_capacities",
        ["product_id"],
    )

    # Alter manufacturing_orders
    op.add_column(
        "manufacturing_orders",
        sa.Column(
            "order_type",
            sa.String(50),
            nullable=False,
            server_default="CUSTOMER",
        ),
    )
    op.add_column(
        "manufacturing_orders",
        sa.Column("priority", sa.String(50), nullable=True),
    )
    op.add_column(
        "manufacturing_orders",
        sa.Column("parent_order_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "manufacturing_orders",
        sa.Column("source_order_ids", postgresql.JSONB, nullable=True),
    )
    op.add_column(
        "manufacturing_orders",
        sa.Column(
            "is_consolidated",
            sa.Boolean,
            nullable=False,
            server_default="false",
        ),
    )
    op.create_index("idx_orders_type", "manufacturing_orders", ["order_type"])
    op.create_index("idx_orders_priority", "manufacturing_orders", ["priority"])
    op.create_index("idx_orders_parent", "manufacturing_orders", ["parent_order_id"])
    op.create_foreign_key(
        "fk_orders_parent",
        "manufacturing_orders",
        "manufacturing_orders",
        ["parent_order_id"],
        ["id"],
    )

    # Alter production_tasks
    op.add_column(
        "production_tasks",
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "production_tasks",
        sa.Column("quantity_kg", sa.Numeric(10, 2), nullable=True),
    )
    op.add_column(
        "production_tasks",
        sa.Column("quantity_pcs", sa.Integer, nullable=True),
    )
    op.create_index("idx_tasks_batch", "production_tasks", ["batch_id"])
    op.create_foreign_key(
        "fk_tasks_batch",
        "production_tasks",
        "batches",
        ["batch_id"],
        ["id"],
    )

    # Alter work_centers
    op.add_column(
        "work_centers",
        sa.Column("batch_capacity_kg", sa.Numeric(10, 2), nullable=True),
    )
    op.add_column(
        "work_centers",
        sa.Column("cycles_per_shift", sa.Integer, nullable=True),
    )
    op.add_column(
        "work_centers",
        sa.Column("exclusive_products", postgresql.JSONB, nullable=True),
    )
    op.add_column(
        "work_centers",
        sa.Column("parallel_capacity", sa.Integer, nullable=False, server_default="1"),
    )


def downgrade() -> None:
    """Откатить миграцию: удалить процессные модели и расширения."""
    # Reverse changes to production_tasks
    op.drop_constraint("fk_tasks_batch", "production_tasks", type_="foreignkey")
    op.drop_index("idx_tasks_batch", table_name="production_tasks")
    op.drop_column("production_tasks", "quantity_pcs")
    op.drop_column("production_tasks", "quantity_kg")
    op.drop_column("production_tasks", "batch_id")

    # Reverse changes to work_centers
    op.drop_column("work_centers", "parallel_capacity")
    op.drop_column("work_centers", "exclusive_products")
    op.drop_column("work_centers", "cycles_per_shift")
    op.drop_column("work_centers", "batch_capacity_kg")

    # Reverse changes to manufacturing_orders
    op.drop_constraint("fk_orders_parent", "manufacturing_orders", type_="foreignkey")
    op.drop_index("idx_orders_parent", table_name="manufacturing_orders")
    op.drop_index("idx_orders_priority", table_name="manufacturing_orders")
    op.drop_index("idx_orders_type", table_name="manufacturing_orders")
    op.drop_column("manufacturing_orders", "is_consolidated")
    op.drop_column("manufacturing_orders", "source_order_ids")
    op.drop_column("manufacturing_orders", "parent_order_id")
    op.drop_column("manufacturing_orders", "priority")
    op.drop_column("manufacturing_orders", "order_type")

    # Drop process tables
    op.drop_table("work_center_capacities")
    op.drop_table("inventory_balances")
    op.drop_table("batches")
    op.drop_table("bill_of_materials")
    op.drop_table("products")

