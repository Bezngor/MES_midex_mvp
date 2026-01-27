"""
Интеграционные тесты для DSIZ Dispatching API endpoints.
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.production_task import ProductionTask
from backend.core.models.work_center import WorkCenter
from backend.core.models.product import Product
from backend.core.models.manufacturing_route import ManufacturingRoute
from backend.core.models.route_operation import RouteOperation
from backend.core.models.enums import (
    OrderStatus, TaskStatus, WorkCenterStatus, ProductType, OrderPriority
)


def test_run_dispatch_preview_success(client, test_db):
    """Тест: успешный запуск preview диспетчеризации."""
    # Создаём продукт
    product = Product(
        id=uuid4(),
        product_code="FG_CREAM_100ML",
        product_name="Крем 100мл",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="шт"
    )
    test_db.add(product)
    test_db.commit()
    
    # Создаём рабочий центр
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
    
    # Создаём заказ
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
    
    # Создаём маршрут и операцию
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
        operation_sequence=1,
        operation_name="Filling",
        work_center_id=work_center.id,
        estimated_duration_minutes=480
    )
    test_db.add(operation)
    test_db.commit()
    
    # Создаём QUEUED задачу
    task = ProductionTask(
        id=uuid4(),
        order_id=order.id,
        operation_id=operation.id,
        work_center_id=work_center.id,
        status=TaskStatus.QUEUED
    )
    test_db.add(task)
    test_db.commit()
    
    # Запускаем preview
    request_data = {
        "manufacturing_order_ids": [str(order.id)],
        "work_center_id": None
    }
    
    response = client.post("/api/v1/dsiz/dispatching/run", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "gantt_preview" in data["data"]
    assert "conflicts" in data["data"]
    assert isinstance(data["data"]["gantt_preview"], list)
    assert isinstance(data["data"]["conflicts"], list)


def test_run_dispatch_preview_with_work_center_filter(client, test_db):
    """Тест: preview диспетчеризации с фильтром по рабочему центру."""
    # Создаём продукт
    product = Product(
        id=uuid4(),
        product_code="FG_CREAM_100ML",
        product_name="Крем 100мл",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="шт"
    )
    test_db.add(product)
    test_db.commit()
    
    # Создаём два рабочих центра
    work_center_1 = WorkCenter(
        id=uuid4(),
        name="WC_TUBE_LINE_1",
        resource_type="MACHINE",
        status=WorkCenterStatus.AVAILABLE,
        capacity_units_per_hour=100.0,
        parallel_capacity=1
    )
    work_center_2 = WorkCenter(
        id=uuid4(),
        name="WC_TUBE_LINE_2",
        resource_type="MACHINE",
        status=WorkCenterStatus.AVAILABLE,
        capacity_units_per_hour=100.0,
        parallel_capacity=1
    )
    test_db.add_all([work_center_1, work_center_2])
    test_db.commit()
    
    # Создаём заказ
    order = ManufacturingOrder(
        id=uuid4(),
        order_number="ORD-002",
        product_id=str(product.id),
        quantity=1000.0,
        status=OrderStatus.RELEASED,
        priority=OrderPriority.NORMAL.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=5)
    )
    test_db.add(order)
    test_db.commit()
    
    # Создаём маршрут и операцию
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
        operation_sequence=1,
        operation_name="Filling",
        work_center_id=work_center_1.id,
        estimated_duration_minutes=480
    )
    test_db.add(operation)
    test_db.commit()
    
    # Создаём задачи на разных рабочих центрах
    task_1 = ProductionTask(
        id=uuid4(),
        order_id=order.id,
        operation_id=operation.id,
        work_center_id=work_center_1.id,
        status=TaskStatus.QUEUED
    )
    task_2 = ProductionTask(
        id=uuid4(),
        order_id=order.id,
        operation_id=operation.id,
        work_center_id=work_center_2.id,
        status=TaskStatus.QUEUED
    )
    test_db.add_all([task_1, task_2])
    test_db.commit()
    
    # Запускаем preview с фильтром по первому рабочему центру
    request_data = {
        "manufacturing_order_ids": [str(order.id)],
        "work_center_id": str(work_center_1.id)
    }
    
    response = client.post("/api/v1/dsiz/dispatching/run", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Все задачи в preview должны быть для work_center_1
    for task_preview in data["data"]["gantt_preview"]:
        assert task_preview["work_center_id"] == str(work_center_1.id)


def test_run_dispatch_preview_no_orders(client, test_db):
    """Тест: preview диспетчеризации без заказов."""
    request_data = {
        "manufacturing_order_ids": [str(uuid4())],  # Несуществующий заказ
        "work_center_id": None
    }
    
    response = client.post("/api/v1/dsiz/dispatching/run", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["gantt_preview"]) == 0
    assert len(data["data"]["conflicts"]) == 0


def test_dispatch_task_success(client, test_db):
    """Тест: успешная диспетчеризация задачи."""
    # Создаём продукт
    product = Product(
        id=uuid4(),
        product_code="FG_CREAM_100ML",
        product_name="Крем 100мл",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="шт"
    )
    test_db.add(product)
    test_db.commit()
    
    # Создаём рабочий центр
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
    
    # Создаём заказ
    order = ManufacturingOrder(
        id=uuid4(),
        order_number="ORD-003",
        product_id=str(product.id),
        quantity=1000.0,
        status=OrderStatus.RELEASED,
        priority=OrderPriority.NORMAL.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=5)
    )
    test_db.add(order)
    test_db.commit()
    
    # Создаём маршрут и операцию
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
        operation_sequence=1,
        operation_name="Filling",
        work_center_id=work_center.id,
        estimated_duration_minutes=480
    )
    test_db.add(operation)
    test_db.commit()
    
    # Создаём QUEUED задачу
    task = ProductionTask(
        id=uuid4(),
        order_id=order.id,
        operation_id=operation.id,
        work_center_id=work_center.id,
        status=TaskStatus.QUEUED
    )
    test_db.add(task)
    test_db.commit()
    
    # Диспетчеризуем задачу
    response = client.post(f"/api/v1/dsiz/dispatching/dispatch-task/{task.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["task"]["status"] == "IN_PROGRESS"
    assert data["data"]["task"]["work_center_id"] == str(work_center.id)
    
    # Проверяем, что задача обновлена в БД
    test_db.refresh(task)
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.started_at is not None


def test_dispatch_task_not_found(client, test_db):
    """Тест: диспетчеризация несуществующей задачи."""
    non_existent_task_id = uuid4()
    
    response = client.post(f"/api/v1/dsiz/dispatching/dispatch-task/{non_existent_task_id}")
    
    assert response.status_code == 404
    data = response.json()
    assert "не найдена" in data["detail"].lower() or "not found" in data["detail"].lower()


def test_dispatch_task_already_in_progress(client, test_db):
    """Тест: диспетчеризация задачи, которая уже в процессе."""
    # Создаём продукт
    product = Product(
        id=uuid4(),
        product_code="FG_CREAM_100ML",
        product_name="Крем 100мл",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="шт"
    )
    test_db.add(product)
    test_db.commit()
    
    # Создаём рабочий центр
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
    
    # Создаём заказ
    order = ManufacturingOrder(
        id=uuid4(),
        order_number="ORD-004",
        product_id=str(product.id),
        quantity=1000.0,
        status=OrderStatus.RELEASED,
        priority=OrderPriority.NORMAL.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=5)
    )
    test_db.add(order)
    test_db.commit()
    
    # Создаём маршрут и операцию
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
        operation_sequence=1,
        operation_name="Filling",
        work_center_id=work_center.id,
        estimated_duration_minutes=480
    )
    test_db.add(operation)
    test_db.commit()
    
    # Создаём задачу, которая уже в процессе
    task = ProductionTask(
        id=uuid4(),
        order_id=order.id,
        operation_id=operation.id,
        work_center_id=work_center.id,
        status=TaskStatus.IN_PROGRESS  # Уже в процессе
    )
    test_db.add(task)
    test_db.commit()
    
    # Пытаемся диспетчеризовать
    response = client.post(f"/api/v1/dsiz/dispatching/dispatch-task/{task.id}")
    
    assert response.status_code == 400
    data = response.json()
    assert "не в статусе" in data["detail"].lower() or "not in status" in data["detail"].lower() or "queued" in data["detail"].lower()


def test_get_work_center_load_success(client, test_db):
    """Тест: получение загрузки рабочего центра."""
    # Создаём рабочий центр
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
    
    # Получаем загрузку
    response = client.get(f"/api/v1/dsiz/dispatching/work-center-load/{work_center.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "work_center_id" in data["data"]
    assert "load_percentage" in data["data"]
    assert "status" in data["data"]
    assert "available_workers" in data["data"]
    assert data["data"]["work_center_id"] == str(work_center.id)
    assert isinstance(data["data"]["load_percentage"], (int, float))
    assert data["data"]["status"] in ["Available", "Busy", "Overloaded"]


def test_get_work_center_load_with_shift(client, test_db):
    """Тест: получение загрузки рабочего центра с указанием смены."""
    # Создаём рабочий центр
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
    
    # Получаем загрузку для смены
    response = client.get(
        f"/api/v1/dsiz/dispatching/work-center-load/{work_center.id}",
        params={"shift": "day"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["shift"] == "day"
    assert "available_workers" in data["data"]


def test_get_work_center_load_not_found(client, test_db):
    """Тест: получение загрузки несуществующего рабочего центра."""
    non_existent_wc_id = uuid4()
    
    response = client.get(f"/api/v1/dsiz/dispatching/work-center-load/{non_existent_wc_id}")
    
    # Сервис должен вернуть 0% загрузки для несуществующего центра
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["load_percentage"] == 0.0
