# Changelog

## [2.0.0] - 2026-01-14

### Added - Iteration 2.0: Process Manufacturing

#### Models (5 new)
- **Product** — Product catalog (RAW_MATERIAL, BULK, PACKAGING, FINISHED_GOOD)
- **BillOfMaterial** — Multi-level BOM support
- **Batch** — Batch production tracking
- **InventoryBalance** — Inventory tracking (FINISHED/SEMI_FINISHED)
- **WorkCenterCapacity** — Capacity planning by product

#### API Endpoints (25 new)
- **Products** (5 endpoints): CRUD + filter by type
- **BOM** (4 endpoints): CRUD + filter by parent
- **Batches** (5 endpoints): CRUD + filter by status
- **Inventory** (4 endpoints): CRUD + adjust (absolute/delta)
- **WorkCenterCapacity** (3 endpoints): CRUD
- **MRP** (4 endpoints): consolidate, explode-bom, net-requirement, create-bulk-order

#### Database Changes
- Migration `20260114000001`: 5 new tables
- Migration `20260114171052`: Add SHIP/IN_WORK to OrderStatus enum
- Extended ManufacturingOrder with `parent_order_id`, `priority`

#### MRP Service
- **consolidate_orders()** — Order consolidation with priority calculation
- **explode_bom()** — Recursive BOM explosion (multi-level)
- **calculate_net_requirement()** — Net = Gross - Available (FINISHED)
- **round_to_batch()** — Batch rounding (always round UP)
- **create_dependent_bulk_order()** — Create INTERNAL_BULK orders

#### Tests
- **92 total tests** (35 unit + 13 integration + 44 existing)
- **95% code coverage** for MRPService
- **100% pass rate** (no regressions)

### Fixed
- parent_order_id made optional in CreateBulkOrderRequest
- SHIP/IN_WORK enum values added to OrderStatus
- Batch auto-generation (BATCH-YYYYMMDD-HHMMSS-UUID format)

### Business Rules
- Priority calculation: <7d=URGENT, 7-14d=HIGH, 14-30d=NORMAL, >30d=LOW
- BOM explosion: recursive with circular dependency protection (max 10 levels)
- Net requirement: only FINISHED inventory counted, SEMI_FINISHED excluded
- Batch rounding: always rounds UP, respects min_batch_size_kg and batch_size_step_kg

---

## [1.0.0] - 2026-01-13

### Added - MVP v1.0: Core MES

#### Models
- ManufacturingOrder
- WorkCenter
- ProductionTask

#### API Endpoints (16 endpoints)
- Manufacturing Orders (CRUD)
- Work Centers (CRUD)
- Production Tasks (CRUD)

#### Database
- Initial schema with 3 core tables
- Enums: OrderStatus, OrderType, TaskStatus

#### Tests
- 16 core tests (100% pass)
