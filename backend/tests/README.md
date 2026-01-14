# Backend Tests

Автоматизированные pytest-тесты для backend API MES платформы.

## Структура тестов

### MVP v1.0 тесты
- `conftest.py` - общие fixtures (тестовая БД, клиент, тестовые данные)
- `test_order_service.py` - unit-тесты для OrderService (5 тестов)
- `test_task_service.py` - unit-тесты для TaskService (6 тестов)
- `test_api_integration.py` - интеграционные API-тесты (5 тестов)

### Iteration 2.0 тесты
- `models/` - unit-тесты для новых моделей:
  - `test_product.py` - тесты модели Product (5 тестов)
  - `test_bom.py` - тесты модели BillOfMaterial (5 тестов)
  - `test_batch.py` - тесты модели Batch (5 тестов)
  - `test_inventory.py` - тесты модели InventoryBalance (6 тестов)
  - `test_work_center_capacity.py` - тесты модели WorkCenterCapacity (4 теста)
- `api/` - интеграционные тесты для новых API endpoints:
  - `test_products_api.py` - тесты API продуктов (9 тестов)
  - `test_bom_api.py` - тесты API спецификаций (6 тестов)
  - `test_batches_api.py` - тесты API батчей (7 тестов)
  - `test_inventory_api.py` - тесты API остатков (7 тестов)
  - `test_work_center_capacities_api.py` - тесты API мощностей РЦ (7 тестов)

## Установка зависимостей

```bash
cd backend
pip install -e .
```

Или установите pytest напрямую:
```bash
pip install pytest pytest-asyncio
```

## Запуск тестов

```bash
cd backend
python -m pytest
```

С подробным выводом:
```bash
python -m pytest -v
```

С покрытием (HTML отчёт):
```bash
python -m pytest --cov=src --cov-report=html
```

Или с текстовым отчётом:
```bash
python -m pytest --cov=src --cov-report=term-missing
```

**Примечание:** Используйте `python -m pytest` вместо просто `pytest` для гарантированной работы всех плагинов (включая pytest-cov).

## Описание тестов

### OrderService Tests (5 тестов)

1. `test_create_order_with_tasks_success` - создание заказа с автогенерацией задач
2. `test_create_order_route_not_found` - обработка несуществующего product_id
3. `test_create_order_invalid_quantity` - валидация quantity <= 0
4. `test_get_order_with_tasks` - получение заказа с задачами (eager loading)
5. `test_list_orders_filter_by_status` - фильтрация заказов по статусу

### TaskService Tests (6 тестов)

1. `test_start_task_from_queued` - запуск задачи из QUEUED
2. `test_start_task_invalid_status` - попытка запустить задачу с невалидным статусом
3. `test_complete_task_from_in_progress` - завершение задачи из IN_PROGRESS
4. `test_complete_task_updates_order_status` - обновление статуса заказа после завершения всех задач
5. `test_fail_task` - пометка задачи как проваленной
6. `test_list_tasks_filter_by_status` - фильтрация задач по статусу

### API Integration Tests (5 тестов)

1. `test_create_order_api` - создание заказа через API
2. `test_get_order_api` - получение заказа с задачами через API
3. `test_start_task_api` - запуск задачи через API
4. `test_complete_task_api` - завершение задачи через API
5. `test_dispatch_preview_excludes_down_centers` - preview dispatch исключает задачи для DOWN центров

## Тестовая БД

Тесты используют временную файловую SQLite базу данных, которая создаётся и удаляется для каждого теста. Это обеспечивает изоляцию тестов и совместимость между сессиями (необходимо для интеграционных API-тестов). JSONB типы автоматически заменяются на JSON для совместимости с SQLite.

## Fixtures

### Базовые fixtures
- `test_db` - тестовая БД-сессия с автоматическим rollback
- `client` - FastAPI TestClient для интеграционных тестов
- `sample_work_centers` - 3 WorkCenter для использования в тестах
- `sample_route` - ManufacturingRoute с 3 RouteOperations

### Fixtures для Iteration 2.0
- `sample_bulk_product` - BULK продукт с параметрами батча
- `sample_finished_good` - FINISHED_GOOD продукт
- `sample_packaging` - PACKAGING продукт
- `sample_raw_material` - RAW_MATERIAL продукт
- `sample_bom_fg_to_bulk` - BOM запись: FG → BULK
- `sample_bom_fg_to_packaging` - BOM запись: FG → PACKAGING
- `sample_bom_bulk_to_raw` - BOM запись: BULK → RAW
- `sample_batch` - батч со статусом PLANNED
- `sample_batch_in_progress` - батч со статусом IN_PROGRESS
- `sample_manufacturing_order` - производственный заказ для тестов
- `sample_inventory_finished` - остаток инвентаря (FINISHED)
- `sample_inventory_semi_finished` - остаток инвентаря (SEMI_FINISHED)
- `sample_wc_capacity_tubing_cream` - мощность РЦ для крема
- `sample_wc_capacity_reactor_bulk` - мощность РЦ для bulk продукта

## Статистика тестов

- **Всего тестов:** 76 (60 passed, 1 skipped, 15 MVP v1.0)
- **Unit-тесты моделей:** 25 тестов
- **Интеграционные API-тесты:** 36 тестов
- **Покрытие кода:** ~62% (для новых моделей и API ~80%+)
