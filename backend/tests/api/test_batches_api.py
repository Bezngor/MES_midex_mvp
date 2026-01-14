"""
Интеграционные тесты для API батчей.
"""

import pytest


def test_create_batch_with_auto_number(client, sample_bulk_product, sample_work_centers):
    """Тест POST /api/v1/batches (автогенерация batch_number)."""
    response = client.post("/api/v1/batches", json={
        "product_id": str(sample_bulk_product.id),
        "quantity_kg": 1000.0,
        "status": "PLANNED",
        "work_center_id": str(sample_work_centers[0].id)
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["batch_number"].startswith("BATCH-")
    assert data["data"]["status"] == "PLANNED"


def test_create_batch_with_custom_number(client, sample_bulk_product, sample_work_centers):
    """Тест POST /api/v1/batches (кастомный batch_number)."""
    response = client.post("/api/v1/batches", json={
        "batch_number": "CUSTOM-BATCH-001",
        "product_id": str(sample_bulk_product.id),
        "quantity_kg": 1500.0,
        "status": "PLANNED",
        "work_center_id": str(sample_work_centers[0].id)
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["batch_number"] == "CUSTOM-BATCH-001"


def test_list_batches(client, sample_batch):
    """Тест GET /api/v1/batches."""
    response = client.get("/api/v1/batches")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1


def test_filter_batches_by_status(client, sample_batch, sample_batch_in_progress):
    """Тест GET /api/v1/batches?status=IN_PROGRESS."""
    response = client.get("/api/v1/batches?status=IN_PROGRESS")
    
    assert response.status_code == 200
    data = response.json()
    assert all(batch["status"] == "IN_PROGRESS" for batch in data["data"])


def test_get_batch_by_id(client, sample_batch):
    """Тест GET /api/v1/batches/{id}."""
    response = client.get(f"/api/v1/batches/{sample_batch.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["batch_number"] == sample_batch.batch_number


def test_update_batch_status(client, sample_batch):
    """Тест PATCH /api/v1/batches/{id} (запуск батча)."""
    response = client.patch(
        f"/api/v1/batches/{sample_batch.id}",
        json={"status": "IN_PROGRESS"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["status"] == "IN_PROGRESS"


def test_delete_batch(client, sample_batch):
    """Тест DELETE /api/v1/batches/{id}."""
    response = client.delete(f"/api/v1/batches/{sample_batch.id}")
    
    assert response.status_code == 200
    
    # Проверяем удаление
    get_response = client.get(f"/api/v1/batches/{sample_batch.id}")
    assert get_response.status_code == 404
