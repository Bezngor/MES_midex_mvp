# Руководство по генерации тестов для DSIZ модулей

## Обзор

Этот документ описывает стандарты и лучшие практики для создания тестов в модулях DSIZ, основанные на анализе существующих тестов в `backend/tests/models` и типичных ошибках, встречающихся при создании тестов для DSIZ.

## 1. Импорты моделей

### ✅ ПРАВИЛЬНО: Использовать `backend.core.models.*`

```python
from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.production_task import ProductionTask
from backend.core.models.work_center import WorkCenter
from backend.core.models.product import Product
from backend.core.models.manufacturing_route import ManufacturingRoute
from backend.core.models.route_operation import RouteOperation
from backend.core.models.enums import (
    OrderStatus, TaskStatus, WorkCenterStatus, ProductType, OrderPriority
)
```

### ❌ НЕПРАВИЛЬНО: Использовать `backend.src.models.*`

```python
# НЕ ИСПОЛЬЗУЙТЕ для DSIZ тестов!
from backend.src.models.product import Product  # ❌
```

**Примечание:** В `backend/tests/models` используется `backend.src.models.*`, но для DSIZ тестов нужно использовать `backend.core.models.*`.

## 2. Использование Enum

### ✅ ПРАВИЛЬНО: Использовать enum напрямую для полей модели

```python
# Для полей модели (status, product_type и т.д.)
work_center = WorkCenter(
    status=WorkCenterStatus.AVAILABLE,  # ✅ enum напрямую
    ...
)

task = ProductionTask(
    status=TaskStatus.QUEUED,  # ✅ enum напрямую
    ...
)

product = Product(
    product_type=ProductType.FINISHED_GOOD.value,  # ✅ .value для ProductType
    ...
)
```

### ❌ НЕПРАВИЛЬНО: Смешивание enum и .value

```python
# ❌ НЕПРАВИЛЬНО
work_center = WorkCenter(
    status=WorkCenterStatus.AVAILABLE.value,  # ❌
    ...
)

task = ProductionTask(
    status=TaskStatus.QUEUED.value,  # ❌
    ...
)
```

### Правило для Enum:

- **TaskStatus, OrderStatus, WorkCenterStatus**: Используйте enum **напрямую** (без `.value`)
- **ProductType, OrderPriority, BatchStatus**: Используйте **`.value`** (строковое значение)

**Проверка:** Посмотрите на определение enum в `backend/core/models/enums.py`:
- Если enum наследуется от `str, enum.Enum` → используйте `.value` для строковых полей
- Если enum просто `enum.Enum` → используйте enum напрямую

## 3. Обязательные поля моделей

### WorkCenter

```python
work_center = WorkCenter(
    id=uuid4(),  # Опционально (автогенерация)
    name="WC_TUBE_LINE_1",
    resource_type="MACHINE",  # ✅ ОБЯЗАТЕЛЬНО
    status=WorkCenterStatus.AVAILABLE,
    capacity_units_per_hour=100.0,  # ✅ ОБЯЗАТЕЛЬНО
    parallel_capacity=1  # Опционально (по умолчанию 1)
)
```

**Обязательные поля:**
- `name` (String)
- `resource_type` (String) - например, "MACHINE", "STATION"
- `status` (Enum: WorkCenterStatus)
- `capacity_units_per_hour` (Numeric)

### RouteOperation

```python
operation = RouteOperation(
    id=uuid4(),  # Опционально
    route_id=route.id,
    operation_sequence=1,  # ✅ НЕ sequence_number!
    operation_name="Filling",
    work_center_id=work_center.id,  # ✅ ОБЯЗАТЕЛЬНО
    estimated_duration_minutes=480
)
```

**Обязательные поля:**
- `route_id` (UUID)
- `operation_sequence` (Integer) - **НЕ** `sequence_number`!
- `operation_name` (String)
- `work_center_id` (UUID) - **ОБЯЗАТЕЛЬНО**
- `estimated_duration_minutes` (Integer)

### ProductionTask

```python
task = ProductionTask(
    id=uuid4(),  # Опционально
    order_id=order.id,
    operation_id=operation.id,  # ✅ НЕ route_operation_id!
    work_center_id=work_center.id,  # ✅ ОБЯЗАТЕЛЬНО
    status=TaskStatus.QUEUED  # enum напрямую
)
```

