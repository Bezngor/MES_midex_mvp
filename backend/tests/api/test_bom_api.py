"""
Интеграционные тесты для API спецификаций (BOM).
"""

import pytest


def test_create_bom(client, sample_finished_good, sample_bulk_product):
    """Тест POST /api/v1/bill-of-materials."""
    response = client.post("/api/v1/bill-of-materials", json={
        "parent_product_id": str(sample_finished_good.id),
        "child_product_id": str(sample_bulk_product.id),
        "quantity": 0.09,
        "unit": "kg"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert float(data["data"]["quantity"]) == 0.09


def test_list_bom(client, sample_bom_fg_to_bulk):
    """Тест GET /api/v1/bill-of-materials."""
    response = client.get("/api/v1/bill-of-materials")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1


def test_filter_bom_by_parent(client, sample_bom_fg_to_bulk):
    """Тест GET /api/v1/bill-of-materials?parent_product_id=..."""
    response = client.get(
        f"/api/v1/bill-of-materials?parent_product_id={sample_bom_fg_to_bulk.parent_product_id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert all(
        bom["parent_product_id"] == str(sample_bom_fg_to_bulk.parent_product_id)
        for bom in data["data"]
    )


def test_get_bom_by_id(client, sample_bom_fg_to_bulk):
    """Тест GET /api/v1/bill-of-materials/{id}."""
    response = client.get(f"/api/v1/bill-of-materials/{sample_bom_fg_to_bulk.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["id"] == str(sample_bom_fg_to_bulk.id)


def test_update_bom(client, sample_bom_fg_to_bulk, sample_finished_good, sample_bulk_product):
    """Тест PATCH /api/v1/bill-of-materials/{id}."""
    # PATCH требует полные данные (BOMCreate схема)
    response = client.patch(
        f"/api/v1/bill-of-materials/{sample_bom_fg_to_bulk.id}",
        json={
            "parent_product_id": str(sample_finished_good.id),
            "child_product_id": str(sample_bulk_product.id),
            "quantity": 0.1,
            "unit": "kg"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert float(data["data"]["quantity"]) == 0.1


def test_delete_bom(client, sample_bom_fg_to_bulk):
    """Тест DELETE /api/v1/bill-of-materials/{id}."""
    response = client.delete(f"/api/v1/bill-of-materials/{sample_bom_fg_to_bulk.id}")
    
    assert response.status_code == 200
    
    # Проверяем удаление
    get_response = client.get(f"/api/v1/bill-of-materials/{sample_bom_fg_to_bulk.id}")
    assert get_response.status_code == 404
