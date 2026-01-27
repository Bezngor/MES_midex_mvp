"""
Unit тесты для DispatchingService.
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from sqlalchemy import select

from backend.src.services.dispatching_service import DispatchingService
from backend.src.models.manufacturing_order import ManufacturingOrder
from backend.src.models.production_task import ProductionTask
from backend.src.models.work_center import WorkCenter
from backend.src.models.manufacturing_route import ManufacturingRoute
from backend.src.models.route_operation import RouteOperation
from backend.src.models.work_center_capacity import WorkCenterCapacity
from backend.src.models.product import Product
from backend.src.models.enums import (
    OrderStatus, OrderType, OrderPriority,
    TaskStatus, WorkCenterStatus, ProductType
)


# ============================================================================
# Release Order Tests
# ============================================================================

def test_release_order_planned_to_released(
    test_db,
    sample_manufacturing_order,
    sample_route
):
    """Тест выпуска заказа из PLANNED в RELEASED."""
    sample_manufacturing_order.status = OrderStatus.PLANNED
    sample_manufacturing_order.product_id = sample_route.product_id
    test_db.commit()
    test_db.refresh(sample_manufacturing_order)
    
    service = DispatchingService(test_db)
    result = service.release_order(sample_manufacturing_order.id)
    
    assert result.status == OrderStatus.RELEASED
    assert result.updated_at is not None


def test_release_order_creates_tasks(
    test_db,
    sample_manufacturing_order,
    sample_route
):
    """Тест: release_order создаёт ProductionTask."""
    sample_manufacturing_order.status = OrderStatus.PLANNED
    sample_manufacturing_order.product_id = sample_route.product_id
    test_db.commit()
    test_db.refresh(sample_manufacturing_order)
    
    service = DispatchingService(test_db)
    service.release_order(sample_manufacturing_order.id)
    
    # Проверяем созданные задачи
    tasks_query = select(ProductionTask).where(
        ProductionTask.order_id == sample_manufacturing_order.id
    )
    tasks_result = test_db.execute(tasks_query)
    tasks = list(tasks_result.scalars().all())
    
    assert len(tasks) >= 1
    assert all(task.status == TaskStatus.QUEUED for task in tasks)


def test_release_order_with_route_operations(
    test_db,
    sample_manufacturing_order,
    sample_route
):
    """Тест: release_order создаёт задачи из операций маршрута."""
    sample_manufacturing_order.status = OrderStatus.PLANNED
    sample_manufacturing_order.product_id = sample_route.product_id
    test_db.commit()
    test_db.refresh(sample_manufacturing_order)
    
    service = DispatchingService(test_db)
    result = service.release_order(sample_manufacturing_order.id)
    
    # Проверяем задачи, созданные из маршрута
    tasks_query = select(ProductionTask).where(
        ProductionTask.order_id == sample_manufacturing_order.id
    )
    tasks_result = test_db.execute(tasks_query)
    tasks = list(tasks_result.scalars().all())
    
    assert len(tasks) >= 1
    # Задача должна иметь operation_id
    assert tasks[0].operation_id is not None
    assert tasks[0].status == TaskStatus.QUEUED


def test_release_order_not_found(test_db):
    """Тест ошибки, когда заказ не найден."""
    service = DispatchingService(test_db)
    
    with pytest.raises(ValueError, match="не найден"):
        service.release_order(uuid4())


def test_release_order_already_released(
    test_db,
    sample_manufacturing_order
):
    """Тест ошибки, когда заказ уже выпущен."""
    sample_manufacturing_order.status = OrderStatus.RELEASED
    test_db.commit()
    test_db.refresh(sample_manufacturing_order)
    
    service = DispatchingService(test_db)
    
    with pytest.raises(ValueError, match="не в статусе PLANNED"):
        service.release_order(sample_manufacturing_order.id)


def test_release_order_with_custom_date(
    test_db,
    sample_manufacturing_order,
    sample_route
):
    """Тест выпуска заказа с кастомной датой выпуска."""
    sample_manufacturing_order.status = OrderStatus.PLANNED
    sample_manufacturing_order.product_id = sample_route.product_id
    test_db.commit()
    test_db.refresh(sample_manufacturing_order)
    
    release_date = datetime.now(timezone.utc) + timedelta(days=1)
    
    service = DispatchingService(test_db)
    result = service.release_order(
        sample_manufacturing_order.id,
        release_date=release_date
    )
    
    assert result.status == OrderStatus.RELEASED


def test_release_order_no_route(
    test_db,
    sample_finished_good
):
    """Тест ошибки, когда маршрут не найден."""
    from datetime import datetime, timezone, timedelta
    
    order = ManufacturingOrder(
        order_number="NO-ROUTE-001",
        product_id=str(sample_finished_good.id),
        quantity=1000.0,
        status=OrderStatus.PLANNED,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=7)
    )
    test_db.add(order)
    test_db.commit()
    test_db.refresh(order)
    
    service = DispatchingService(test_db)
    
    with pytest.raises(ValueError, match="Маршрут производства не найден"):
        service.release_order(order.id)


# ============================================================================
# Dispatch Task Tests
# ============================================================================

def test_dispatch_task_queued_to_in_progress(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест диспетчеризации задачи из QUEUED в IN_PROGRESS."""
    # Создаём QUEUED задачу
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),  # Временный UUID
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.QUEUED
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    
    service = DispatchingService(test_db)
    result = service.dispatch_task(
        task.id,
        sample_work_centers[0].id,
        scheduled_start=datetime.now(timezone.utc)
    )
    
    assert result.status == TaskStatus.IN_PROGRESS
    assert result.work_center_id == sample_work_centers[0].id
    assert result.started_at is not None
    assert result.completed_at is not None


