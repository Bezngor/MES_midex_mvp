"""
Unit тесты для модели Product.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from backend.src.models.product import Product
from backend.src.models.enums import ProductType


def test_create_bulk_product(test_db):
    """Тест создания BULK продукта с параметрами батча."""
    product = Product(
        product_code="BULK_TEST_001",
        product_name="Test Bulk Product",
        product_type=ProductType.BULK.value,
        unit_of_measure="kg",
        min_batch_size_kg=500.0,
        batch_size_step_kg=1000.0,
        shelf_life_days=7
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)
    
    assert product.id is not None
    assert product.product_code == "BULK_TEST_001"
    assert product.product_type == ProductType.BULK.value
    assert float(product.min_batch_size_kg) == 500.0
    assert float(product.batch_size_step_kg) == 1000.0
    assert product.shelf_life_days == 7
    assert product.created_at is not None
    assert product.updated_at is not None


def test_create_finished_good(test_db):
    """Тест создания FINISHED_GOOD без полей батча."""
    product = Product(
        product_code="FG_TEST_001",
        product_name="Test Finished Good",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="pcs"
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)
    
    assert product.id is not None
    assert product.product_type == ProductType.FINISHED_GOOD.value
    assert product.min_batch_size_kg is None
    assert product.batch_size_step_kg is None
    assert product.shelf_life_days is None


def test_product_code_unique_constraint(test_db, sample_bulk_product):
    """Тест уникальности product_code."""
    duplicate = Product(
        product_code=sample_bulk_product.product_code,
        product_name="Duplicate Product",
        product_type=ProductType.RAW_MATERIAL.value,
        unit_of_measure="kg"
    )
    test_db.add(duplicate)
    
    with pytest.raises(IntegrityError):
        test_db.commit()


def test_product_relationships(test_db, sample_bom_fg_to_bulk):
    """Тест связей продукта (BOM parents/children)."""
    parent = sample_bom_fg_to_bulk.parent_product
    child = sample_bom_fg_to_bulk.child_product
    
    assert parent.product_type == ProductType.FINISHED_GOOD.value
    assert child.product_type == ProductType.BULK.value
    
    # Проверяем связи через запросы
    parent_query = select(Product).where(Product.id == parent.id)
    parent_result = test_db.execute(parent_query)
    parent_loaded = parent_result.scalar_one()
    
    assert len(parent_loaded.bom_children) >= 1
    assert len(child.bom_parents) >= 1


def test_product_types(test_db):
    """Тест всех типов продуктов."""
    types = [
        ProductType.RAW_MATERIAL,
        ProductType.BULK,
        ProductType.PACKAGING,
        ProductType.FINISHED_GOOD
    ]
    
    products = []
    for idx, ptype in enumerate(types):
        product = Product(
            product_code=f"TEST_{ptype.value}_{idx}",
            product_name=f"Test {ptype.value}",
            product_type=ptype.value,
            unit_of_measure="kg" if ptype in [ProductType.RAW_MATERIAL, ProductType.BULK] else "pcs"
        )
        products.append(product)
        test_db.add(product)
    
    test_db.commit()
    
    query = select(Product).where(Product.product_code.like("TEST_%"))
    result = test_db.execute(query)
    loaded_products = list(result.scalars().all())
    assert len(loaded_products) == 4
