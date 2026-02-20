"""
Unit-тесты для StrategicPlanningService.

Проверяют пересчёт плана: резервирование BOM (Этап 1) и планирование операций (Этап 2).
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from backend.core.services.strategic_planning_service import StrategicPlanningService
from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.product import Product
from backend.core.models.manufacturing_route import ManufacturingRoute
from backend.core.models.route_operation import RouteOperation
from backend.core.models.production_task import ProductionTask
from backend.core.models.enums import OrderStatus, OrderType, ProductType, TaskStatus


def test_recalculate_plan_empty_order_ids(test_db):
    """Пустой список заказов — успех, все списки пусты."""
    service = StrategicPlanningService(test_db)
    result = service.recalculate_plan([])
    assert result["success"] is True
    assert result["reserved_orders"] == []
    assert result["failed_orders"] == []
    assert result["planned_operations"] == []


def test_recalculate_plan_order_without_bom_fails_reservation(
    test_db,
    sample_work_centers,
):
    """Заказ по продукту без BOM — резервирование не проходит, в failed_orders одна запись."""
    product = Product(
        product_code="NO-BOM-PROD",
        product_name="Product without BOM",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="pcs",
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)

    order = ManufacturingOrder(
        order_number="NO-BOM-ORDER-001",
        product_id=str(product.id),
        quantity=5,
        status=OrderStatus.PLANNED,
        due_date=datetime(2026, 2, 15, 8, 0, 0, tzinfo=timezone.utc),
        order_type=OrderType.CUSTOMER.value,
        priority="NORMAL",
    )
    test_db.add(order)
    test_db.commit()
    test_db.refresh(order)

    service = StrategicPlanningService(test_db)
    result = service.recalculate_plan([order.id])

    assert result["success"] is True
    assert result["reserved_orders"] == []
    assert len(result["failed_orders"]) == 1
    assert result["failed_orders"][0]["order_id"] == str(order.id)
    assert "missing_components" in result["failed_orders"][0]
    assert result["planned_operations"] == []


def test_recalculate_plan_order_with_route_creates_planned_operations(
    test_db,
    sample_work_centers,
    sample_finished_good,
    sample_bom_fg_to_bulk,
    sample_bom_fg_to_packaging,
    sample_inventory_finished,
    sample_packaging,
):
    """
    Заказ по продукту с BOM и достаточными остатками и маршрутом —
    резервирование успешно, создаются ProductionTask (planned_operations).
    """
    from backend.core.models.inventory_balance import InventoryBalance
    from backend.core.models.enums import ProductStatus

    inv_packaging = InventoryBalance(
        product_id=sample_packaging.id,
        location="WH1",
        quantity=1000,
        unit="pcs",
        product_status=ProductStatus.FINISHED.value,
        reserved_quantity=0,
    )
    test_db.add(inv_packaging)
    test_db.commit()

    route = ManufacturingRoute(
        product_id=str(sample_finished_good.id),
        route_name="FG Route",
        description="Test",
    )
    test_db.add(route)
    test_db.commit()
    test_db.refresh(route)

    test_db.add(
        RouteOperation(
            route_id=route.id,
            operation_sequence=1,
            operation_name="Assembly",
            work_center_id=sample_work_centers[0].id,
            estimated_duration_minutes=60,
        )
    )
    test_db.commit()

    order = ManufacturingOrder(
        order_number="FG-ORDER-001",
        product_id=str(sample_finished_good.id),
        quantity=10,
        status=OrderStatus.PLANNED,
        due_date=datetime(2026, 2, 20, 8, 0, 0, tzinfo=timezone.utc),
        order_type=OrderType.CUSTOMER.value,
        priority="NORMAL",
    )
    test_db.add(order)
    test_db.commit()
    test_db.refresh(order)

    service = StrategicPlanningService(test_db)
    result = service.recalculate_plan([order.id])

    assert result["success"] is True
    assert str(order.id) in result["reserved_orders"]
    assert len(result["planned_operations"]) >= 1
    assert all(
        "task_id" in op and "planned_start" in op and "planned_end" in op
        for op in result["planned_operations"]
    )

    tasks = (
        test_db.query(ProductionTask)
        .filter(ProductionTask.order_id == order.id)
        .all()
    )
    assert len(tasks) >= 1
    for task in tasks:
        assert task.status == TaskStatus.QUEUED
        assert task.started_at is not None
        assert task.completed_at is not None
