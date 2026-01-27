# Database Schema v2.0

## Новые таблицы (Iteration 2.0)

### products

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_code VARCHAR(100) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_type VARCHAR(50) NOT NULL,  -- RAW_MATERIAL, BULK, PACKAGING, FINISHED_GOOD
    unit_of_measure VARCHAR(20) NOT NULL,
    min_batch_size_kg NUMERIC(10,2),
    batch_size_step_kg NUMERIC(10,2),
    shelf_life_days INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_products_code ON products(product_code);
CREATE INDEX idx_products_type ON products(product_type);
bill_of_materials
sql
CREATE TABLE bill_of_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    child_product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity NUMERIC(10,4) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    sequence INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_bom_parent_child UNIQUE (parent_product_id, child_product_id)
);

CREATE INDEX idx_bom_parent ON bill_of_materials(parent_product_id);
CREATE INDEX idx_bom_child ON bill_of_materials(child_product_id);
batches
sql
CREATE TABLE batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_number VARCHAR(100) UNIQUE NOT NULL,
    product_id UUID NOT NULL REFERENCES products(id),
    quantity_kg NUMERIC(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL,  -- PLANNED, IN_PROGRESS, COMPLETED, FAILED
    work_center_id UUID REFERENCES work_centers(id),
    operator_id VARCHAR(100),
    planned_start TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    storage_location_id UUID,
    parent_order_id UUID REFERENCES manufacturing_orders(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_batches_number ON batches(batch_number);
CREATE INDEX idx_batches_product ON batches(product_id);
CREATE INDEX idx_batches_status ON batches(status);
CREATE INDEX idx_batches_parent_order ON batches(parent_order_id);
inventory_balances
sql
CREATE TABLE inventory_balances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id),
    location VARCHAR(100) NOT NULL,
    quantity NUMERIC(12,2) NOT NULL DEFAULT 0,
    unit VARCHAR(20) NOT NULL,
    product_status VARCHAR(50) DEFAULT 'FINISHED',  -- FINISHED, SEMI_FINISHED
    production_date TIMESTAMP,
    expiry_date TIMESTAMP,
    reserved_quantity NUMERIC(12,2) NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_inventory_product_location UNIQUE (product_id, location, product_status)
);

CREATE INDEX idx_inventory_product ON inventory_balances(product_id);
CREATE INDEX idx_inventory_location ON inventory_balances(location);
CREATE INDEX idx_inventory_status ON inventory_balances(product_status);
work_center_capacities
sql
CREATE TABLE work_center_capacities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_center_id UUID NOT NULL REFERENCES work_centers(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    capacity_per_shift NUMERIC(10,2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_wc_product UNIQUE (work_center_id, product_id)
);

CREATE INDEX idx_wc_capacity_wc ON work_center_capacities(work_center_id);
CREATE INDEX idx_wc_capacity_product ON work_center_capacities(product_id);
Изменения в существующих таблицах
manufacturing_orders (добавлены поля)
sql
ALTER TABLE manufacturing_orders
ADD COLUMN order_type VARCHAR(50) DEFAULT 'CUSTOMER',
ADD COLUMN priority VARCHAR(50),
ADD COLUMN parent_order_id UUID REFERENCES manufacturing_orders(id),
ADD COLUMN source_order_ids JSONB,
ADD COLUMN is_consolidated BOOLEAN DEFAULT FALSE;

CREATE INDEX idx_orders_type ON manufacturing_orders(order_type);
CREATE INDEX idx_orders_priority ON manufacturing_orders(priority);
CREATE INDEX idx_orders_parent ON manufacturing_orders(parent_order_id);
production_tasks (добавлены поля)
sql
ALTER TABLE production_tasks
ADD COLUMN batch_id UUID REFERENCES batches(id),
ADD COLUMN quantity_kg NUMERIC(10,2),
ADD COLUMN quantity_pcs INTEGER;

CREATE INDEX idx_tasks_batch ON production_tasks(batch_id);
work_centers (добавлены поля)
sql
ALTER TABLE work_centers
ADD COLUMN batch_capacity_kg NUMERIC(10,2),
ADD COLUMN cycles_per_shift INTEGER,
ADD COLUMN exclusive_products JSONB,
ADD COLUMN parallel_capacity INTEGER DEFAULT 1;
Enum-типы (используются в коде, не в БД)
python
# ProductType
RAW_MATERIAL, BULK, PACKAGING, FINISHED_GOOD

# OrderType
CUSTOMER, INTERNAL_BULK

# OrderPriority
URGENT, HIGH, NORMAL, LOW

# OrderStatus (расширен)
PLANNED, RELEASED, IN_PROGRESS, COMPLETED, CANCELLED, SHIP, IN_WORK

# BatchStatus
PLANNED, IN_PROGRESS, COMPLETED, FAILED

# ProductStatus
FINISHED, SEMI_FINISHED
Changelog
v2.0 (2026-01-14):

Добавлены таблицы: products, bill_of_materials, batches, inventory_balances, work_center_capacities.

Расширены: manufacturing_orders, production_tasks, work_centers.

v1.0 (2026-01-13):

Базовая схема для дискретного производства.

text