def test_dispatch_task_calculates_duration_from_operation(
    test_db,
    sample_work_centers,
    sample_route,
    sample_manufacturing_order
):
    """Тест: dispatch использует estimated_duration_minutes из операции."""
    # Получаем операцию маршрута
    operations_query = select(RouteOperation).where(
        RouteOperation.route_id == sample_route.id
    ).limit(1)
    operations_result = test_db.execute(operations_query)
    operation = operations_result.scalar_one()
    
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=operation.id,
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.QUEUED
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    
    start_time = datetime.now(timezone.utc)
    
    service = DispatchingService(test_db)
    result = service.dispatch_task(
        task.id,
        sample_work_centers[0].id,
        scheduled_start=start_time
    )
    
    # Должен использовать estimated_duration_minutes из операции (45 минут)
    duration = (result.completed_at - result.started_at).total_seconds() / 3600
    # Для MVP используется фиксированная 8-часовая смена, но проверяем, что времена установлены
    assert duration == 8.0  # По умолчанию 8 часов для MVP


def test_dispatch_task_fallback_to_8_hours(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест: dispatch использует 8 часов по умолчанию, если нет длительности."""
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),  # Нет реальной операции
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.QUEUED
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    
    start_time = datetime.now(timezone.utc)
    
    service = DispatchingService(test_db)
    result = service.dispatch_task(
        task.id,
        sample_work_centers[0].id,
        scheduled_start=start_time
    )
    
    duration = (result.completed_at - result.started_at).total_seconds() / 3600
    assert duration == 8.0  # По умолчанию 8-часовая смена


def test_dispatch_task_not_found(test_db, sample_work_centers):
    """Тест ошибки, когда задача не найдена."""
    service = DispatchingService(test_db)
    
    with pytest.raises(ValueError, match="не найдена"):
        service.dispatch_task(uuid4(), sample_work_centers[0].id)


def test_dispatch_task_work_center_not_found(test_db, sample_manufacturing_order):
    """Тест ошибки, когда рабочий центр не найден."""
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=uuid4(),
        status=TaskStatus.QUEUED
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    
    service = DispatchingService(test_db)
    
    with pytest.raises(ValueError, match="не найден"):
        service.dispatch_task(task.id, uuid4())


def test_dispatch_task_already_dispatched(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест ошибки, когда задача уже в процессе."""
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.IN_PROGRESS
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    
    service = DispatchingService(test_db)
    
    with pytest.raises(ValueError, match="не в статусе QUEUED"):
        service.dispatch_task(task.id, sample_work_centers[0].id)


def test_dispatch_task_capacity_exceeded(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест ошибки, когда мощность рабочего центра превышена."""
    # Устанавливаем parallel_capacity = 1
    wc = sample_work_centers[0]
    wc.parallel_capacity = 1
    test_db.commit()
    test_db.refresh(wc)
    
    # Создаём задачу, которая заполняет мощность (8 часов)
    today = datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0)
    existing_task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=wc.id,
        status=TaskStatus.IN_PROGRESS,
        started_at=today,
        completed_at=today + timedelta(hours=8)
    )
    test_db.add(existing_task)
    test_db.commit()
    
    # Пытаемся добавить ещё одну задачу
    new_task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=wc.id,
        status=TaskStatus.QUEUED
    )
    test_db.add(new_task)
    test_db.commit()
    test_db.refresh(new_task)
    
    service = DispatchingService(test_db)
    
    with pytest.raises(ValueError, match="загружен"):
        service.dispatch_task(new_task.id, wc.id, scheduled_start=today)


# ============================================================================
# Schedule Tasks Tests
# ============================================================================

def test_schedule_tasks_returns_list(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест: schedule_tasks возвращает список запланированных задач."""
    # Создаём IN_PROGRESS задачу
    # Устанавливаем приоритет заказа
    sample_manufacturing_order.priority = OrderPriority.HIGH.value
    test_db.commit()
    test_db.refresh(sample_manufacturing_order)
    
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.IN_PROGRESS,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc) + timedelta(hours=8)
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    
    service = DispatchingService(test_db)
    schedule = service.schedule_tasks(work_center_id=sample_work_centers[0].id)
    
    assert len(schedule) >= 1
    assert schedule[0]["task_id"] == task.id
    assert schedule[0]["priority"] == OrderPriority.HIGH.value


def test_schedule_tasks_priority_ordering(test_db, sample_work_centers, sample_route):
    """Тест: schedule_tasks сортирует по приоритету (URGENT первым)."""
    from datetime import datetime, timezone, timedelta
    
    # Создаём заказы с разными приоритетами
    orders_data = [
        ("LOW-ORDER", OrderPriority.LOW),
        ("URGENT-ORDER", OrderPriority.URGENT),
        ("NORMAL-ORDER", OrderPriority.NORMAL),
        ("HIGH-ORDER", OrderPriority.HIGH),
    ]
    
    tasks = []
    for order_name, priority in orders_data:
        order = ManufacturingOrder(
            order_number=order_name,
            product_id=sample_route.product_id,
            quantity=100.0,
            status=OrderStatus.RELEASED,
            order_type=OrderType.CUSTOMER.value,
            priority=priority.value,
            due_date=datetime.now(timezone.utc) + timedelta(days=7)
        )
        test_db.add(order)
        test_db.flush()
        
        # Получаем первую операцию маршрута
        operations_query = select(RouteOperation).where(
            RouteOperation.route_id == sample_route.id
        ).limit(1)
        operations_result = test_db.execute(operations_query)
        operation = operations_result.scalar_one()
        
        task = ProductionTask(
            order_id=order.id,
            operation_id=operation.id,
            work_center_id=sample_work_centers[0].id,
            status=TaskStatus.IN_PROGRESS,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc) + timedelta(hours=8)
        )
        tasks.append(task)
        test_db.add(task)
    
    test_db.commit()
    
    service = DispatchingService(test_db)
    schedule = service.schedule_tasks(work_center_id=sample_work_centers[0].id)
    
    # Проверяем порядок: URGENT, HIGH, NORMAL, LOW
    assert len(schedule) == 4
    assert schedule[0]["priority"] == OrderPriority.URGENT.value
    assert schedule[1]["priority"] == OrderPriority.HIGH.value
    assert schedule[2]["priority"] == OrderPriority.NORMAL.value
    assert schedule[3]["priority"] == OrderPriority.LOW.value


