## 4. DSIZ API Specification (API Спецификация)

### 4.1. Общие принципы

- **Префикс:** `/api/v1/dsiz/...`
- **Формат:** `{"success": true, "data": {...}}` / `{"success": false, "error": "message"}`.
- **HTTP коды:** 200/201, 400, 404, 409, 500.
- **Аутентификация:** JWT, роли:
  - `admin` — полная админка,
  - `planner` — планирование,
  - `dispatcher` — диспетчеризация,
  - `shift_master` — получение/контроль заданий на смену. 
- **Версионирование:** v1.

***

### 4.2. Planning API

#### 4.2.1. `POST /api/v1/dsiz/planning/run` (Роли: planner, admin)

**Описание:** Полный цикл DSIZ-планирования.

**Request:**
```json
{
  "planning_date": "2026-01-25",
  "horizon_days": 7,
  "force_recalculate": false,
  "manual_blocks": [{"work_center_id": "uuid", "blocked_until": "2026-01-26T08:00"}],
  "workforce_state": {
    "shift_1": {"operators_reactor": 1, "operators_tube": 2, "operators_auto": 4},
    "shift_2": {"operators_reactor": 1, "operators_tube": 1, "operators_auto": 3}
  },
  "qr_delays": [{"production_task_id": "uuid-task-123", "qr_ready_date": "2026-01-26T12:00"}]
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "plan_id": "uuid-plan-456",
    "generated_at": "2026-01-25T10:00:00",
    "operations": [
      {
        "id": "uuid-op-mix-001",
        "type": "OP_MIX",
        "work_center": "WC_REACTOR_MAIN",
        "mode": "PASTE_MODE",
        "quantity_kg": 1000,
        "shift": 1,
        "reactor_slot": 1,
        "start_time": "2026-01-25T08:00:00",
        "end_time": "2026-01-25T13:00:00"
      },
      {
        "id": "uuid-op-fill-001",
        "type": "OP_FILL",
        "work_center": "WC_TUBE_LINE_1",
        "quantity_pcs": 9000,
        "setup_time_min": 15,
        "shift": 1,
        "start_time": "2026-01-25T13:30:00",
        "end_time": "2026-01-25T20:00:00",
        "labeling_mode": "MANUAL"
      },
      {
        "id": "uuid-op-label-001",
        "type": "OP_LABEL",
        "work_center": "WC_LABELING",
        "quantity_pcs": 9000,
        "shift": 2,
        "start_time": "2026-01-26T08:00:00",
        "end_time": "2026-01-26T10:00:00"
      }
    ],
    "warnings": ["Авто-розлив shift_2 на 75% (3/4 оператора)"],
    "conflicts": []
  }
}
```

#### 4.2.2. `GET /api/v1/dsiz/planning/plan/{plan_id}` (Роли: planner, dispatcher, shift_master, admin)

Получить план по ID (та же структура ответа).

***

### 4.3. Admin API (Справочники)

#### 4.3.1. Master Data (`admin`)

`GET/PUT /api/v1/dsiz/master-data/work-center-modes`

#### 4.3.2. Changeover Matrix (`admin`)

`GET/POST/PUT/DELETE /api/v1/dsiz/changeover-matrix`

#### 4.3.3. Base Rates (`admin`)

`GET/POST/PUT/DELETE /api/v1/dsiz/base-rates`

#### 4.3.4. Workforce Rules (`admin`)

`GET/POST/PUT/DELETE /api/v1/dsiz/workforce-rules`

#### 4.3.5. Labeling Rules (`admin`)

`GET/PUT /api/v1/dsiz/labeling-rules`

#### 4.3.6. QR Availability (`dispatcher`, `shift_master`, `admin`)

`GET/POST/PUT /api/v1/dsiz/qr-availability/{production_task_id}`

```json
{
  "production_task_id": "uuid-task-123",
  "qr_ready_date": "2026-01-26T12:00:00",
  "qr_count": 9000,
  "status": "READY"
}
```

***

### 4.4. Shift Management (Роли: shift_master, dispatcher, admin)

#### 4.4.1. `POST /api/v1/dsiz/shift/actualize/{shift_date}/{shift_num}`

**Описание:** Фактизация смены (люди, блокировки, QR).

**Request:**
```json
{
  "workforce_actual": {
    "WC_REACTOR_MAIN": {"OPERATOR": 1},
    "WC_TUBE_LINE_1": {"OPERATOR": 1, "PACKER": 0},
    "WC_AUTO_LIQUID_SOAP": {"OPERATOR": 3}
  },
  "manual_blocks": [{"work_center_id": "uuid", "blocked_until": "2026-01-26T08:00"}],
  "qr_updates": [{"production_task_id": "uuid-task-123", "qr_ready_date": "2026-01-26T12:00"}]
}
```

**Response:** Пересчитанный план на смену.

***

### 4.5. Integration

**Core API:** `/api/v1/mrp/run`, `/api/v1/dispatching/plan` автоматически используют DSIZ-сервисы.
**n8n:** `POST /api/v1/dsiz/webhook/order-update`.
**Power BI:** прямое подключение к БД (views), отдельный экспорт не нужен.

***