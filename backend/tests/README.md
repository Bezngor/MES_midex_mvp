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
- `services/` - unit-тесты для сервисов:
  - `test_mrp_service.py` - тесты MRPService (35 тестов)
- `api/` - интеграционные тесты для новых API endpoints:
  - `test_products_api.py` - тесты API продуктов (9 тестов)
  - `test_bom_api.py` - тесты API спецификаций (6 тестов)
  - `test_batches_api.py` - тесты API батчей (7 тестов)
  - `test_inventory_api.py` - тесты API остатков (7 тестов)
  - `test_work_center_capacities_api.py` - тесты API мощностей РЦ (7 тестов)
  - `test_mrp_api.py` - тесты MRP API (13 тестов)

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

## Описание MRP тестов

### MRPService Unit Tests (35 тестов)

#### Консолидация заказов (10 тестов)
1. `test_consolidate_orders_single_product` - консолидация одного продукта
2. `test_consolidate_orders_multiple_products` - консолидация нескольких продуктов
3. `test_consolidate_orders_priority_urgent` - приоритет URGENT (<7 дней)
4. `test_consolidate_orders_priority_high` - приоритет HIGH (7-14 дней)
5. `test_consolidate_orders_priority_normal` - приоритет NORMAL (14-30 дней)
6. `test_consolidate_orders_priority_low` - приоритет LOW (>30 дней)
7. `test_consolidate_orders_highest_priority_wins` - выбор наивысшего приоритета
8. `test_consolidate_orders_horizon_filter` - фильтрация по горизонту
9. `test_consolidate_orders_empty_when_no_ship_orders` - пустой результат без SHIP заказов
10. `test_consolidate_orders_earliest_latest_dates` - отслеживание дат

#### Взрыв BOM (6 тестов)
1. `test_explode_bom_single_level` - одноуровневый BOM
2. `test_explode_bom_multi_level` - многоуровневый BOM
3. `test_explode_bom_multiple_children` - несколько дочерних продуктов
4. `test_explode_bom_no_children` - продукт без BOM
5. `test_explode_bom_circular_dependency_protection` - защита от циклов
6. `test_explode_bom_quantity_accumulation` - накопление количеств

#### Нетто-потребность (6 тестов)
1. `test_calculate_net_requirement_no_stock` - без запаса
2. `test_calculate_net_requirement_sufficient_stock` - достаточный запас
3. `test_calculate_net_requirement_partial_stock` - частичный запас
4. `test_calculate_net_requirement_ignores_semi_finished` - игнорирование SEMI_FINISHED
5. `test_calculate_net_requirement_ignores_reserved` - исключение резерва
6. `test_calculate_net_requirement_multiple_locations` - несколько локаций

#### Округление до батча (8 тестов)
1. `test_round_to_batch_exact_multiple` - точное кратное
2. `test_round_to_batch_round_up` - округление вверх
3. `test_round_to_batch_below_minimum` - ниже минимума
4. `test_round_to_batch_at_minimum` - на минимуме
5. `test_round_to_batch_between_min_and_step` - между min и step
6. `test_round_to_batch_non_bulk_product` - ошибка для не-BULK
7. `test_round_to_batch_product_not_found` - продукт не найден
8. `test_round_to_batch_no_step_defined` - step не определён

#### Создание зависимых заказов (5 тестов)
1. `test_create_dependent_bulk_order` - создание с родителем
2. `test_create_dependent_bulk_order_without_parent` - без родителя
3. `test_create_dependent_bulk_order_non_bulk_product` - ошибка для не-BULK
4. `test_create_dependent_bulk_order_product_not_found` - продукт не найден
5. `test_create_dependent_bulk_order_unique_number` - уникальность номеров

### MRP API Integration Tests (13 тестов)

1. `test_consolidate_orders_api` - консолидация через API
2. `test_consolidate_orders_api_custom_horizon` - кастомный горизонт
3. `test_explode_bom_api` - взрыв BOM через API
4. `test_explode_bom_api_no_bom` - продукт без BOM
5. `test_explode_bom_api_invalid_product` - невалидный продукт
6. `test_net_requirement_api` - нетто-потребность через API
7. `test_net_requirement_api_with_inventory` - с инвентарём
8. `test_create_bulk_order_api` - создание батч-заказа
9. `test_create_bulk_order_api_without_parent` - без родителя
10. `test_create_bulk_order_api_invalid_product` - невалидный продукт
11. `test_consolidate_orders_api_validation_error` - ошибка валидации
12. `test_explode_bom_api_validation_error` - ошибка валидации
13. `test_net_requirement_api_validation_error` - ошибка валидации

## Статистика тестов

- **Всего тестов:** 124 (48 MRP, 60 Iteration 2.0, 16 MVP v1.0)
- **Unit-тесты моделей:** 25 тестов
- **Unit-тесты сервисов:** 35 тестов (MRPService)
- **Интеграционные API-тесты:** 49 тестов (36 Iteration 2.0 + 13 MRP)
- **Покрытие кода:** 
  - MRPService: **95%** ✅
  - MRP API routes: **79%**
  - Общее покрытие новых моделей и API: **~80%+**
