"""
Интеграционные тесты для API остатков (Inventory).
"""

import pytest


def test_list_inventory(client, sample_inventory_finished):
    """Тест GET /api/v1/inventory."""
    response = client.get("/api/v1/inventory")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1


def test_filter_inventory_by_product(client, sample_inventory_finished):
    """Тест GET /api/v1/inventory?product_id=..."""
    response = client.get(
        f"/api/v1/inventory?product_id={sample_inventory_finished.product_id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert all(
        inv["product_id"] == str(sample_inventory_finished.product_id)
        for inv in data["data"]
    )


def test_get_inventory_by_id(client, sample_inventory_finished):
    """Тест GET /api/v1/inventory/{id}."""
    response = client.get(f"/api/v1/inventory/{sample_inventory_finished.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["id"] == str(sample_inventory_finished.id)


def test_adjust_inventory_absolute(client, sample_bulk_product):
    """Тест POST /api/v1/inventory/adjust (абсолютное количество)."""
    response = client.post("/api/v1/inventory/adjust", json={
        "product_id": str(sample_bulk_product.id),
        "location": "WAREHOUSE",
        "quantity": 1000.0,
        "unit": "kg",
        "product_status": "FINISHED"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert float(data["data"]["quantity"]) == 1000.0


def test_adjust_inventory_delta(client, sample_inventory_finished):
    """Тест POST /api/v1/inventory/adjust (дельта)."""
    response = client.post("/api/v1/inventory/adjust", json={
        "product_id": str(sample_inventory_finished.product_id),
        "location": sample_inventory_finished.location,
        "quantity_delta": 100.0,
        "unit": "kg",
        "product_status": "FINISHED"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert float(data["data"]["quantity"]) == 750.0  # 650 + 100


def test_adjust_inventory_validation_error(client, sample_bulk_product):
    """Тест POST /api/v1/inventory/adjust (оба quantity и delta)."""
    response = client.post("/api/v1/inventory/adjust", json={
        "product_id": str(sample_bulk_product.id),
        "location": "WAREHOUSE",
        "quantity": 1000.0,
        "quantity_delta": 100.0,  # Нельзя указывать оба
        "unit": "kg",
        "product_status": "FINISHED"
    })
    
    # Pydantic валидация должна отклонить запрос
    assert response.status_code in [400, 422]


def test_delete_inventory(client, sample_inventory_finished):
    """Тест DELETE /api/v1/inventory/{id}."""
    response = client.delete(f"/api/v1/inventory/{sample_inventory_finished.id}")
    
    assert response.status_code == 200
    
    # Проверяем удаление
    get_response = client.get(f"/api/v1/inventory/{sample_inventory_finished.id}")
    assert get_response.status_code == 404
