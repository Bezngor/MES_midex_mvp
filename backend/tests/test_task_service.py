"""
Unit tests for TaskService.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import select

from backend.src.services.order_service import OrderService
from backend.src.services.task_service import TaskService
from backend.src.schemas.manufacturing_order import ManufacturingOrderCreate
from backend.src.models.production_task import ProductionTask
from backend.src.models.genealogy_record import GenealogyRecord
from backend.src.models.manufacturing_order import ManufacturingOrder
from backend.src.models.enums import TaskStatus, OrderStatus


def test_start_task_from_queued(test_db, sample_route):
    """
    Тест запуска задачи из QUEUED.
    """
    # Создаём заказ
    order_service = OrderService(test_db)
    payload = ManufacturingOrderCreate(
        product_id="TEST-PROD-001",
        quantity=Decimal("10.0"),
        order_number="TEST-ORDER-001",
        due_date=datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    order = order_service.create_order_with_tasks(payload)
    
    # Получаем первую задачу
    task_query = select(ProductionTask).where(ProductionTask.order_id == order.id).limit(1)
    task_result = test_db.execute(task_query)
    task = task_result.scalar_one()
    assert task.status == TaskStatus.QUEUED
    
    # Запускаем задачу
    task_service = TaskService(test_db)
    updated_task = task_service.start_task(task.id, operator_id="test-operator")
    
    # Проверки
    assert updated_task.status == TaskStatus.IN_PROGRESS
    assert updated_task.started_at is not None
    assert updated_task.assigned_to == "test-operator"
    
    # Проверяем genealogy
    genealogy_query = select(GenealogyRecord).where(GenealogyRecord.task_id == task.id)
    genealogy_result = test_db.execute(genealogy_query)
    genealogy = list(genealogy_result.scalars().all())
    assert len(genealogy) == 1
    assert genealogy[0].event_type == "STARTED"
    assert genealogy[0].operator_id == "test-operator"


def test_start_task_invalid_status(test_db, sample_route):
    """
    Тест попытки запустить задачу с невалидным статусом.
    """
    # Создаём заказ
    order_service = OrderService(test_db)
    payload = ManufacturingOrderCreate(
        product_id="TEST-PROD-001",
        quantity=Decimal("10.0"),
        order_number="TEST-ORDER-002",
        due_date=datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    order = order_service.create_order_with_tasks(payload)
    
    # Получаем задачу и запускаем её
    task = test_db.query(ProductionTask).filter(ProductionTask.order_id == order.id).first()
    task_service = TaskService(test_db)
    task_service.start_task(task.id, operator_id="test-operator")
    
    # Пытаемся запустить снова (статус уже IN_PROGRESS)
    with pytest.raises(ValueError, match="Cannot start task with status"):
        task_service.start_task(task.id, operator_id="test-operator")
    
    # Завершаем задачу
    task_service.complete_task(task.id)
    
    # Пытаемся запустить завершённую задачу
    with pytest.raises(ValueError, match="Cannot start task with status"):
        task_service.start_task(task.id, operator_id="test-operator")


def test_complete_task_from_in_progress(test_db, sample_route):
    """
    Тест завершения задачи из IN_PROGRESS.
    """
    # Создаём заказ
    order_service = OrderService(test_db)
    payload = ManufacturingOrderCreate(
        product_id="TEST-PROD-001",
        quantity=Decimal("10.0"),
        order_number="TEST-ORDER-003",
        due_date=datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    order = order_service.create_order_with_tasks(payload)
    
    # Получаем задачу и запускаем её
    task_query = select(ProductionTask).where(ProductionTask.order_id == order.id).limit(1)
    task_result = test_db.execute(task_query)
    task = task_result.scalar_one()
    task_service = TaskService(test_db)
    task_service.start_task(task.id, operator_id="test-operator")
    
    # Завершаем задачу
    updated_task = task_service.complete_task(task.id, notes="Task completed successfully")
    
    # Проверки
    assert updated_task.status == TaskStatus.COMPLETED
    assert updated_task.completed_at is not None
    
    # Проверяем genealogy
    genealogy_query = select(GenealogyRecord).where(GenealogyRecord.task_id == task.id)
    genealogy_result = test_db.execute(genealogy_query)
    genealogy = list(genealogy_result.scalars().all())
    assert len(genealogy) == 2  # STARTED и COMPLETED
    completed_records = [g for g in genealogy if g.event_type == "COMPLETED"]
    assert len(completed_records) == 1
    assert completed_records[0].notes == "Task completed successfully"


def test_complete_task_updates_order_status(test_db, sample_route):
    """
    Тест обновления статуса заказа после завершения всех задач.
    """
    # Создаём заказ
    order_service = OrderService(test_db)
    payload = ManufacturingOrderCreate(
        product_id="TEST-PROD-001",
        quantity=Decimal("10.0"),
        order_number="TEST-ORDER-004",
        due_date=datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    order = order_service.create_order_with_tasks(payload)
    
    # Проверяем начальный статус заказа
    assert order.status == OrderStatus.PLANNED
    
    # Получаем все задачи
    tasks_query = select(ProductionTask).where(ProductionTask.order_id == order.id).order_by(ProductionTask.created_at)
    tasks_result = test_db.execute(tasks_query)
    tasks = list(tasks_result.scalars().all())
    assert len(tasks) == 3
    
    task_service = TaskService(test_db)
    
    # Запускаем и завершаем все задачи последовательно
    for task in tasks:
        task_service.start_task(task.id, operator_id="test-operator")
        task_service.complete_task(task.id)
    
    # Проверяем, что все задачи завершены
    for task in tasks:
        test_db.refresh(task)
        assert task.status == TaskStatus.COMPLETED
    
    # Проверяем, что статус заказа обновлён на COMPLETED
    test_db.refresh(order)
    assert order.status == OrderStatus.COMPLETED


def test_fail_task(test_db, sample_route):
    """
    Тест пометки задачи как проваленной.
    """
    # Создаём заказ
    order_service = OrderService(test_db)
    payload = ManufacturingOrderCreate(
        product_id="TEST-PROD-001",
        quantity=Decimal("10.0"),
        order_number="TEST-ORDER-005",
        due_date=datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    order = order_service.create_order_with_tasks(payload)
    
    # Получаем задачу и запускаем её
    task_query = select(ProductionTask).where(ProductionTask.order_id == order.id).limit(1)
    task_result = test_db.execute(task_query)
    task = task_result.scalar_one()
    task_service = TaskService(test_db)
    task_service.start_task(task.id, operator_id="test-operator")
    
    # Помечаем задачу как проваленную
    updated_task = task_service.fail_task(task.id, reason="Equipment failure")
    
    # Проверки
    assert updated_task.status == TaskStatus.FAILED
    
    # Проверяем genealogy
    genealogy_query = select(GenealogyRecord).where(GenealogyRecord.task_id == task.id)
    genealogy_result = test_db.execute(genealogy_query)
    genealogy = list(genealogy_result.scalars().all())
    assert len(genealogy) == 2  # STARTED и FAILED
    failed_records = [g for g in genealogy if g.event_type == "FAILED"]
    assert len(failed_records) == 1
    assert failed_records[0].notes == "Equipment failure"


def test_list_tasks_filter_by_status(test_db, sample_route):
    """
    Тест фильтрации задач по статусу.
    """
    # Создаём заказ
    order_service = OrderService(test_db)
    payload = ManufacturingOrderCreate(
        product_id="TEST-PROD-001",
        quantity=Decimal("10.0"),
        order_number="TEST-ORDER-006",
        due_date=datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    order = order_service.create_order_with_tasks(payload)
    
    # Получаем все задачи
    tasks_query = select(ProductionTask).where(ProductionTask.order_id == order.id)
    tasks_result = test_db.execute(tasks_query)
    tasks = list(tasks_result.scalars().all())
    assert len(tasks) == 3
    
    task_service = TaskService(test_db)
    
    # Запускаем первую задачу
    task_service.start_task(tasks[0].id, operator_id="test-operator")
    
    # Завершаем вторую задачу (сначала запускаем, потом завершаем)
    task_service.start_task(tasks[1].id, operator_id="test-operator")
    task_service.complete_task(tasks[1].id)
    
    # Третья задача остаётся в QUEUED
    
    # Фильтруем по статусу QUEUED
    queued_tasks = task_service.list_tasks(status=TaskStatus.QUEUED)
    queued_task_ids = [t.id for t in queued_tasks]
    assert tasks[2].id in queued_task_ids
    assert all(t.status == TaskStatus.QUEUED for t in queued_tasks)
    
    # Фильтруем по статусу IN_PROGRESS
    in_progress_tasks = task_service.list_tasks(status=TaskStatus.IN_PROGRESS)
    in_progress_task_ids = [t.id for t in in_progress_tasks]
    assert tasks[0].id in in_progress_task_ids
    assert all(t.status == TaskStatus.IN_PROGRESS for t in in_progress_tasks)
    
    # Фильтруем по статусу COMPLETED
    completed_tasks = task_service.list_tasks(status=TaskStatus.COMPLETED)
    completed_task_ids = [t.id for t in completed_tasks]
    assert tasks[1].id in completed_task_ids
    assert all(t.status == TaskStatus.COMPLETED for t in completed_tasks)
