"""
Интеграционные тесты для API мощностей рабочих центров.
"""

import pytest


def test_create_wc_capacity(client, sample_work_centers, sample_finished_good):
    """Тест POST /api/v1/work-center-capacities."""
    response = client.post("/api/v1/work-center-capacities", json={
        "work_center_id": str(sample_work_centers[0].id),
        "product_id": str(sample_finished_good.id),
        "capacity_per_shift": 20000.0,
        "unit": "pcs"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert float(data["data"]["capacity_per_shift"]) == 20000.0


def test_create_wc_capacity_duplicate(client, sample_wc_capacity_tubing_cream):
    """Тест создания дублирующейся мощности."""
    response = client.post("/api/v1/work-center-capacities", json={
        "work_center_id": str(sample_wc_capacity_tubing_cream.work_center_id),
        "product_id": str(sample_wc_capacity_tubing_cream.product_id),
        "capacity_per_shift": 10000.0,
        "unit": "pcs"
    })
    
    assert response.status_code == 400
    assert "уже существует" in response.json()["detail"].lower() or "already exists" in response.json()["detail"].lower()


def test_list_wc_capacities(client, sample_wc_capacity_tubing_cream):
    """Тест GET /api/v1/work-center-capacities."""
    response = client.get("/api/v1/work-center-capacities")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1


def test_filter_wc_capacity_by_work_center(client, sample_wc_capacity_tubing_cream):
    """Тест GET /api/v1/work-center-capacities?work_center_id=..."""
    response = client.get(
        f"/api/v1/work-center-capacities?work_center_id={sample_wc_capacity_tubing_cream.work_center_id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert all(
        cap["work_center_id"] == str(sample_wc_capacity_tubing_cream.work_center_id)
        for cap in data["data"]
    )


def test_get_wc_capacity_by_id(client, sample_wc_capacity_tubing_cream):
    """Тест GET /api/v1/work-center-capacities/{id}."""
    response = client.get(f"/api/v1/work-center-capacities/{sample_wc_capacity_tubing_cream.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["id"] == str(sample_wc_capacity_tubing_cream.id)


def test_update_wc_capacity(client, sample_wc_capacity_tubing_cream, sample_work_centers, sample_finished_good):
    """Тест PATCH /api/v1/work-center-capacities/{id}."""
    # PATCH требует полные данные (CapacityCreate схема)
    response = client.patch(
        f"/api/v1/work-center-capacities/{sample_wc_capacity_tubing_cream.id}",
        json={
            "work_center_id": str(sample_work_centers[0].id),
            "product_id": str(sample_finished_good.id),
            "capacity_per_shift": 18000.0,
            "unit": "pcs"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert float(data["data"]["capacity_per_shift"]) == 18000.0


def test_delete_wc_capacity(client, sample_wc_capacity_tubing_cream):
    """Тест DELETE /api/v1/work-center-capacities/{id}."""
    response = client.delete(
        f"/api/v1/work-center-capacities/{sample_wc_capacity_tubing_cream.id}"
    )
    
    assert response.status_code == 200
    
    # Проверяем удаление
    get_response = client.get(f"/api/v1/work-center-capacities/{sample_wc_capacity_tubing_cream.id}")
    assert get_response.status_code == 404
