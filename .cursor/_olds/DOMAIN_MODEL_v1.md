# MES Domain Model

This document describes the MES domain model used in the SaaS platform.

## Core Entities

- **ManufacturingOrder**
  - Represents a production order.
  - Fields: id, order_number, product_id, quantity, status, due_date, created_at, updated_at.

- **WorkCenter**
  - Logical or physical unit that performs operations.
  - Fields: id, name, resource_type, status, capacity_units_per_hour, created_at, updated_at.

- **ManufacturingRoute**
  - Sequence of operations to produce a product.
  - Fields: id, product_id, route_name, description, created_at, updated_at.

- **RouteOperation**
  - A single step within a route.
  - Fields: id, route_id, operation_sequence, operation_name, work_center_id, estimated_duration_minutes.

- **ProductionTask**
  - Executable instance of an operation for a specific order.
  - Fields: id, order_id, operation_id, work_center_id, status, assigned_to, started_at, completed_at.

- **GenealogyRecord**
  - Immutable record of events on tasks/products.
  - Fields: id, task_id, operator_id, event_type, timestamp, notes.

- **QualityInspection**
  - Quality check for tasks or orders.
  - Fields: id, task_id, inspector_id, inspection_timestamp, measurements (JSON), status, notes.

## Relationships

- One `ManufacturingOrder` → many `ProductionTask`.
- One `ManufacturingOrder` → one `ManufacturingRoute` (by product).
- One `ManufacturingRoute` → many `RouteOperation`.
- One `RouteOperation` → many `ProductionTask`.
- One `WorkCenter` → many `ProductionTask`.
- One `ProductionTask` → many `GenealogyRecord` and `QualityInspection`.

## Statuses

- Task status: `QUEUED`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `CANCELLED`.
- Order status: `PLANNED`, `RELEASED`, `IN_PROGRESS`, `COMPLETED`, `ON_HOLD`, `CANCELLED`.
- Work center status: `AVAILABLE`, `BUSY`, `MAINTENANCE`, `DOWN`.
- Quality status: `PENDING`, `PASSED`, `FAILED`, `REWORK`.

Use this model as the canonical reference for backend, frontend, and integration logic.
