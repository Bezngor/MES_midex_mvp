"""
Интеграционные тесты для API продуктов.
"""

import pytest


def test_create_product_bulk(client):
    """Тест POST /api/v1/products (BULK)."""
    response = client.post("/api/v1/products", json={
        "product_code": "API_BULK_001",
        "product_name": "API Test Bulk",
        "product_type": "BULK",
        "unit_of_measure": "kg",
        "min_batch_size_kg": 500.0,
        "batch_size_step_kg": 1000.0,
        "shelf_life_days": 7
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["product_code"] == "API_BULK_001"
    assert data["data"]["product_type"] == "BULK"
    assert data["data"]["id"] is not None


def test_create_product_finished_good(client):
    """Тест POST /api/v1/products (FINISHED_GOOD)."""
    response = client.post("/api/v1/products", json={
        "product_code": "API_FG_001",
        "product_name": "API Test FG",
        "product_type": "FINISHED_GOOD",
        "unit_of_measure": "pcs"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["product_type"] == "FINISHED_GOOD"
    assert data["data"]["min_batch_size_kg"] is None


def test_create_product_duplicate_code(client, sample_bulk_product):
    """Тест создания продукта с дублирующимся кодом."""
    response = client.post("/api/v1/products", json={
        "product_code": sample_bulk_product.product_code,
        "product_name": "Duplicate",
        "product_type": "RAW_MATERIAL",
        "unit_of_measure": "kg"
    })
    
    assert response.status_code == 400
    assert "уже существует" in response.json()["detail"].lower() or "already exists" in response.json()["detail"].lower()


def test_list_products(client, sample_bulk_product, sample_finished_good):
    """Тест GET /api/v1/products."""
    response = client.get("/api/v1/products")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 2


def test_filter_products_by_type(client, sample_bulk_product, sample_finished_good):
    """Тест GET /api/v1/products?product_type=BULK."""
    response = client.get("/api/v1/products?product_type=BULK")
    
    assert response.status_code == 200
    data = response.json()
    assert all(p["product_type"] == "BULK" for p in data["data"])


def test_get_product_by_id(client, sample_bulk_product):
    """Тест GET /api/v1/products/{id}."""
    response = client.get(f"/api/v1/products/{sample_bulk_product.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["product_code"] == sample_bulk_product.product_code


def test_get_product_not_found(client):
    """Тест GET /api/v1/products/{invalid_id}."""
    response = client.get("/api/v1/products/00000000-0000-0000-0000-000000000000")
    
    assert response.status_code == 404


def test_update_product(client, sample_bulk_product):
    """Тест PATCH /api/v1/products/{id}."""
    response = client.patch(
        f"/api/v1/products/{sample_bulk_product.id}",
        json={"product_name": "Updated Name"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["product_name"] == "Updated Name"


def test_delete_product(client, sample_bulk_product):
    """Тест DELETE /api/v1/products/{id}."""
    response = client.delete(f"/api/v1/products/{sample_bulk_product.id}")
    
    assert response.status_code == 200
    
    # Проверяем удаление
    get_response = client.get(f"/api/v1/products/{sample_bulk_product.id}")
    assert get_response.status_code == 404