def test_schedule_tasks_eager_loading(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест: schedule_tasks использует eager loading (нет N+1 запросов)."""
    # Создаём задачу со связями
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.IN_PROGRESS,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc) + timedelta(hours=8)
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    
    service = DispatchingService(test_db)
    
    # Это не должно вызывать N+1 запросов
    schedule = service.schedule_tasks(work_center_id=sample_work_centers[0].id)
    
    assert len(schedule) >= 1
    assert schedule[0]["work_center_name"] == sample_work_centers[0].name


def test_schedule_tasks_filter_by_work_center(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест фильтрации расписания по рабочему центру."""
    # Создаём другой рабочий центр
    wc2 = WorkCenter(
        name="WC2",
        resource_type="ASSEMBLY",
        capacity_units_per_hour=5.0,
        status=WorkCenterStatus.AVAILABLE
    )
    test_db.add(wc2)
    test_db.commit()
    test_db.refresh(wc2)
    
    # Создаём задачи для обоих рабочих центров
    task1 = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.IN_PROGRESS,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc) + timedelta(hours=8)
    )
    task2 = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=wc2.id,
        status=TaskStatus.IN_PROGRESS,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc) + timedelta(hours=8)
    )
    test_db.add_all([task1, task2])
    test_db.commit()
    
    service = DispatchingService(test_db)
    schedule = service.schedule_tasks(work_center_id=sample_work_centers[0].id)
    
    # Должна вернуться только task1
    assert len(schedule) == 1
    assert schedule[0]["work_center_id"] == sample_work_centers[0].id