**Обязательные поля:**
- `order_id` (UUID)
- `operation_id` (UUID) - **НЕ** `route_operation_id`!
- `work_center_id` (UUID) - **ОБЯЗАТЕЛЬНО** (NOT NULL constraint)
- `status` (Enum: TaskStatus)

**Важно:** `work_center_id` не может быть `None` из-за NOT NULL constraint в БД.

### Product

```python
product = Product(
    id=uuid4(),  # Опционально
    product_code="FG_CREAM_100ML",
    product_name="Крем 100мл",
    product_type=ProductType.FINISHED_GOOD.value,  # ✅ .value
    unit_of_measure="шт"
)
```

**Обязательные поля:**
- `product_code` (String, уникальный)
- `product_name` (String)
- `product_type` (String) - используйте `ProductType.XXX.value`
- `unit_of_measure` (String)

### ManufacturingOrder

```python
order = ManufacturingOrder(
    id=uuid4(),  # Опционально
    order_number="ORD-001",
    product_id=str(product.id),  # Может быть UUID или product_code (String)
    quantity=1000.0,
    status=OrderStatus.RELEASED,  # enum напрямую
    priority=OrderPriority.NORMAL.value,  # ✅ .value
    due_date=datetime.now(timezone.utc) + timedelta(days=5)
)
```

**Обязательные поля:**
- `order_number` (String)
- `product_id` (String) - UUID или product_code
- `quantity` (Numeric)
- `status` (Enum: OrderStatus) - enum напрямую

### ManufacturingRoute

```python
route = ManufacturingRoute(
    id=uuid4(),  # Опционально
    product_id=str(product.id),  # String (UUID или product_code)
    route_name="Filling Route"
)
```

**Обязательные поля:**
- `product_id` (String)
- `route_name` (String)

## 4. Стандартная структура теста

### Шаблон создания объектов

```python
def test_example(client, test_db):
    """Описание теста."""
    from datetime import datetime, timezone, timedelta
    from uuid import uuid4
    
    # 1. Создаём базовые объекты (Product, WorkCenter)
    product = Product(
        id=uuid4(),
        product_code="FG_CREAM_100ML",
        product_name="Крем 100мл",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="шт"
    )
    test_db.add(product)
    test_db.commit()
    
    work_center = WorkCenter(
        id=uuid4(),
        name="WC_TUBE_LINE_1",
        resource_type="MACHINE",  # ✅ ОБЯЗАТЕЛЬНО
        status=WorkCenterStatus.AVAILABLE,
        capacity_units_per_hour=100.0,  # ✅ ОБЯЗАТЕЛЬНО
        parallel_capacity=1
    )
    test_db.add(work_center)
    test_db.commit()
    
    # 2. Создаём зависимые объекты (Order, Route, Operation)
    order = ManufacturingOrder(
        id=uuid4(),
        order_number="ORD-001",
        product_id=str(product.id),
        quantity=1000.0,
        status=OrderStatus.RELEASED,
        priority=OrderPriority.NORMAL.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=5)
    )
    test_db.add(order)
    test_db.commit()
    
    route = ManufacturingRoute(
        id=uuid4(),
        product_id=str(product.id),
        route_name="Filling Route"
    )
    test_db.add(route)
    test_db.commit()
    
    operation = RouteOperation(
        id=uuid4(),
        route_id=route.id,
        operation_sequence=1,  # ✅ НЕ sequence_number
        operation_name="Filling",
        work_center_id=work_center.id,  # ✅ ОБЯЗАТЕЛЬНО
        estimated_duration_minutes=480
    )
    test_db.add(operation)
    test_db.commit()
    
    # 3. Создаём тестовые объекты (Task)
    task = ProductionTask(
        id=uuid4(),
        order_id=order.id,
        operation_id=operation.id,  # ✅ НЕ route_operation_id
        work_center_id=work_center.id,  # ✅ ОБЯЗАТЕЛЬНО
        status=TaskStatus.QUEUED  # enum напрямую
    )
    test_db.add(task)
    test_db.commit()
    
    # 4. Выполняем тест
    response = client.post("/api/v1/dsiz/dispatching/run", json={
        "manufacturing_order_ids": [str(order.id)]
    })
    
    # 5. Проверки
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
```

### Обязательные шаги при создании объектов

1. **Создание объекта** через конструктор модели
2. **Добавление в сессию**: `test_db.add(object)`
3. **Коммит**: `test_db.commit()`
4. **Обновление** (если нужен ID): `test_db.refresh(object)`

