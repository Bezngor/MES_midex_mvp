"""
Integration tests for API endpoints.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import select

from backend.src.models.production_task import ProductionTask
from backend.src.models.work_center import WorkCenter
from backend.src.models.enums import TaskStatus, WorkCenterStatus


def test_create_order_api(client, sample_route):
    """
    Интеграционный тест создания заказа через API.
    """
    response = client.post(
        "/api/v1/manufacturing-orders",
        json={
            "product_id": "TEST-PROD-001",
            "quantity": 10.0,
            "order_number": "API-ORDER-001",
            "due_date": "2026-02-01T00:00:00Z"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["order_number"] == "API-ORDER-001"
    assert data["data"]["status"] == "PLANNED"
    assert data["data"]["quantity"] == 10.0


def test_get_order_api(client, sample_route):
    """
    Интеграционный тест получения заказа с задачами через API.
    """
    # Создаём заказ
    create_response = client.post(
        "/api/v1/manufacturing-orders",
        json={
            "product_id": "TEST-PROD-001",
            "quantity": 5.0,
            "order_number": "API-ORDER-002",
            "due_date": "2026-02-01T00:00:00Z"
        }
    )
    assert create_response.status_code == 201
    order_id = create_response.json()["data"]["id"]
    
    # Получаем заказ
    get_response = client.get(f"/api/v1/manufacturing-orders/{order_id}")
    
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["success"] is True
    assert data["data"]["order_number"] == "API-ORDER-002"
    assert "production_tasks" in data["data"]
    assert len(data["data"]["production_tasks"]) == 3
    
    # Проверяем, что все задачи в статусе QUEUED
    for task in data["data"]["production_tasks"]:
        assert task["status"] == "QUEUED"


def test_start_task_api(client, sample_route):
    """
    Интеграционный тест запуска задачи через API.
    """
    # Создаём заказ
    create_response = client.post(
        "/api/v1/manufacturing-orders",
        json={
            "product_id": "TEST-PROD-001",
            "quantity": 10.0,
            "order_number": "API-ORDER-003",
            "due_date": "2026-02-01T00:00:00Z"
        }
    )
    assert create_response.status_code == 201
    order_id = create_response.json()["data"]["id"]
    
    # Получаем заказ с задачами
    get_order_response = client.get(f"/api/v1/manufacturing-orders/{order_id}")
    assert get_order_response.status_code == 200
    task_id = get_order_response.json()["data"]["production_tasks"][0]["id"]
    
    # Запускаем задачу
    start_response = client.patch(
        f"/api/v1/production-tasks/{task_id}/start",
        json={
            "operator_id": "operator-123"
        }
    )
    
    assert start_response.status_code == 200
    data = start_response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "IN_PROGRESS"
    assert data["data"]["assigned_to"] == "operator-123"
    assert data["data"]["started_at"] is not None


def test_complete_task_api(client, sample_route):
    """
    Интеграционный тест завершения задачи через API.
    """
    # Создаём заказ
    create_response = client.post(
        "/api/v1/manufacturing-orders",
        json={
            "product_id": "TEST-PROD-001",
            "quantity": 10.0,
            "order_number": "API-ORDER-004",
            "due_date": "2026-02-01T00:00:00Z"
        }
    )
    assert create_response.status_code == 201
    order_id = create_response.json()["data"]["id"]
    
    # Получаем заказ с задачами
    get_order_response = client.get(f"/api/v1/manufacturing-orders/{order_id}")
    assert get_order_response.status_code == 200
    task_id = get_order_response.json()["data"]["production_tasks"][0]["id"]
    
    # Запускаем задачу
    start_response = client.patch(
        f"/api/v1/production-tasks/{task_id}/start",
        json={"operator_id": "operator-123"}
    )
    assert start_response.status_code == 200
    
    # Завершаем задачу
    complete_response = client.patch(
        f"/api/v1/production-tasks/{task_id}/complete",
        json={"notes": "Task completed successfully"}
    )
    
    assert complete_response.status_code == 200
    data = complete_response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "COMPLETED"
    assert data["data"]["completed_at"] is not None


def test_dispatch_preview_excludes_down_centers(client, sample_route, sample_work_centers, test_db):
    """
    Интеграционный тест preview dispatch, исключающий задачи для DOWN центров.
    """
    # Создаём заказ
    create_response = client.post(
        "/api/v1/manufacturing-orders",
        json={
            "product_id": "TEST-PROD-001",
            "quantity": 10.0,
            "order_number": "API-ORDER-005",
            "due_date": "2026-02-01T00:00:00Z"
        }
    )
    assert create_response.status_code == 201
    order_id = create_response.json()["data"]["id"]
    
    # Получаем задачи заказа
    get_order_response = client.get(f"/api/v1/manufacturing-orders/{order_id}")
    assert get_order_response.status_code == 200
    tasks = get_order_response.json()["data"]["production_tasks"]
    
    # Находим задачу, привязанную к первому WorkCenter
    task_for_wc1 = None
    for task in tasks:
        if task["work_center_id"] == str(sample_work_centers[0].id):
            task_for_wc1 = task
            break
    
    assert task_for_wc1 is not None
    
    # Устанавливаем первый WorkCenter в статус DOWN
    wc1_query = select(WorkCenter).where(WorkCenter.id == sample_work_centers[0].id)
    wc1_result = test_db.execute(wc1_query)
    wc1 = wc1_result.scalar_one()
    wc1.status = WorkCenterStatus.DOWN
    test_db.commit()
    
    # Получаем preview dispatch
    preview_response = client.post("/api/v1/dispatch/preview?limit=50")
    
    assert preview_response.status_code == 200
    data = preview_response.json()
    assert data["success"] is True
    
    # Проверяем, что задачи для DOWN центра отсутствуют в preview
    dispatchable_task_ids = [task["id"] for task in data["data"]]
    assert task_for_wc1["id"] not in dispatchable_task_ids
    
    # Проверяем, что задачи для доступных центров присутствуют
    task_for_wc2 = None
    task_for_wc3 = None
    for task in tasks:
        if task["work_center_id"] == str(sample_work_centers[1].id):
            task_for_wc2 = task
        if task["work_center_id"] == str(sample_work_centers[2].id):
            task_for_wc3 = task
    
    # Хотя бы одна из задач для доступных центров должна быть в preview
    assert task_for_wc2["id"] in dispatchable_task_ids or task_for_wc3["id"] in dispatchable_task_ids
