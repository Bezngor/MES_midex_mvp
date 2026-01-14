# API Specification v2.0

## Новые endpoints (Iteration 2.0)

### Products

POST /api/v1/products
GET /api/v1/products
GET /api/v1/products/{product_id}
PATCH /api/v1/products/{product_id}
DELETE /api/v1/products/{product_id}

text

**Example:**
```json
POST /api/v1/products
{
  "product_code": "BULK_CREAM_REGEN",
  "product_name": "Масса Крем Регенерирующий",
  "product_type": "BULK",
  "unit_of_measure": "kg",
  "min_batch_size_kg": 500,
  "batch_size_step_kg": 1000,
  "shelf_life_days": 7
}
Bill of Materials (BOM)
text
POST   /api/v1/bom
GET    /api/v1/bom?parent_product_id={id}
GET    /api/v1/bom?child_product_id={id}
GET    /api/v1/bom/{bom_id}
DELETE /api/v1/bom/{bom_id}
Example:

json
POST /api/v1/bom
{
  "parent_product_id": "uuid-fg-cream-100ml",
  "child_product_id": "uuid-bulk-cream-regen",
  "quantity": 0.09,
  "unit": "kg"
}
Batches
text
POST   /api/v1/batches
GET    /api/v1/batches
GET    /api/v1/batches/{batch_id}
PATCH  /api/v1/batches/{batch_id}/start
PATCH  /api/v1/batches/{batch_id}/complete
Example:

json
POST /api/v1/batches
{
  "product_id": "uuid-bulk-cream-regen",
  "quantity_kg": 2000,
  "work_center_id": "uuid-reactor-cream",
  "parent_order_id": "uuid-order-001"
}

Response:
{
  "batch_number": "BATCH-2026-001",
  "status": "PLANNED",
  ...
}
Inventory
text
GET    /api/v1/inventory
GET    /api/v1/inventory?product_id={id}
GET    /api/v1/inventory?location={location}
GET    /api/v1/inventory?product_status=SEMI_FINISHED
PATCH  /api/v1/inventory/{product_id}/adjust
Example:

json
GET /api/v1/inventory?product_id=uuid-bulk-cream-regen

Response:
[
  {
    "product_id": "uuid-bulk-cream-regen",
    "location": "CUB_1",
    "quantity": 650,
    "unit": "kg",
    "product_status": "FINISHED",
    "production_date": "2026-01-10T08:00:00Z",
    "expiry_date": "2026-01-17T08:00:00Z",
    "reserved_quantity": 100,
    "available_quantity": 550
  }
]
Work Center Capacities
text
POST   /api/v1/work-center-capacities
GET    /api/v1/work-center-capacities?work_center_id={id}
GET    /api/v1/work-center-capacities?product_id={id}
PATCH  /api/v1/work-center-capacities/{id}
DELETE /api/v1/work-center-capacities/{id}
Example:

json
POST /api/v1/work-center-capacities
{
  "work_center_id": "uuid-wc-tubing-cream",
  "product_id": "uuid-fg-cream-100ml",
  "capacity_per_shift": 15000,
  "unit": "pcs"
}
MRP (Material Requirements Planning)
text
POST /api/v1/mrp/consolidate
POST /api/v1/mrp/explode-bom
Example:

json
POST /api/v1/mrp/consolidate
{
  "horizon_days": 7
}

Response:
{
  "consolidated_orders": [
    {
      "product_id": "uuid-fg-cream-100ml",
      "total_quantity": 20000,
      "priority": "URGENT",
      "earliest_due_date": "2026-01-18T12:00:00Z",
      "source_orders": ["uuid-order-001", "uuid-order-005"]
    }
  ]
}
json
POST /api/v1/mrp/explode-bom
{
  "product_id": "uuid-fg-cream-100ml",
  "quantity": 20000
}

Response:
{
  "requirements": {
    "uuid-bulk-cream-regen": {"quantity": 1800, "unit": "kg"},
    "uuid-pkg-tube-100ml": {"quantity": 20000, "unit": "pcs"},
    "uuid-raw-glycerin": {"quantity": 27, "unit": "kg"},
    ...
  }
}
Изменения в существующих endpoints
Manufacturing Orders (расширены)
POST /api/v1/orders — новые поля:

json
{
  "product_id": "uuid-fg-cream-100ml",
  "quantity": 15000,
  "order_type": "CUSTOMER",  // НОВОЕ
  "status": "SHIP",          // НОВОЕ (вместо PLANNED)
  "priority": "URGENT",      // НОВОЕ (auto-calculated)
  "due_date": "2026-01-18T12:00:00Z"
}
GET /api/v1/orders — новые query params:

text
GET /api/v1/orders?order_type=CUSTOMER
GET /api/v1/orders?status=SHIP
GET /api/v1/orders?priority=URGENT
Changelog
v2.0 (2026-01-14):

Добавлены endpoints для Products, BOM, Batches, Inventory, WorkCenterCapacities, MRP.

Расширены Manufacturing Orders (новые поля и фильтры).

v1.0 (2026-01-13):

Базовые CRUD endpoints для Orders, Tasks, WorkCenters, QualityInspections.