## 5. Типичные ошибки и их решения

### Ошибка 1: NOT NULL constraint failed

**Симптом:**
```
sqlalchemy.exc.IntegrityError: NOT NULL constraint failed: work_centers.resource_type
```

**Причина:** Отсутствует обязательное поле `resource_type` или `capacity_units_per_hour` в `WorkCenter`.

**Решение:**
```python
work_center = WorkCenter(
    name="WC_TUBE_LINE_1",
    resource_type="MACHINE",  # ✅ Добавить
    capacity_units_per_hour=100.0,  # ✅ Добавить
    status=WorkCenterStatus.AVAILABLE,
    parallel_capacity=1
)
```

### Ошибка 2: Invalid keyword argument

**Симптом:**
```
TypeError: 'sequence_number' is an invalid keyword argument for RouteOperation
```

**Причина:** Использовано неправильное имя поля.

**Решение:**
```python
# ❌ НЕПРАВИЛЬНО
operation = RouteOperation(
    sequence_number=1,  # ❌
    ...
)

# ✅ ПРАВИЛЬНО
operation = RouteOperation(
    operation_sequence=1,  # ✅
    ...
)
```

### Ошибка 3: Invalid keyword argument для ProductionTask

**Симптом:**
```
TypeError: 'route_operation_id' is an invalid keyword argument for ProductionTask
```

**Причина:** Использовано неправильное имя поля.

**Решение:**
```python
# ❌ НЕПРАВИЛЬНО
task = ProductionTask(
    route_operation_id=operation.id,  # ❌
    ...
)

# ✅ ПРАВИЛЬНО
task = ProductionTask(
    operation_id=operation.id,  # ✅
    ...
)
```

### Ошибка 4: Enum comparison error

**Симптом:**
```
AssertionError: assert TaskStatus.QUEUED.value == TaskStatus.IN_PROGRESS
```

**Причина:** Смешивание enum и `.value` при сравнении.

**Решение:**
```python
# ✅ ПРАВИЛЬНО
assert task.status == TaskStatus.IN_PROGRESS  # enum напрямую

# ❌ НЕПРАВИЛЬНО
assert task.status == TaskStatus.IN_PROGRESS.value  # ❌
```

### Ошибка 5: HTTPException не перехватывается

**Симптом:**
```
assert 500 == 404  # Ожидается 404, получается 500
```

**Причина:** HTTPException перехватывается общим `except Exception`.

**Решение:**
```python
try:
    # код
except HTTPException:
    # Перебрасываем HTTPException как есть
    raise
except ValueError as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(e)
    )
except Exception as e:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Ошибка: {str(e)}"
    )
```

## 6. Чек-лист перед созданием теста

- [ ] Использованы правильные импорты: `backend.core.models.*`
- [ ] Все обязательные поля заполнены:
  - [ ] `WorkCenter`: `resource_type`, `capacity_units_per_hour`
  - [ ] `RouteOperation`: `operation_sequence` (не `sequence_number`), `work_center_id`
  - [ ] `ProductionTask`: `operation_id` (не `route_operation_id`), `work_center_id`
- [ ] Enum используются правильно:
  - [ ] `TaskStatus`, `OrderStatus`, `WorkCenterStatus` - без `.value`
  - [ ] `ProductType`, `OrderPriority` - с `.value`
- [ ] Объекты созданы в правильном порядке (зависимости сначала)
- [ ] Выполнены все шаги: `add()`, `commit()`, `refresh()` (если нужно)
- [ ] HTTPException перехватывается отдельно от общих исключений

## 7. Примеры правильных тестов

### Пример 1: Тест создания задачи

