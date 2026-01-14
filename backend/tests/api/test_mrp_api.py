"""
Интеграционные тесты для MRP API endpoints.
"""

import pytest
from datetime import datetime, timezone, timedelta


def test_consolidate_orders_api(
    client,
    test_db,
    sample_finished_good
):
    """Тест POST /api/v1/mrp/consolidate."""
    # Создаём SHIP заказ напрямую в БД (API создаёт PLANNED)
    from backend.src.models.manufacturing_order import ManufacturingOrder
    from backend.src.models.enums import OrderStatus, OrderType
    
    order = ManufacturingOrder(
        order_number="API-CONS-001",
        product_id=str(sample_finished_good.id),
        quantity=5000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=5)
    )
    test_db.add(order)
    test_db.commit()
    
    # Консолидируем
    response = client.post("/api/v1/mrp/consolidate", json={"horizon_days": 30})
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "consolidated_orders" in data["data"]
    assert len(data["data"]["consolidated_orders"]) >= 1


def test_consolidate_orders_api_custom_horizon(
    client,
    test_db,
    sample_finished_good
):
    """Тест консолидации с кастомным горизонтом."""
    from backend.src.models.manufacturing_order import ManufacturingOrder
    from backend.src.models.enums import OrderStatus, OrderType
    
    # Создаём заказ на 40 дней вперёд напрямую в БД
    order = ManufacturingOrder(
        order_number="API-CONS-FAR",
        product_id=str(sample_finished_good.id),
        quantity=1000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=40)
    )
    test_db.add(order)
    test_db.commit()
    
    # Тест с горизонтом 30 дней (должен исключить заказ)
    response30 = client.post("/api/v1/mrp/consolidate", json={"horizon_days": 30})
    data30 = response30.json()
    
    # Тест с горизонтом 60 дней (должен включить заказ)
    response60 = client.post("/api/v1/mrp/consolidate", json={"horizon_days": 60})
    data60 = response60.json()
    
    assert response30.status_code == 200
    assert response60.status_code == 200
    # Заказ должен быть в 60-дневном, но не в 30-дневном
    assert len(data30["data"]["consolidated_orders"]) == 0
    assert len(data60["data"]["consolidated_orders"]) >= 1


def test_explode_bom_api(
    client,
    sample_finished_good,
    sample_bulk_product,
    sample_bom_fg_to_bulk
):
    """Тест POST /api/v1/mrp/explode-bom."""
    response = client.post("/api/v1/mrp/explode-bom", json={
        "product_id": str(sample_finished_good.id),
        "quantity": 10000.0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert str(sample_bulk_product.id) in data["data"]["requirements"]
    assert float(data["data"]["requirements"][str(sample_bulk_product.id)]) == 900.0
    assert data["data"]["total_components"] == 1


def test_explode_bom_api_no_bom(client, sample_raw_material):
    """Тест взрыва BOM для продукта без BOM."""
    response = client.post("/api/v1/mrp/explode-bom", json={
        "product_id": str(sample_raw_material.id),
        "quantity": 1000.0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["total_components"] == 0
    assert data["data"]["requirements"] == {}


def test_explode_bom_api_invalid_product(client):
    """Тест взрыва BOM с невалидным product ID."""
    response = client.post("/api/v1/mrp/explode-bom", json={
        "product_id": "00000000-0000-0000-0000-000000000000",
        "quantity": 1000.0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["total_components"] == 0


def test_net_requirement_api(client, sample_bulk_product):
    """Тест POST /api/v1/mrp/net-requirement."""
    response = client.post("/api/v1/mrp/net-requirement", json={
        "product_id": str(sample_bulk_product.id),
        "gross_requirement": 1000.0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "net_requirement" in data["data"]
    assert "available_stock" in data["data"]
    assert "needs_production" in data["data"]


def test_net_requirement_api_with_inventory(
    client,
    sample_bulk_product,
    sample_inventory_finished
):
    """Тест нетто-потребности с существующим инвентарём."""
    # sample_inventory_finished: 650 всего, 100 зарезервировано = 550 доступно
    response = client.post("/api/v1/mrp/net-requirement", json={
        "product_id": str(sample_bulk_product.id),
        "gross_requirement": 1000.0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert float(data["data"]["available_stock"]) == 550.0
    assert float(data["data"]["net_requirement"]) == 450.0
    assert data["data"]["needs_production"] is True


def test_create_bulk_order_api(
    client,
    sample_bulk_product,
    sample_manufacturing_order
):
    """Тест POST /api/v1/mrp/create-bulk-order."""
    response = client.post("/api/v1/mrp/create-bulk-order", json={
        "parent_order_id": str(sample_manufacturing_order.id),
        "bulk_product_id": str(sample_bulk_product.id),
        "quantity_kg": 900.0,
        "due_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "order" in data["data"]
    assert data["data"]["order"]["order_type"] == "INTERNAL_BULK"
    assert float(data["data"]["rounded_quantity"]) == 1000.0  # Округлено с 900


def test_create_bulk_order_api_without_parent(
    client,
    sample_bulk_product
):
    """Тест создания батч-заказа без родителя."""
    response = client.post("/api/v1/mrp/create-bulk-order", json={
        "bulk_product_id": str(sample_bulk_product.id),
        "quantity_kg": 500.0,
        "due_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["order"]["parent_order_id"] is None


def test_create_bulk_order_api_invalid_product(
    client,
    sample_finished_good,
    sample_manufacturing_order
):
    """Тест ошибки, когда продукт не является BULK."""
    response = client.post("/api/v1/mrp/create-bulk-order", json={
        "parent_order_id": str(sample_manufacturing_order.id),
        "bulk_product_id": str(sample_finished_good.id),
        "quantity_kg": 1000.0,
        "due_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    })
    
    assert response.status_code == 400
    assert "не является типом BULK" in response.json()["detail"] or "not BULK type" in response.json()["detail"]


def test_consolidate_orders_api_validation_error(client):
    """Тест ошибки валидации для невалидного horizon_days."""
    response = client.post("/api/v1/mrp/consolidate", json={
        "horizon_days": -10  # Невалидное отрицательное значение
    })
    
    assert response.status_code == 422  # Ошибка валидации


def test_explode_bom_api_validation_error(client, sample_finished_good):
    """Тест ошибки валидации для невалидного количества."""
    response = client.post("/api/v1/mrp/explode-bom", json={
        "product_id": str(sample_finished_good.id),
        "quantity": -100.0  # Невалидное отрицательное количество
    })
    
    assert response.status_code == 422


def test_net_requirement_api_validation_error(client, sample_bulk_product):
    """Тест ошибки валидации для невалидного gross_requirement."""
    response = client.post("/api/v1/mrp/net-requirement", json={
        "product_id": str(sample_bulk_product.id),
        "gross_requirement": -500.0  # Невалидное отрицательное значение
    })
    
    assert response.status_code == 422