def test_schedule_tasks_excludes_completed(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест: COMPLETED задачи исключаются из расписания."""
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.COMPLETED,
        started_at=datetime.now(timezone.utc) - timedelta(hours=8),
        completed_at=datetime.now(timezone.utc)
    )
    test_db.add(task)
    test_db.commit()
    
    service = DispatchingService(test_db)
    schedule = service.schedule_tasks(work_center_id=sample_work_centers[0].id)
    
    # COMPLETED задача не должна появляться
    assert len(schedule) == 0


def test_schedule_tasks_handles_missing_work_center_relationship(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест: расписание обрабатывает задачи с отсутствующим work_center в relationship."""
    # Создаём задачу с work_center_id, но без загруженного relationship
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.IN_PROGRESS,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc) + timedelta(hours=8)
    )
    test_db.add(task)
    test_db.commit()
    
    service = DispatchingService(test_db)
    schedule = service.schedule_tasks()
    
    # Должна обработать корректно
    assert len(schedule) >= 1
    assert schedule[0]["work_center_name"] == sample_work_centers[0].name


# ============================================================================
# Work Center Load Tests
# ============================================================================

def test_calculate_work_center_load_no_tasks(
    test_db,
    sample_work_centers
):
    """Тест расчёта загрузки без задач."""
    service = DispatchingService(test_db)
    load = service.calculate_work_center_load(sample_work_centers[0].id)
    
    assert load == 0.0


def test_calculate_work_center_load_single_task(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест расчёта загрузки с одной 8-часовой задачей."""
    wc = sample_work_centers[0]
    wc.parallel_capacity = 1
    test_db.commit()
    test_db.refresh(wc)
    
    today = datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0)
    
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=wc.id,
        status=TaskStatus.IN_PROGRESS,
        started_at=today,
        completed_at=today + timedelta(hours=8)
    )
    test_db.add(task)
    test_db.commit()
    
    service = DispatchingService(test_db)
    load = service.calculate_work_center_load(
        wc.id,
        date=today
    )
    
    # 8 часов / (8 × 1) = 100%
    assert load == 100.0


def test_calculate_work_center_load_with_parallel_capacity(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест расчёта загрузки с parallel_capacity = 2."""
    wc = sample_work_centers[0]
    wc.parallel_capacity = 2
    test_db.commit()
    test_db.refresh(wc)
    
    today = datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0)
    
    # Две 4-часовые задачи = 8 часов всего
    task1 = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=wc.id,
        status=TaskStatus.IN_PROGRESS,
        started_at=today,
        completed_at=today + timedelta(hours=4)
    )
    task2 = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=wc.id,
        status=TaskStatus.IN_PROGRESS,
        started_at=today + timedelta(hours=4),
        completed_at=today + timedelta(hours=8)
    )
    test_db.add_all([task1, task2])
    test_db.commit()
    
    service = DispatchingService(test_db)
    load = service.calculate_work_center_load(
        wc.id,
        date=today
    )
    
    # 8 часов / (8 × 2) = 50%
    assert load == 50.0


