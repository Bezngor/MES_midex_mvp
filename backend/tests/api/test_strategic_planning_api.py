"""
Интеграционные тесты для Strategic Planning API.

Проверяют endpoint POST /api/v1/strategic-planning/recalculate-plan.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.product import Product
from backend.core.models.manufacturing_route import ManufacturingRoute
from backend.core.models.route_operation import RouteOperation
from backend.core.models.enums import OrderStatus, OrderType, ProductType


def test_recalculate_plan_empty_order_ids_400(client):
    """Пустой список order_ids возвращает 400."""
    response = client.post(
        "/api/v1/strategic-planning/recalculate-plan",
        json={"order_ids": []},
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "заказ" in data["detail"].lower() or "order" in data["detail"].lower()


def test_recalculate_plan_invalid_uuid_400(client):
    """Некорректный UUID в order_ids возвращает 400."""
    response = client.post(
        "/api/v1/strategic-planning/recalculate-plan",
        json={"order_ids": ["not-a-uuid"]},
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_recalculate_plan_success_response_structure(
    client,
    test_db,
    sample_work_centers,
    sample_finished_good,
):
    """
    При валидных order_ids возвращается 200 и структура ответа:
    success, data.reserved_orders, data.failed_orders, data.planned_operations.
    Заказ без BOM или без достаточных остатков даёт failed_orders.
    """
    route = ManufacturingRoute(
        product_id=str(sample_finished_good.id),
        route_name="Test FG Route",
        description="Route for strategic planning test",
    )
    test_db.add(route)
    test_db.commit()
    test_db.refresh(route)

    test_db.add(
        RouteOperation(
            route_id=route.id,
            operation_sequence=1,
            operation_name="Op1",
            work_center_id=sample_work_centers[0].id,
            estimated_duration_minutes=60,
        )
    )
    test_db.commit()

    order = ManufacturingOrder(
        order_number="STRAT-PLAN-001",
        product_id=str(sample_finished_good.id),
        quantity=10,
        status=OrderStatus.PLANNED,
        due_date=datetime(2026, 2, 10, 8, 0, 0, tzinfo=timezone.utc),
        order_type=OrderType.CUSTOMER.value,
        priority="NORMAL",
    )
    test_db.add(order)
    test_db.commit()
    test_db.refresh(order)

    response = client.post(
        "/api/v1/strategic-planning/recalculate-plan",
        json={"order_ids": [str(order.id)]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "data" in data
    body = data["data"]
    assert "reserved_orders" in body
    assert "failed_orders" in body
    assert "planned_operations" in body
    assert isinstance(body["reserved_orders"], list)
    assert isinstance(body["failed_orders"], list)
    assert isinstance(body["planned_operations"], list)


def test_recalculate_plan_nonexistent_order_ids_200(client):
    """
    Передача несуществующих UUID возвращает 200:
    заказы не найдены — reserved_orders и planned_operations пусты.
    """
    response = client.post(
        "/api/v1/strategic-planning/recalculate-plan",
        json={"order_ids": [str(uuid4())]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert data["data"]["reserved_orders"] == []
    assert data["data"]["planned_operations"] == []
