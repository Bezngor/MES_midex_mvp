"""
Unit тесты для модели Batch.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from backend.src.models.batch import Batch
from backend.src.models.enums import BatchStatus


def test_create_batch(test_db, sample_batch):
    """Тест создания батча."""
    assert sample_batch.id is not None
    assert sample_batch.batch_number == "BATCH-2026-001"
    assert sample_batch.status == BatchStatus.PLANNED.value
    assert float(sample_batch.quantity_kg) == 1000.0
    assert sample_batch.created_at is not None


def test_batch_number_unique_constraint(test_db, sample_batch):
    """Тест уникальности batch_number."""
    duplicate = Batch(
        batch_number=sample_batch.batch_number,
        product_id=sample_batch.product_id,
        quantity_kg=500.0,
        status=BatchStatus.PLANNED.value
    )
    test_db.add(duplicate)
    
    with pytest.raises(IntegrityError):
        test_db.commit()


def test_batch_relationships(test_db, sample_batch):
    """Тест связей батча (product, work_center)."""
    assert sample_batch.product is not None
    assert sample_batch.work_center is not None
    assert sample_batch.product.product_type == "BULK"


def test_batch_status_lifecycle(test_db, sample_batch):
    """Тест переходов статуса батча: PLANNED → IN_PROGRESS → COMPLETED."""
    # Запускаем батч
    sample_batch.status = BatchStatus.IN_PROGRESS.value
    sample_batch.started_at = datetime.now(timezone.utc)
    test_db.commit()
    test_db.refresh(sample_batch)
    
    assert sample_batch.status == BatchStatus.IN_PROGRESS.value
    assert sample_batch.started_at is not None
    
    # Завершаем батч
    sample_batch.status = BatchStatus.COMPLETED.value
    sample_batch.completed_at = datetime.now(timezone.utc)
    test_db.commit()
    test_db.refresh(sample_batch)
    
    assert sample_batch.status == BatchStatus.COMPLETED.value
    assert sample_batch.completed_at is not None


def test_batch_with_parent_order(
    test_db, 
    sample_bulk_product, 
    sample_work_centers,
    sample_manufacturing_order
):
    """Тест батча с parent_order_id."""
    batch = Batch(
        batch_number="BATCH-2026-CHILD",
        product_id=sample_bulk_product.id,
        quantity_kg=2000.0,
        status=BatchStatus.PLANNED.value,
        work_center_id=sample_work_centers[0].id,
        parent_order_id=sample_manufacturing_order.id
    )
    test_db.add(batch)
    test_db.commit()
    test_db.refresh(batch)
    
    assert batch.parent_order_id == sample_manufacturing_order.id
    assert batch.parent_order is not None