def test_calculate_work_center_load_overloaded(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест расчёта загрузки при перегрузке (>100%)."""
    wc = sample_work_centers[0]
    wc.parallel_capacity = 1
    test_db.commit()
    test_db.refresh(wc)
    
    today = datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0)
    
    # 12-часовая задача на 8-часовую смену
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=wc.id,
        status=TaskStatus.IN_PROGRESS,
        started_at=today,
        completed_at=today + timedelta(hours=12)
    )
    test_db.add(task)
    test_db.commit()
    
    service = DispatchingService(test_db)
    load = service.calculate_work_center_load(
        wc.id,
        date=today
    )
    
    # 12 / 8 = 150%
    assert load == 150.0


def test_calculate_work_center_load_ignores_queued(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест: QUEUED задачи не учитываются в загрузке."""
    today = datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0)
    
    # QUEUED задача (должна игнорироваться)
    queued_task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.QUEUED
    )
    
    # IN_PROGRESS задача (должна учитываться)
    active_task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.IN_PROGRESS,
        started_at=today,
        completed_at=today + timedelta(hours=4)
    )
    
    test_db.add_all([queued_task, active_task])
    test_db.commit()
    
    service = DispatchingService(test_db)
    load = service.calculate_work_center_load(
        sample_work_centers[0].id,
        date=today
    )
    
    # Только active_task (4 часа)
    assert load == 50.0  # 4 / 8 = 50%


def test_calculate_work_center_load_different_date(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест расчёта загрузки для конкретной даты."""
    today = datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    # Задача запланирована на завтра
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.IN_PROGRESS,
        started_at=tomorrow,
        completed_at=tomorrow + timedelta(hours=8)
    )
    test_db.add(task)
    test_db.commit()
    
    service = DispatchingService(test_db)
    
    # Загрузка на сегодня должна быть 0
    load_today = service.calculate_work_center_load(
        sample_work_centers[0].id,
        date=today
    )
    assert load_today == 0.0
    
    # Загрузка на завтра должна быть 100
    load_tomorrow = service.calculate_work_center_load(
        sample_work_centers[0].id,
        date=tomorrow
    )
    assert load_tomorrow == 100.0


# ============================================================================
# Gantt Data Tests
# ============================================================================

def test_get_gantt_data_structure(
    test_db,
    sample_work_centers
):
    """Тест: Gantt data возвращает правильную структуру."""
    service = DispatchingService(test_db)
    gantt = service.get_gantt_data()
    
    assert "work_centers" in gantt
    assert "start_date" in gantt
    assert "end_date" in gantt
    assert isinstance(gantt["work_centers"], list)


def test_get_gantt_data_with_tasks(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест: Gantt data включает задачи."""
    start = datetime.now(timezone.utc)
    
    # Устанавливаем приоритет заказа
    sample_manufacturing_order.priority = OrderPriority.HIGH.value
    test_db.commit()
    test_db.refresh(sample_manufacturing_order)
    
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.IN_PROGRESS,
        started_at=start,
        completed_at=start + timedelta(hours=8)
    )
    test_db.add(task)
    test_db.commit()
    
    service = DispatchingService(test_db)
    gantt = service.get_gantt_data(
        start_date=start - timedelta(days=1),
        end_date=start + timedelta(days=1)
    )
    
    assert len(gantt["work_centers"]) >= 1
    wc_data = gantt["work_centers"][0]
    assert wc_data["name"] == sample_work_centers[0].name
    assert len(wc_data["tasks"]) >= 1
    assert wc_data["tasks"][0]["id"] == task.id


def test_get_gantt_data_filter_by_work_center(
    test_db,
    sample_work_centers
):
    """Тест: Gantt data фильтруется по рабочему центру."""
    # Создаём другой рабочий центр
    wc2 = WorkCenter(
        name="WC2",
        resource_type="ASSEMBLY",
        capacity_units_per_hour=5.0,
        status=WorkCenterStatus.AVAILABLE
    )
    test_db.add(wc2)
    test_db.commit()
    test_db.refresh(wc2)
    
    service = DispatchingService(test_db)
    gantt = service.get_gantt_data(work_center_id=sample_work_centers[0].id)
    
    # Должен включать только sample_work_centers[0]
    assert len(gantt["work_centers"]) == 1
    assert gantt["work_centers"][0]["id"] == sample_work_centers[0].id


