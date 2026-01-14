# MES Platform Changelog

## [2.0.0] - 2026-01-14

### Added - Iteration 2.0: Process Manufacturing Foundation

#### Core Models
- **Product** — универсальный справочник (RAW_MATERIAL, BULK, PACKAGING, FINISHED_GOOD)
- **BillOfMaterial** — многоуровневая BOM (3 уровня)
- **Batch** — партии для batch-производства (варка массы)
- **InventoryBalance** — учёт остатков (с поддержкой SEMI_FINISHED статуса)
- **WorkCenterCapacity** — производительность WorkCenter по продуктам

#### Extended Models
- **ManufacturingOrder**: добавлены поля `order_type`, `priority`, `parent_order_id`, `source_order_ids`, `is_consolidated`
- **ProductionTask**: добавлены поля `batch_id`, `quantity_kg`, `quantity_pcs`
- **WorkCenter**: добавлены поля `batch_capacity_kg`, `cycles_per_shift`, `exclusive_products`, `parallel_capacity`

#### API Endpoints (21 новый)
- `/api/v1/products` — CRUD для продуктов
- `/api/v1/bill-of-materials` — CRUD для BOM
- `/api/v1/batches` — CRUD для партий
- `/api/v1/inventory` — просмотр остатков + корректировка
- `/api/v1/work-center-capacities` — CRUD для мощностей

#### Features
- Автогенерация `batch_number` (формат: `BATCH-YYYYMMDD-HHMMSS-{UUID}`)
- Гибкая корректировка инвентаря: абсолютное значение (`quantity`) или дельта (`quantity_delta`)
- Фильтрация: продукты по типу, BOM по родителю, батчи по статусу
- Валидация уникальности: `product_code`, `batch_number`, `(work_center_id, product_id)`

### Changed
- Миграция БД: `20260114000001_add_process_manufacturing_models.py`
- Расширены enums: `ProductType`, `BatchStatus`, `ProductStatus`, `OrderType`, `OrderPriority`

### Fixed
- Корректная работа с Decimal полями (quantity, reserved_quantity)
- SQLite совместимость в тестах (JSONB → JSON)
- Валидация Pydantic вместо ValueError

### Testing
- Smoke test: ✅ Все операции (создание продуктов, BOM, batch, inventory) работают
- Regression: ✅ 16/16 тестов MVP v1.0 пройдены (100%)

---

## [1.0.0] - 2026-01-13

### Added - MVP v1.0: Discrete Manufacturing
- ManufacturingOrder, ProductionTask, WorkCenter, Route, QualityInspection
- Basic CRUD API
- Genealogy tracking
- Simple FIFO dispatching

### Testing
- 16 pytest tests (100% passed)
