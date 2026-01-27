"""
Unit tests for OrderService.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import select

from backend.src.services.order_service import OrderService
from backend.src.schemas.manufacturing_order import ManufacturingOrderCreate
from backend.src.models.manufacturing_order import ManufacturingOrder
from backend.src.models.production_task import ProductionTask
from backend.src.models.enums import OrderStatus, TaskStatus


def test_create_order_with_tasks_success(test_db, sample_route):
    """
    Тест создания заказа с автогенерацией задач.
    """
    service = OrderService(test_db)
    
    payload = ManufacturingOrderCreate(
        product_id="TEST-PROD-001",
        quantity=Decimal("10.0"),
        order_number="TEST-ORDER-001",
        due_date=datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    
    order = service.create_order_with_tasks(payload)
    
    # Проверки заказа
    assert order.order_number == "TEST-ORDER-001"
    assert order.status == OrderStatus.PLANNED
    assert order.quantity == Decimal("10.0")
    assert order.product_id == "TEST-PROD-001"
    
    # Проверяем задачи
    tasks_query = select(ProductionTask).where(ProductionTask.order_id == order.id)
    tasks_result = test_db.execute(tasks_query)
    tasks = list(tasks_result.scalars().all())
    assert len(tasks) == 3
    
    for task in tasks:
        assert task.status == TaskStatus.QUEUED
        assert task.work_center_id is not None
        assert task.operation_id is not None
        assert task.order_id == order.id
    
    # Проверяем последовательность задач
    task_sequences = []
    for task in tasks:
        test_db.refresh(task)
        task_sequences.append(task.route_operation.operation_sequence)
    assert sorted(task_sequences) == [1, 2, 3]


def test_create_order_route_not_found(test_db):
    """
    Тест создания заказа для несуществующего product_id.
    """
    service = OrderService(test_db)
    
    payload = ManufacturingOrderCreate(
        product_id="NONEXISTENT-PROD",
        quantity=Decimal("10.0"),
        order_number="TEST-ORDER-002",
        due_date=datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    
    with pytest.raises(ValueError, match="Manufacturing route not found"):
        service.create_order_with_tasks(payload)


def test_create_order_invalid_quantity(test_db, sample_route):
    """
    Тест валидации количества (quantity <= 0).
    Pydantic валидирует на уровне схемы, поэтому проверяем ValidationError.
    """
    from pydantic import ValidationError
    
    # Тест с quantity = 0 - Pydantic валидирует на уровне схемы
    with pytest.raises(ValidationError):
        ManufacturingOrderCreate(
            product_id="TEST-PROD-001",
            quantity=Decimal("0.0"),
            order_number="TEST-ORDER-003",
            due_date=datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
        )
    
    # Тест с отрицательным quantity - Pydantic валидирует на уровне схемы
    with pytest.raises(ValidationError):
        ManufacturingOrderCreate(
            product_id="TEST-PROD-001",
            quantity=Decimal("-5.0"),
            order_number="TEST-ORDER-004",
            due_date=datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
        )


def test_get_order_with_tasks(test_db, sample_route):
    """
    Тест получения заказа с задачами (eager loading).
    """
    service = OrderService(test_db)
    
    # Создаём заказ
    payload = ManufacturingOrderCreate(
        product_id="TEST-PROD-001",
        quantity=Decimal("5.0"),
        order_number="TEST-ORDER-005",
        due_date=datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    created_order = service.create_order_with_tasks(payload)
    
    # Получаем заказ через get_order_with_tasks
    retrieved_order = service.get_order_with_tasks(created_order.id)
    
    # Проверки
    assert retrieved_order is not None
    assert retrieved_order.id == created_order.id
    assert retrieved_order.order_number == "TEST-ORDER-005"
    
    # Проверяем, что задачи подгружены
    assert len(retrieved_order.production_tasks) == 3
    for task in retrieved_order.production_tasks:
        assert task.status == TaskStatus.QUEUED
        assert task.order_id == retrieved_order.id


def test_list_orders_filter_by_status(test_db, sample_route):
    """
    Тест фильтрации заказов по статусу.
    """
    service = OrderService(test_db)
    
    # Создаём 2 заказа
    payload1 = ManufacturingOrderCreate(
        product_id="TEST-PROD-001",
        quantity=Decimal("10.0"),
        order_number="TEST-ORDER-006",
        due_date=datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    order1 = service.create_order_with_tasks(payload1)
    
    payload2 = ManufacturingOrderCreate(
        product_id="TEST-PROD-001",
        quantity=Decimal("20.0"),
        order_number="TEST-ORDER-007",
        due_date=datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    order2 = service.create_order_with_tasks(payload2)
    
    # Обновляем статус второго заказа на COMPLETED
    service.update_order_status(order2.id, OrderStatus.COMPLETED)
    
    # Получаем заказы со статусом PLANNED
    planned_orders = service.list_orders(status=OrderStatus.PLANNED)
    assert len(planned_orders) >= 1
    assert all(order.status == OrderStatus.PLANNED for order in planned_orders)
    assert order1.id in [order.id for order in planned_orders]
    
    # Получаем заказы со статусом COMPLETED
    completed_orders = service.list_orders(status=OrderStatus.COMPLETED)
    assert len(completed_orders) >= 1
    assert all(order.status == OrderStatus.COMPLETED for order in completed_orders)
    assert order2.id in [order.id for order in completed_orders]
