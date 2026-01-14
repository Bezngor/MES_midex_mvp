"""
Unit тесты для модели InventoryBalance.
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from backend.src.models.inventory_balance import InventoryBalance
from backend.src.models.enums import ProductStatus


def test_create_inventory_finished(test_db, sample_inventory_finished):
    """Тест создания остатка со статусом FINISHED."""
    assert sample_inventory_finished.id is not None
    assert float(sample_inventory_finished.quantity) == 650.0
    assert float(sample_inventory_finished.reserved_quantity) == 100.0
    assert sample_inventory_finished.product_status == ProductStatus.FINISHED.value


def test_inventory_available_quantity(test_db, sample_inventory_finished):
    """Тест вычисляемого свойства available_quantity."""
    assert float(sample_inventory_finished.available_quantity) == 550.0  # 650 - 100


def test_inventory_unique_constraint(test_db, sample_inventory_finished):
    """Тест уникальности (product_id, location, product_status)."""
    duplicate = InventoryBalance(
        product_id=sample_inventory_finished.product_id,
        location=sample_inventory_finished.location,
        quantity=100.0,
        unit="kg",
        product_status=sample_inventory_finished.product_status
    )
    test_db.add(duplicate)
    
    with pytest.raises(IntegrityError):
        test_db.commit()


def test_inventory_semi_finished(test_db, sample_inventory_semi_finished):
    """Тест создания остатка со статусом SEMI_FINISHED."""
    assert sample_inventory_semi_finished.product_status == ProductStatus.SEMI_FINISHED.value
    assert float(sample_inventory_semi_finished.quantity) == 500.0


def test_inventory_multiple_statuses_same_location(
    test_db, 
    sample_bulk_product
):
    """Тест: один продукт может иметь FINISHED и SEMI_FINISHED в одной локации."""
    inv1 = InventoryBalance(
        product_id=sample_bulk_product.id,
        location="WAREHOUSE",
        quantity=100.0,
        unit="kg",
        product_status=ProductStatus.FINISHED.value
    )
    inv2 = InventoryBalance(
        product_id=sample_bulk_product.id,
        location="WAREHOUSE",
        quantity=50.0,
        unit="kg",
        product_status=ProductStatus.SEMI_FINISHED.value
    )
    test_db.add_all([inv1, inv2])
    test_db.commit()
    
    query = select(InventoryBalance).where(
        InventoryBalance.product_id == sample_bulk_product.id,
        InventoryBalance.location == "WAREHOUSE"
    )
    result = test_db.execute(query)
    inventories = list(result.scalars().all())
    
    assert len(inventories) == 2


def test_inventory_expiry_date(test_db, sample_inventory_finished):
    """Тест отслеживания expiry_date."""
    assert sample_inventory_finished.production_date is not None
    assert sample_inventory_finished.expiry_date is not None
    assert sample_inventory_finished.expiry_date > sample_inventory_finished.production_date
