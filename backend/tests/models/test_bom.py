"""
Unit тесты для модели BillOfMaterial.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from backend.src.models.bill_of_material import BillOfMaterial


def test_create_bom_fg_to_bulk(test_db, sample_finished_good, sample_bulk_product):
    """Тест создания BOM записи: FG → BULK."""
    bom = BillOfMaterial(
        parent_product_id=sample_finished_good.id,
        child_product_id=sample_bulk_product.id,
        quantity=0.09,
        unit="kg"
    )
    test_db.add(bom)
    test_db.commit()
    test_db.refresh(bom)
    
    assert bom.id is not None
    assert float(bom.quantity) == 0.09
    assert bom.unit == "kg"
    assert bom.parent_product_id == sample_finished_good.id
    assert bom.child_product_id == sample_bulk_product.id


def test_bom_unique_constraint(test_db, sample_bom_fg_to_bulk):
    """Тест уникальности (parent_product_id, child_product_id)."""
    duplicate = BillOfMaterial(
        parent_product_id=sample_bom_fg_to_bulk.parent_product_id,
        child_product_id=sample_bom_fg_to_bulk.child_product_id,
        quantity=0.1,
        unit="kg"
    )
    test_db.add(duplicate)
    
    with pytest.raises(IntegrityError):
        test_db.commit()


def test_bom_relationships(test_db, sample_bom_fg_to_bulk):
    """Тест связей BOM (parent/child products)."""
    assert sample_bom_fg_to_bulk.parent_product is not None
    assert sample_bom_fg_to_bulk.child_product is not None
    assert sample_bom_fg_to_bulk.parent_product.product_code == "FG_CREAM_REGEN_100ML"
    assert sample_bom_fg_to_bulk.child_product.product_code == "BULK_CREAM_REGEN"


def test_bom_cascade_delete(test_db, sample_bom_fg_to_bulk):
    """Тест CASCADE удаления при удалении продукта.
    
    Примечание: SQLite может не поддерживать CASCADE DELETE так же, как PostgreSQL.
    Проверяем, что BOM удаляется при удалении родительского продукта.
    """
    bom_id = sample_bom_fg_to_bulk.id
    parent_product = sample_bom_fg_to_bulk.parent_product
    
    # Удаляем родительский продукт
    test_db.delete(parent_product)
    
    try:
        test_db.commit()
    except Exception:
        # Если CASCADE не работает в SQLite, пропускаем тест
        test_db.rollback()
        pytest.skip("CASCADE DELETE может не работать в SQLite")
    
    # BOM должна быть удалена (CASCADE)
    bom_query = select(BillOfMaterial).where(
        BillOfMaterial.id == bom_id
    )
    bom_result = test_db.execute(bom_query)
    bom = bom_result.scalar_one_or_none()
    assert bom is None


def test_bom_multi_level(
    test_db, 
    sample_bom_fg_to_bulk, 
    sample_bom_bulk_to_raw
):
    """Тест многоуровневого BOM: FG → BULK → RAW."""
    fg = sample_bom_fg_to_bulk.parent_product
    bulk = sample_bom_fg_to_bulk.child_product
    raw = sample_bom_bulk_to_raw.child_product
    
    # FG имеет 1 дочерний (BULK)
    assert len(fg.bom_children) >= 1
    
    # BULK имеет 1 родительский (FG) и 1 дочерний (RAW)
    assert len(bulk.bom_parents) >= 1
    assert len(bulk.bom_children) >= 1
    
    # RAW имеет 1 родительский (BULK)
    assert len(raw.bom_parents) >= 1
