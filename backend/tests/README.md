# Backend Tests

Автоматизированные pytest-тесты для backend API MES платформы.

## Структура тестов

- `conftest.py` - общие fixtures (тестовая БД, клиент, тестовые данные)
- `test_order_service.py` - unit-тесты для OrderService (5 тестов)
- `test_task_service.py` - unit-тесты для TaskService (6 тестов)
- `test_api_integration.py` - интеграционные API-тесты (5 тестов)

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
pytest
```

С подробным выводом:
```bash
pytest -v
```

С покрытием:
```bash
pytest --cov=backend.src --cov-report=html
```

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

- `test_db` - тестовая БД-сессия с автоматическим rollback
- `client` - FastAPI TestClient для интеграционных тестов
- `sample_work_centers` - 3 WorkCenter для использования в тестах
- `sample_route` - ManufacturingRoute с 3 RouteOperations
