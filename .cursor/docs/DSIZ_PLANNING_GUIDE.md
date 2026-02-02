# DSIZ Planning — гайд по тестированию

**Назначение:** Планирование варок реактора по сменам на основе нетто-потребности по ГП. Страница «DSIZ Planning» в UI и API `POST /api/v1/dsiz/planning/run`.

**Связь с планом:** Раздел 7 в `MANUAL_TEST_PLAN_MES.md`.

---

## Что делает DSIZ Planning

1. Берёт все ГП из справочника продуктов.
2. Считает нетто-потребность по каждому ГП (через DSIZ MRP: заказы, остатки массы).
3. Агрегирует потребность по массам (BULK).
4. Планирует варки реактора по сменам на заданный горизонт (дата + horizon_days).
5. Учитывает ручные блокировки (manual_blocks) и при необходимости состояние персонала (workforce_state).
6. Возвращает список операций (варки: масса, кг, смена, слот реактора) и предупреждения.

---

## Чек-лист тестирования (раздел 7)

- [ ] **7.1** Открытие страницы «DSIZ Planning» (`/dsiz/planning`) — форма и конфигурация загружаются без белого экрана.
- [ ] **7.2** Выбор параметров: дата начала планирования (не раньше сегодня), горизонт (дней), слоты реакторов, персонал по сменам (при наличии в UI).
- [ ] **7.3** Запуск планирования (кнопка «Запустить планирование») — расчёт выполняется, результаты отображаются (операции, сводка, предупреждения).
- [ ] **7.4** Отображение Gantt планирования (DsizGanttChart) — без падений, читаемые подписи по сменам/реакторам.

**Отложено до после Dispatching:** учёт приоритета MRP (7.отл.1), состав персонала по сменам (7.отл.2), режим маркировки (7.отл.3) — см. MANUAL_TEST_PLAN_MES.md, раздел 7.

**Поведение «Запустить планирование»:** только расчёт плана в памяти; в БД заказы и задачи не создаются. Откат не требуется.

---

## API: POST /api/v1/dsiz/planning/run

**Метод и путь:** `POST /api/v1/dsiz/planning/run`

### Тело запроса (JSON)

| Поле | Тип | Обязательное | Описание |
|------|-----|--------------|----------|
| **planning_date** | string (YYYY-MM-DD) | да | Дата начала планирования |
| **horizon_days** | number | нет (по умолч. 7) | Горизонт в днях (1–30) |
| **manual_blocks** | array | нет | Ручные блокировки смен |
| **workforce_state** | object | нет | Персонал по датам: `{"2026-02-01": {"OPERATOR": 5, "PACKER": 2}}` |

**Элемент manual_blocks (объект):**

| Поле | Тип | Описание |
|------|-----|----------|
| work_center_id | string | Например `WC_REACTOR_MAIN` |
| shift_date | string (YYYY-MM-DD) | Дата смены |
| shift_num | number | 1 или 2 |
| reason | string | Опционально |

**Пример запроса (минимум):**
```json
{
  "planning_date": "2026-02-01",
  "horizon_days": 7
}
```

**Пример с блокировками и персоналом:**
```json
{
  "planning_date": "2026-02-01",
  "horizon_days": 7,
  "manual_blocks": [
    {
      "work_center_id": "WC_REACTOR_MAIN",
      "shift_date": "2026-02-03",
      "shift_num": 1,
      "reason": "Ремонт"
    }
  ],
  "workforce_state": {
    "2026-02-01": { "OPERATOR": 5, "PACKER": 2 },
    "2026-02-02": { "OPERATOR": 4, "PACKER": 2 }
  }
}
```

### Ответ 200 (success: true)

| Поле | Описание |
|------|----------|
| **plan_id** | ID плана (например `DSIZ-PLAN-20260201-A1B2C3D4`) |
| **planning_date** | Дата планирования |
| **horizon_days** | Горизонт в днях |
| **operations** | Массив операций (варки) |
| **warnings** | Массив предупреждений |
| **summary** | Сводка: total_fg_products, total_operations, total_warnings, net_requirements_kg, planned_shifts |

**Элемент operations (объект):**

| Поле | Описание |
|------|----------|
| bulk_product_sku | Код массы (BULK) |
| quantity_kg | Количество кг |
| mode | Режим реактора (CREAM_MODE / PASTE_MODE) |
| shift_date | Дата смены |
| shift_num | 1 или 2 |
| reactor_slot | Слот реактора (1 или 2) |

**Пример ответа:**
```json
{
  "success": true,
  "data": {
    "plan_id": "DSIZ-PLAN-20260201-A1B2C3D4",
    "planning_date": "2026-02-01",
    "horizon_days": 7,
    "operations": [
      {
        "bulk_product_sku": "BULK_CREAM_100ML",
        "quantity_kg": 2000,
        "mode": "CREAM_MODE",
        "shift_date": "2026-02-01",
        "shift_num": 1,
        "reactor_slot": 1
      }
    ],
    "warnings": [],
    "summary": {
      "total_fg_products": 12,
      "total_operations": 5,
      "total_warnings": 0,
      "net_requirements_kg": 8500,
      "planned_shifts": 4
    }
  }
}
```

**Если нет ГП:** ответ 200, `operations: []`, в `warnings` — сообщение «Не найдено готовых продуктов для планирования».

**Ошибки:** 500 — внутренняя ошибка (текст в `detail`).

---

## Где тестировать

- **UI:** Меню → «DSIZ Planning», форма параметров → «Запустить планирование» → результаты и Gantt.
- **Swagger:** `POST /api/v1/dsiz/planning/run` с телом из примеров выше.

---

*Ссылки: MANUAL_TEST_PLAN_MES.md (раздел 7), backend: `customizations/dsiz/routes/dsiz_planning_routes.py`, frontend: `pages/DsizPlanningPage.tsx`.*
