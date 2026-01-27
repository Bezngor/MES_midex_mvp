"""
Интеграционные тесты для Dispatching API endpoints.
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from sqlalchemy import select

from backend.src.models.manufacturing_order import ManufacturingOrder
from backend.src.models.production_task import ProductionTask
from backend.src.models.enums import OrderStatus, TaskStatus


def test_release_order_api(
    client,
    test_db,
    sample_manufacturing_order,
    sample_route
):
    """Тест POST /api/v1/dispatching/release-order."""
    sample_manufacturing_order.status = OrderStatus.PLANNED
    sample_manufacturing_order.product_id = sample_route.product_id
    test_db.commit()
    test_db.refresh(sample_manufacturing_order)
    
    response = client.post("/api/v1/dispatching/release-order", json={
        "order_id": str(sample_manufacturing_order.id)
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["order"]["status"] == "RELEASED"
    assert data["data"]["tasks_created"] >= 1


def test_release_order_api_not_found(client):
    """Тест выпуска заказа с невалидным ID."""
    response = client.post("/api/v1/dispatching/release-order", json={
        "order_id": str(uuid4())
    })
    
    assert response.status_code == 400
    assert "не найден" in response.json()["detail"].lower() or "not found" in response.json()["detail"].lower()


def test_release_order_api_already_released(
    client,
    test_db,
    sample_manufacturing_order
):
    """Тест ошибки, когда заказ уже выпущен."""
    sample_manufacturing_order.status = OrderStatus.RELEASED
    test_db.commit()
    test_db.refresh(sample_manufacturing_order)
    
    response = client.post("/api/v1/dispatching/release-order", json={
        "order_id": str(sample_manufacturing_order.id)
    })
    
    assert response.status_code == 400
    # Проверяем, что ошибка содержит информацию о статусе
    detail = response.json()["detail"].lower()
    assert "planned" in detail or "не в статусе" in detail


def test_dispatch_task_api(
    client,
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест POST /api/v1/dispatching/dispatch-task."""
    # Создаём QUEUED задачу
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.QUEUED
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    
    response = client.post("/api/v1/dispatching/dispatch-task", json={
        "task_id": str(task.id),
        "work_center_id": str(sample_work_centers[0].id),
        "scheduled_start": datetime.now(timezone.utc).isoformat()
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["task"]["status"] == "IN_PROGRESS"


def test_dispatch_task_api_not_found(client, sample_work_centers):
    """Тест диспетчеризации с невалидным task ID."""
    response = client.post("/api/v1/dispatching/dispatch-task", json={
        "task_id": str(uuid4()),
        "work_center_id": str(sample_work_centers[0].id)
    })
    
    assert response.status_code == 400


def test_get_schedule_api(
    client,
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест GET /api/v1/dispatching/schedule."""
    # Настраиваем IN_PROGRESS задачу
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
    
    response = client.get("/api/v1/dispatching/schedule?horizon_days=7")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "schedule" in data["data"]
    assert len(data["data"]["schedule"]) >= 1


def test_get_schedule_api_filter_work_center(
    client,
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест фильтрации расписания по рабочему центру."""
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
    
    response = client.get(
        f"/api/v1/dispatching/schedule?work_center_id={sample_work_centers[0].id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    # Все задачи должны быть для этого рабочего центра
    for task_item in data["data"]["schedule"]:
        assert task_item["work_center_id"] == str(sample_work_centers[0].id)


def test_get_work_center_load_api(
    client,
    sample_work_centers
):
    """Тест GET /api/v1/dispatching/work-center-load/{id}."""
    response = client.get(
        f"/api/v1/dispatching/work-center-load/{sample_work_centers[0].id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "load_percentage" in data["data"]
    assert "status" in data["data"]


def test_get_work_center_load_api_with_task(
    client,
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест загрузки рабочего центра с активной задачей."""
    wc = sample_work_centers[0]
    wc.parallel_capacity = 1
    test_db.commit()
    test_db.refresh(wc)
    
    today = datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0)
    
    # 4-часовая задача = 50% загрузки
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=wc.id,
        status=TaskStatus.IN_PROGRESS,
        started_at=today,
        completed_at=today + timedelta(hours=4)
    )
    test_db.add(task)
    test_db.commit()
    
    # Передаём дату как query параметр в ISO формате
    response = client.get(
        f"/api/v1/dispatching/work-center-load/{wc.id}",
        params={"date": today.isoformat()}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["load_percentage"] == 50.0
    assert data["data"]["status"] == "Available"  # <70%


def test_get_gantt_data_api(
    client,
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест GET /api/v1/dispatching/gantt-data."""
    # Настраиваем задачу
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
    
    response = client.get("/api/v1/dispatching/gantt-data")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "work_centers" in data["data"]
    assert "start_date" in data["data"]
    assert "end_date" in data["data"]


def test_get_gantt_data_api_with_date_range(
    client,
    sample_work_centers
):
    """Тест данных Ганта с кастомным диапазоном дат."""
    # Используем формат, который FastAPI может распарсить
    start = datetime.now(timezone.utc)
    end = start + timedelta(days=14)
    
    response = client.get(
        f"/api/v1/dispatching/gantt-data",
        params={
            "start_date": start.isoformat(),
            "end_date": end.isoformat()
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_release_order_with_route_api(
    client,
    test_db,
    sample_manufacturing_order,
    sample_route
):
    """Тест выпуска заказа с операциями маршрута."""
    sample_manufacturing_order.status = OrderStatus.PLANNED
    sample_manufacturing_order.product_id = sample_route.product_id
    test_db.commit()
    test_db.refresh(sample_manufacturing_order)
    
    response = client.post("/api/v1/dispatching/release-order", json={
        "order_id": str(sample_manufacturing_order.id)
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["tasks_created"] >= 1  # Должна создаться из маршрута


def test_preview_dispatch_api(
    client,
    test_db,
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест POST /api/v1/dispatch/preview."""
    # Создаём QUEUED задачу
    task = ProductionTask(
        order_id=sample_manufacturing_order.id,
        operation_id=uuid4(),
        work_center_id=sample_work_centers[0].id,
        status=TaskStatus.QUEUED
    )
    test_db.add(task)
    test_db.commit()
    
    response = client.post("/api/v1/dispatch/preview?limit=50")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