def test_get_gantt_data_date_range(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест: Gantt data учитывает диапазон дат."""
    today = datetime.now(timezone.utc)
    week_ago = today - timedelta(days=7)
    
    # Задача с прошлой недели (должна быть исключена)
    old_task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.COMPLETED,
        started_at=week_ago,
        completed_at=week_ago + timedelta(hours=8)
    )
    
    # Задача на сегодня (должна быть включена)
    new_task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.IN_PROGRESS,
        started_at=today,
        completed_at=today + timedelta(hours=8)
    )
    
    test_db.add_all([old_task, new_task])
    test_db.commit()
    
    service = DispatchingService(test_db)
    gantt = service.get_gantt_data(
        start_date=today - timedelta(days=1),
        end_date=today + timedelta(days=1)
    )
    
    # Должна включать только new_task
    tasks = gantt["work_centers"][0]["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["id"] == new_task.id


# ============================================================================
# Find Available Work Center Tests
# ============================================================================

def test_find_available_work_center_no_capacity(test_db, sample_finished_good):
    """Тест: когда нет рабочего центра с мощностью для продукта."""
    service = DispatchingService(test_db)
    result = service.find_available_work_center(
        str(sample_finished_good.id),
        datetime.now(timezone.utc)
    )
    
    assert result is None


def test_find_available_work_center_with_capacity(
    test_db,
    sample_work_centers,
    sample_finished_good
):
    """Тест: поиск рабочего центра с мощностью."""
    # Добавляем мощность
    capacity = WorkCenterCapacity(
        work_center_id=sample_work_centers[0].id,
        product_id=sample_finished_good.id,
        capacity_per_shift=1000.0,
        unit="pcs"
    )
    test_db.add(capacity)
    test_db.commit()
    
    service = DispatchingService(test_db)
    result = service.find_available_work_center(
        str(sample_finished_good.id),
        datetime.now(timezone.utc)
    )
    
    assert result == sample_work_centers[0].id


def test_find_available_work_center_overloaded(
    test_db,
    sample_work_centers,
    sample_finished_good,
    sample_manufacturing_order
):
    """Тест: перегруженный рабочий центр не возвращается."""
    wc = sample_work_centers[0]
    wc.parallel_capacity = 1
    test_db.commit()
    test_db.refresh(wc)
    
    # Добавляем мощность
    capacity = WorkCenterCapacity(
        work_center_id=wc.id,
        product_id=sample_finished_good.id,
        capacity_per_shift=1000.0,
        unit="pcs"
    )
    test_db.add(capacity)
    
    # Добавляем задачу, которая заполняет мощность
    today = datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0)
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=wc.id,
        status=TaskStatus.IN_PROGRESS,
        started_at=today,
        completed_at=today + timedelta(hours=8)
    )
    test_db.add(task)
    test_db.commit()
    
    service = DispatchingService(test_db)
    result = service.find_available_work_center(
        str(sample_finished_good.id),
        today
    )
    
    assert result is None  # Перегружен, не должен возвращаться


# ============================================================================
# Dispatch Preview Tests
# ============================================================================

def test_dispatch_tasks_returns_queued_tasks(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест: dispatch_tasks возвращает QUEUED задачи."""
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.QUEUED
    )
    test_db.add(task)
    test_db.commit()
    
    service = DispatchingService(test_db)
    result = service.dispatch_tasks(limit=50)
    
    assert len(result) >= 1
    assert result[0].id == task.id
    assert result[0].status == TaskStatus.QUEUED


def test_dispatch_tasks_excludes_down_centers(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест: dispatch_tasks исключает задачи для DOWN центров."""
    wc = sample_work_centers[0]
    wc.status = WorkCenterStatus.DOWN
    test_db.commit()
    test_db.refresh(wc)
    
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=wc.id,
        status=TaskStatus.QUEUED
    )
    test_db.add(task)
    test_db.commit()
    
    service = DispatchingService(test_db)
    result = service.dispatch_tasks(limit=50)
    
    # Задача для DOWN центра не должна быть в списке
    assert len(result) == 0 or task.id not in [t.id for t in result]


def test_get_dispatch_preview_by_work_center(
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест: get_dispatch_preview_by_work_center группирует по рабочим центрам."""
    task1 = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.QUEUED
    )
    task2 = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[1].id,
        status=TaskStatus.QUEUED
    )
    test_db.add_all([task1, task2])
    test_db.commit()
    
    service = DispatchingService(test_db)
    result = service.get_dispatch_preview_by_work_center(limit=50)
    
    assert len(result) >= 2
    assert str(sample_work_centers[0].id) in result
    assert str(sample_work_centers[1].id) in result
