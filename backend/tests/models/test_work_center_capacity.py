"""
Unit тесты для модели WorkCenterCapacity.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from backend.src.models.work_center_capacity import WorkCenterCapacity


def test_create_wc_capacity(test_db, sample_wc_capacity_tubing_cream):
    """Тест создания WorkCenterCapacity."""
    assert sample_wc_capacity_tubing_cream.id is not None
    assert float(sample_wc_capacity_tubing_cream.capacity_per_shift) == 15000.0
    assert sample_wc_capacity_tubing_cream.unit == "pcs"


def test_wc_capacity_unique_constraint(test_db, sample_wc_capacity_tubing_cream):
    """Тест уникальности (work_center_id, product_id)."""
    duplicate = WorkCenterCapacity(
        work_center_id=sample_wc_capacity_tubing_cream.work_center_id,
        product_id=sample_wc_capacity_tubing_cream.product_id,
        capacity_per_shift=10000.0,
        unit="pcs"
    )
    test_db.add(duplicate)
    
    with pytest.raises(IntegrityError):
        test_db.commit()


def test_wc_capacity_relationships(test_db, sample_wc_capacity_tubing_cream):
    """Тест связей WorkCenterCapacity."""
    assert sample_wc_capacity_tubing_cream.work_center is not None
    assert sample_wc_capacity_tubing_cream.product is not None


def test_wc_capacity_multiple_products(
    test_db,
    sample_work_centers,
    sample_finished_good,
    sample_bulk_product
):
    """Тест: один WorkCenter может иметь мощности для нескольких продуктов."""
    cap1 = WorkCenterCapacity(
        work_center_id=sample_work_centers[0].id,
        product_id=sample_finished_good.id,
        capacity_per_shift=15000.0,
        unit="pcs"
    )
    cap2 = WorkCenterCapacity(
        work_center_id=sample_work_centers[0].id,
        product_id=sample_bulk_product.id,
        capacity_per_shift=2000.0,
        unit="kg"
    )
    test_db.add_all([cap1, cap2])
    test_db.commit()
    
    query = select(WorkCenterCapacity).where(
        WorkCenterCapacity.work_center_id == sample_work_centers[0].id
    )
    result = test_db.execute(query)
    capacities = list(result.scalars().all())
    
    assert len(capacities) >= 2
