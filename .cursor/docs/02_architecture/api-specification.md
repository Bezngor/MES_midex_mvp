# API Specification v2.1

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
Dispatching & Scheduling

#### Release Order

```http
POST /api/v1/dispatching/release-order
Content-Type: application/json

{
  "order_id": "uuid-order-001"
}
Response:

json
{
  "success": true,
  "data": {
    "order_id": "uuid-order-001",
    "status": "RELEASED",
    "tasks_created": 3,
    "task_ids": ["uuid-task-001", "uuid-task-002", "uuid-task-003"]
  }
}
#### Dispatch Task

```http
POST /api/v1/dispatching/dispatch-task
Content-Type: application/json

{
  "task_id": "uuid-task-001",
  "work_center_id": "uuid-wc-tubing",
  "scheduled_start": "2026-01-20T08:00:00Z"
}
Response:

json
{
  "success": true,
  "data": {
    "task_id": "uuid-task-001",
    "status": "IN_PROGRESS",
    "scheduled_start": "2026-01-20T08:00:00Z",
    "scheduled_end": "2026-01-20T09:30:00Z",
    "work_center_id": "uuid-wc-tubing"
  }
}
#### Get Work Center Load

```http
GET /api/v1/dispatching/work-center-load/{work_center_id}?date=2026-01-20
Response:

json
{
  "success": true,
  "data": {
    "work_center_id": "uuid-wc-tubing",
    "date": "2026-01-20",
    "load_percentage": 85.5,
    "status": "BUSY",
    "parallel_capacity": 4,
    "active_tasks": 3,
    "available_slots": 1,
    "total_task_hours": 27.4
  }
}
Load Status:
- `AVAILABLE` — load < 70%
- `BUSY` — load 70-99%
- `OVERLOADED` — load ≥ 100%

#### Get Schedule (Gantt Data)

```http
GET /api/v1/dispatching/schedule?horizon_days=7&work_center_id=uuid-wc-tubing
Response:

json
{
  "success": true,
  "data": [
    {
      "task_id": "uuid-task-001",
      "order_id": "uuid-order-001",
      "operation_name": "Filling",
      "work_center_id": "uuid-wc-tubing",
      "scheduled_start": "2026-01-20T08:00:00Z",
      "scheduled_end": "2026-01-20T09:30:00Z",
      "status": "IN_PROGRESS",
      "priority": "URGENT"
    }
  ]
}
#### Preview Dispatch Plan

```http
POST /api/v1/dispatching/preview?limit=50
Response:

json
{
  "success": true,
  "data": [
    {
      "task_id": "uuid-task-005",
      "order_id": "uuid-order-002",
      "status": "QUEUED",
      "work_center_id": "uuid-wc-reactor",
      "can_dispatch": true,
      "reason": "Work center available"
    },
    {
      "task_id": "uuid-task-007",
      "order_id": "uuid-order-003",
      "status": "QUEUED",
      "work_center_id": "uuid-wc-down",
      "can_dispatch": false,
      "reason": "Work center status: DOWN"
    }
  ]
}
Logic:
- Returns QUEUED tasks sorted by created_at (FIFO).
- Filters out tasks assigned to MAINTENANCE/DOWN work centers.
- Does NOT change task statuses (preview only).

---

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
## Changelog

**v2.1 (2026-01-15):**
- Добавлены **Dispatching endpoints**: `release-order`, `dispatch-task`, `work-center-load`, `schedule`, `preview`.
- Добавлены расчёты загрузки Work Centers (load percentage, status).
- Добавлен календарный план задач (Gantt data) с фильтрацией по Work Center.

**v2.0 (2026-01-14):**
- Добавлены endpoints для Products, BOM, Batches, Inventory, WorkCenterCapacities, MRP.
- Расширены Manufacturing Orders (новые поля и фильтры).

**v1.0 (2026-01-13):**
- Базовые CRUD endpoints для Orders, Tasks, WorkCenters, QualityInspections.