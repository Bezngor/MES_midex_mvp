# Database Schema (PostgreSQL)

## manufacturing_orders

- `id` (uuid, pk)
- `order_number` (text, unique)
- `product_id` (text)
- `quantity` (numeric)
- `status` (text, enum)
- `due_date` (timestamp)
- `created_at` (timestamp)
- `updated_at` (timestamp)

Indexes:

- `idx_manufacturing_orders_status`
- `idx_manufacturing_orders_due_date`

## work_centers

- `id` (uuid, pk)
- `name` (text)
- `resource_type` (text)
- `status` (text, enum)
- `capacity_units_per_hour` (numeric)
- `created_at` (timestamp)
- `updated_at` (timestamp)

## manufacturing_routes

- `id` (uuid, pk)
- `product_id` (text)
- `route_name` (text)
- `description` (text, nullable)
- `created_at` (timestamp)
- `updated_at` (timestamp)

## route_operations

- `id` (uuid, pk)
- `route_id` (uuid, fk → manufacturing_routes.id)
- `operation_sequence` (int)
- `operation_name` (text)
- `work_center_id` (uuid, fk → work_centers.id)
- `estimated_duration_minutes` (int)

## production_tasks

- `id` (uuid, pk)
- `order_id` (uuid, fk → manufacturing_orders.id)
- `operation_id` (uuid, fk → route_operations.id)
- `work_center_id` (uuid, fk → work_centers.id)
- `status` (text, enum)
- `assigned_to` (text, nullable)
- `started_at` (timestamp, nullable)
- `completed_at` (timestamp, nullable)
- `created_at` (timestamp)
- `updated_at` (timestamp)

## genealogy_records

- `id` (uuid, pk)
- `task_id` (uuid, fk → production_tasks.id)
- `operator_id` (text)
- `event_type` (text)
- `timestamp` (timestamp)
- `notes` (text, nullable)

## quality_inspections

- `id` (uuid, pk)
- `task_id` (uuid, fk → production_tasks.id)
- `inspector_id` (text)
- `inspection_timestamp` (timestamp)
- `measurements` (jsonb)
- `status` (text, enum)
- `notes` (text, nullable)

(Keep this schema in sync with Alembic migrations.)
