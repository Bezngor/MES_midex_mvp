# Dispatching & Scheduling Guide

## Overview

Dispatching module manages work center assignment and task scheduling for production orders.

---

## Core Concepts

### 1. Order Release
**Flow:** `PLANNED → RELEASED`

- Creates ProductionTask records from route operations
- Tasks start in `QUEUED` status
- Priority inherited from order

**API:**
```bash
POST /api/v1/dispatching/release-order
{
  "order_id": "uuid-order"
}
2. Task Dispatching
Flow: QUEUED → IN_PROGRESS

Assigns task to work center

Calculates scheduled_start and scheduled_end

Validates capacity before assignment

API:

bash
POST /api/v1/dispatching/dispatch-task
{
  "task_id": "uuid-task",
  "work_center_id": "uuid-wc",
  "scheduled_start": "2026-01-15T08:00:00Z"
}
Duration Calculation:

text
scheduled_end = scheduled_start + estimated_duration_minutes
3. Work Center Load
Formula:

text
Load % = (Σ IN_PROGRESS task hours / (8 × parallel_capacity)) × 100
Status Thresholds:

<70% → Available

70-99% → Busy

≥100% → Overloaded

API:

bash
GET /api/v1/dispatching/work-center-load/{work_center_id}?date=2026-01-15
4. Scheduling
Priority Order: URGENT → HIGH → NORMAL → LOW

Only includes:

IN_PROGRESS tasks (dispatched and running)

Tasks within horizon (default: 7 days)

API:

bash
GET /api/v1/dispatching/schedule?horizon_days=7&work_center_id={uuid}
5. Gantt Data Export
Structure:

json
{
  "work_centers": [
    {
      "id": "uuid",
      "name": "Assembly Line 1",
      "tasks": [
        {
          "id": "uuid",
          "name": "Produce FG-001",
          "start": "2026-01-15T08:00:00Z",
          "end": "2026-01-15T16:00:00Z",
          "priority": "HIGH",
          "status": "IN_PROGRESS",
          "order_number": "MO-2026-001"
        }
      ]
    }
  ],
  "start_date": "2026-01-15T00:00:00Z",
  "end_date": "2026-01-22T00:00:00Z"
}
API:

bash
GET /api/v1/dispatching/gantt-data?start_date=...&end_date=...
Business Rules
Capacity Validation:

Cannot dispatch task if work center load ≥100%

Uses parallel_capacity for multi-line work centers

Priority Sequencing:

URGENT tasks scheduled first

Within priority, sorted by scheduled_start

Duration Sources (priority order):

Actual: started_at / completed_at

Estimated: estimated_duration_minutes from RouteOperation

Default: 8 hours (one shift)

Task Lifecycle:

QUEUED → created from order release

IN_PROGRESS → dispatched to work center

COMPLETED → finished production

Example Workflow
Step 1: Create Order
bash
POST /api/v1/manufacturing-orders
{
  "order_number": "MO-2026-001",
  "product_id": "uuid-fg",
  "quantity": 1000,
  "status": "PLANNED",
  "priority": "HIGH",
  "due_date": "2026-01-20T12:00:00Z"
}
Step 2: Release Order
bash
POST /api/v1/dispatching/release-order
{
  "order_id": "uuid-order"
}
# → Creates 3 tasks in QUEUED status
Step 3: Dispatch Tasks
bash
POST /api/v1/dispatching/dispatch-task
{
  "task_id": "uuid-task-1",
  "work_center_id": "uuid-wc-reactor",
  "scheduled_start": "2026-01-15T08:00:00Z"
}
# → Task 1: QUEUED → IN_PROGRESS
Step 4: Monitor Schedule
bash
GET /api/v1/dispatching/schedule
# → View all dispatched tasks with timeline
Step 5: Check Capacity
bash
GET /api/v1/dispatching/work-center-load/{uuid-wc-reactor}
# → Load: 100%, Status: Overloaded
Known Limitations (MVP v2.1)
❌ No automatic scheduling (manual dispatch required)

❌ No changeover time consideration

❌ No multi-shift support (fixed 8-hour shifts)

❌ No backward scheduling (all forward from release date)

These will be addressed in Iteration 2.2+.

Metrics & KPIs
Work Center Utilization
text
Utilization % = (Actual Production Hours / Available Hours) × 100
On-Time Dispatch Rate
text
OTD % = (Tasks Dispatched On Time / Total Tasks) × 100
Schedule Adherence
text
Adherence % = (Tasks Started On Schedule / Total Tasks) × 100
Testing
Manual Smoke Test
bash
# 1. Release order
curl -X POST .../dispatching/release-order -d '{"order_id": "..."}'

# 2. Dispatch task
curl -X POST .../dispatching/dispatch-task -d '{"task_id": "...", "work_center_id": "..."}'

# 3. Get schedule
curl -X GET .../dispatching/schedule?horizon_days=7

# 4. Check load
curl -X GET .../dispatching/work-center-load/{uuid}

# 5. Get Gantt data
curl -X GET .../dispatching/gantt-data
Automated Tests
bash
pytest tests/services/test_dispatching_service.py -v
pytest tests/api/test_dispatching_api.py -v
Changelog
2026-01-14 (v2.1):

Fixed: Work center load calculation (300% → correct %)

Fixed: 500 error in /schedule (eager loading)

Added: parallel_capacity support

Added: Automatic task creation from route operations

Added: Gantt data export API