## [2.1.0] - 2026-01-14

### Added - Dispatching & Scheduling

#### DispatchingService (6 methods)
- **release_order()** — Release order to production (PLANNED → RELEASED)
  - Creates ProductionTask from route operations
  - Inherits priority from order
  - Tasks start in QUEUED status

- **dispatch_task()** — Dispatch task to work center (QUEUED → IN_PROGRESS)
  - Capacity validation (checks parallel_capacity)
  - Auto-calculates scheduled_end from estimated_duration
  - Duration priority: actual > estimated > 8h default

- **schedule_tasks()** — Get scheduled tasks with priority ordering
  - Priority: URGENT → HIGH → NORMAL → LOW
  - Eager loading (no N+1 queries)
  - Filters: work_center, horizon_days

- **calculate_work_center_load()** — Calculate utilization %
  - Formula: (Σ IN_PROGRESS hours / (8 × parallel_capacity)) × 100
  - Only counts IN_PROGRESS tasks
  - Ignores QUEUED tasks

- **get_gantt_data()** — Export Gantt chart data
  - Structured timeline for UI visualization
  - Filters: work_center, date range
  - Includes order_number for tracking

- **find_available_work_center()** — Find WC with capacity
  - Checks WorkCenterCapacity for product
  - Returns WC with load <80%
  - Returns None if all overloaded

#### API Endpoints (5 new)
- `POST /api/v1/dispatching/release-order` — Release order
- `POST /api/v1/dispatching/dispatch-task` — Dispatch task
- `GET /api/v1/dispatching/schedule` — Get schedule
- `GET /api/v1/dispatching/work-center-load/{id}` — Get load %
- `GET /api/v1/dispatching/gantt-data` — Export Gantt data

#### Tests (49 new)
- **40 unit tests** for DispatchingService (90% coverage)
- **12 integration tests** for API endpoints (93% coverage)
- **Total: 141 tests** (93% overall coverage)

#### Database Changes
- Added `parallel_capacity` to WorkCenter (for multi-line RCs)
- Task lifecycle: QUEUED → IN_PROGRESS (direct transition)

### Fixed
- Work center load calculation (now uses parallel_capacity)
- 500 error in `/schedule` endpoint (eager loading)
- Safe access to task.work_center (None checks)
- Timezone handling (datetime with tzinfo)

### Business Rules Updated
- **Capacity Formula:**
Load % = (Σ IN_PROGRESS hours / (8 × parallel_capacity)) × 100

- **Load Status Thresholds:**
- <70% → Available
- 70-99% → Busy
- ≥100% → Overloaded

- **Duration Priority:**
1. Actual: `started_at` / `completed_at`
2. Estimated: `estimated_duration_minutes` from RouteOperation
3. Default: 8 hours (one shift)

- **Priority Sequencing:**
- URGENT → HIGH → NORMAL → LOW
- Within priority: sorted by `started_at`

### Documentation
- Created `/docs/DISPATCHING_GUIDE.md` — Complete dispatching guide
- Updated README with test coverage stats