```python
def test_create_task_success(client, test_db):
    """Тест: успешное создание задачи."""
    from datetime import datetime, timezone, timedelta
    from uuid import uuid4
    
    # Product
    product = Product(
        id=uuid4(),
        product_code="FG_CREAM_100ML",
        product_name="Крем 100мл",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="шт"
    )
    test_db.add(product)
    test_db.commit()
    
    # WorkCenter
    work_center = WorkCenter(
        id=uuid4(),
        name="WC_TUBE_LINE_1",
        resource_type="MACHINE",
        status=WorkCenterStatus.AVAILABLE,
        capacity_units_per_hour=100.0,
        parallel_capacity=1
    )
    test_db.add(work_center)
    test_db.commit()
    
    # Order
    order = ManufacturingOrder(
        id=uuid4(),
        order_number="ORD-001",
        product_id=str(product.id),
        quantity=1000.0,
        status=OrderStatus.RELEASED,
        due_date=datetime.now(timezone.utc) + timedelta(days=5)
    )
    test_db.add(order)
    test_db.commit()
    
    # Route
    route = ManufacturingRoute(
        id=uuid4(),
        product_id=str(product.id),
        route_name="Filling Route"
    )
    test_db.add(route)
    test_db.commit()
    
    # Operation
    operation = RouteOperation(
        id=uuid4(),
        route_id=route.id,
        operation_sequence=1,
        operation_name="Filling",
        work_center_id=work_center.id,
        estimated_duration_minutes=480
    )
    test_db.add(operation)
    test_db.commit()
    
    # Task
    task = ProductionTask(
        id=uuid4(),
        order_id=order.id,
        operation_id=operation.id,
        work_center_id=work_center.id,
        status=TaskStatus.QUEUED
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    
    # Проверки
    assert task.id is not None
    assert task.status == TaskStatus.QUEUED
    assert task.work_center_id == work_center.id
```

### Пример 2: Тест API endpoint

```python
def test_dispatch_task_success(client, test_db):
    """Тест: успешная диспетчеризация задачи."""
    from datetime import datetime, timezone, timedelta
    from uuid import uuid4
    
    # Создаём все необходимые объекты (как в примере 1)
    # ...
    
    # Выполняем запрос
    response = client.post(f"/api/v1/dsiz/dispatching/dispatch-task/{task.id}")
    
    # Проверки
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["task"]["status"] == "IN_PROGRESS"
    
    # Проверка в БД
    test_db.refresh(task)
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.started_at is not None
```

## 8. Полезные фикстуры из conftest.py

Если объекты создаются часто, можно использовать фикстуры из `backend/tests/conftest.py`:

```python
def test_with_fixtures(client, test_db, sample_bulk_product, sample_work_centers):
    """Тест с использованием фикстур."""
    # sample_bulk_product уже создан
    # sample_work_centers - список из 3 WorkCenter
    
    # Используем готовые объекты
    order = ManufacturingOrder(
        order_number="ORD-001",
        product_id=str(sample_bulk_product.id),
        quantity=1000.0,
        status=OrderStatus.RELEASED
    )
    test_db.add(order)
    test_db.commit()
    # ...
```

**Доступные фикстуры:**
- `sample_bulk_product` - BULK продукт
- `sample_finished_good` - FINISHED_GOOD продукт
- `sample_work_centers` - список из 3 WorkCenter
- `sample_manufacturing_order` - ManufacturingOrder
- И другие (см. `backend/tests/conftest.py`)

## 9. Отладка тестов

### Проверка структуры модели

Если не уверены в полях модели, проверьте определение:

```python
# backend/core/models/production_task.py
class ProductionTask(Base):
    operation_id = Column(...)  # ✅ Правильное имя
    # НЕТ route_operation_id!
```

### Проверка enum

```python
# backend/core/models/enums.py
class TaskStatus(str, enum.Enum):  # str enum - может использовать .value
    QUEUED = "QUEUED"
    
# Но в модели используется Enum(TaskStatus), поэтому используйте enum напрямую
```

### Запуск одного теста для отладки

```bash
pytest backend/tests/customizations/dsiz/test_dsiz_dispatching_routes.py::test_name -v --tb=short
```

## 10. Резюме правил

1. **Импорты**: `backend.core.models.*` (не `backend.src.models.*`)
2. **Enum**: 
   - `TaskStatus`, `OrderStatus`, `WorkCenterStatus` → без `.value`
   - `ProductType`, `OrderPriority` → с `.value`
3. **Поля**:
   - `RouteOperation.operation_sequence` (не `sequence_number`)
   - `ProductionTask.operation_id` (не `route_operation_id`)
   - `WorkCenter.resource_type` и `capacity_units_per_hour` обязательны
   - `ProductionTask.work_center_id` обязателен (NOT NULL)
4. **Порядок**: Создавайте объекты в порядке зависимостей
5. **Шаги**: `add()` → `commit()` → `refresh()` (если нужно)
6. **Ошибки**: Перехватывайте `HTTPException` отдельно

---

**Дата создания:** 2026-01-26  
**Версия:** 1.0  
**Автор:** На основе анализа `backend/tests/models` и типичных ошибок в DSIZ тестах
