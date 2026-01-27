"""
Pytest fixtures for MES backend tests.
"""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import types as sa_types
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from backend.src.main import app
from backend.src.db.session import Base, get_db
from backend.core.models.work_center import WorkCenter
from backend.core.models.manufacturing_route import ManufacturingRoute
from backend.core.models.route_operation import RouteOperation
from backend.core.models.product import Product
from backend.core.models.bill_of_material import BillOfMaterial
from backend.core.models.batch import Batch
from backend.core.models.inventory_balance import InventoryBalance
from backend.core.models.work_center_capacity import WorkCenterCapacity
from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.enums import (
    WorkCenterStatus, ProductType, BatchStatus, ProductStatus, OrderStatus, OrderType, OrderPriority
)

def replace_jsonb_with_json():
    """
    Заменяет JSONB на JSON для всех таблиц в метаданных для совместимости с SQLite.
    """
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, JSONB):
                # Заменяем JSONB на JSON для SQLite
                column.type = sa_types.JSON()


@pytest.fixture(scope="function")
def test_db():
    """
    Создаёт тестовую БД-сессию с rollback после теста.
    Использует временную файловую БД SQLite для совместимости между сессиями.
    """
    import tempfile
    import os
    
    # Создаём временный файл БД
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    try:
        # Настройка тестовой БД (временный файл SQLite)
        test_engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False}
        )
        
        # Заменяем JSONB на JSON перед созданием таблиц
        replace_jsonb_with_json()
        
        # Создаём все таблицы
        Base.metadata.create_all(bind=test_engine)
        
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        db = TestSessionLocal()
        
        try:
            yield db
        finally:
            db.rollback()
            db.close()
            # Удаляем все таблицы
            Base.metadata.drop_all(bind=test_engine)
            test_engine.dispose()
    finally:
        # Удаляем временный файл БД
        os.close(db_fd)
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.fixture(scope="function")
def client(test_db):
    """
    FastAPI TestClient с подменой get_db.
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_work_centers(test_db):
    """
    Создаёт 3 WorkCenter для тестов.
    """
    wc1 = WorkCenter(
        name="CNC Lathe",
        resource_type="MACHINE",
        capacity_units_per_hour=10.0,
        status=WorkCenterStatus.AVAILABLE
    )
    wc2 = WorkCenter(
        name="Assembly",
        resource_type="STATION",
        capacity_units_per_hour=5.0,
        status=WorkCenterStatus.AVAILABLE
    )
    wc3 = WorkCenter(
        name="QC",
        resource_type="STATION",
        capacity_units_per_hour=8.0,
        status=WorkCenterStatus.AVAILABLE
    )
    test_db.add_all([wc1, wc2, wc3])
    test_db.commit()
    test_db.refresh(wc1)
    test_db.refresh(wc2)
    test_db.refresh(wc3)
    return [wc1, wc2, wc3]


@pytest.fixture
def sample_route(test_db, sample_work_centers):
    """
    Создаёт ManufacturingRoute с 3 операциями.
    """
    route = ManufacturingRoute(
        product_id="TEST-PROD-001",
        route_name="Test Route",
        description="Test manufacturing route"
    )
    test_db.add(route)
    test_db.commit()
    test_db.refresh(route)
    
    operations = [
        RouteOperation(
            route_id=route.id,
            operation_sequence=1,
            operation_name="Op1 - Machining",
            work_center_id=sample_work_centers[0].id,
            estimated_duration_minutes=30
        ),
        RouteOperation(
            route_id=route.id,
            operation_sequence=2,
            operation_name="Op2 - Assembly",
            work_center_id=sample_work_centers[1].id,
            estimated_duration_minutes=45
        ),
        RouteOperation(
            route_id=route.id,
            operation_sequence=3,
            operation_name="Op3 - Quality Check",
            work_center_id=sample_work_centers[2].id,
            estimated_duration_minutes=15
        ),
    ]
    test_db.add_all(operations)
    test_db.commit()
    
    for op in operations:
        test_db.refresh(op)
    
    return route


# ============================================================================
# Product Fixtures
# ============================================================================

@pytest.fixture
def sample_bulk_product(test_db):
    """Создаёт BULK продукт (масса для варки)."""
    product = Product(
        product_code="BULK_CREAM_REGEN",
        product_name="Масса Крем Регенерирующий",
        product_type=ProductType.BULK.value,
        unit_of_measure="kg",
        min_batch_size_kg=500.0,
        batch_size_step_kg=1000.0,
        shelf_life_days=7
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)
    return product


@pytest.fixture
def sample_finished_good(test_db):
    """Создаёт FINISHED_GOOD продукт."""
    product = Product(
        product_code="FG_CREAM_REGEN_100ML",
        product_name="Крем Регенерирующий 100 мл",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="pcs"
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)
    return product


@pytest.fixture
def sample_packaging(test_db):
    """Создаёт PACKAGING продукт (туба)."""
    product = Product(
        product_code="PKG_TUBE_100ML",
        product_name="Туба 100 мл",
        product_type=ProductType.PACKAGING.value,
        unit_of_measure="pcs"
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)
    return product


@pytest.fixture
def sample_raw_material(test_db):
    """Создаёт RAW_MATERIAL продукт."""
    product = Product(
        product_code="RAW_GLYCERIN",
        product_name="Глицерин",
        product_type=ProductType.RAW_MATERIAL.value,
        unit_of_measure="kg"
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)
    return product


# ============================================================================
# BOM Fixtures
# ============================================================================

@pytest.fixture
def sample_bom_fg_to_bulk(test_db, sample_finished_good, sample_bulk_product):
    """Создаёт BOM запись: FG → BULK."""
    bom = BillOfMaterial(
        parent_product_id=sample_finished_good.id,
        child_product_id=sample_bulk_product.id,
        quantity=0.09,
        unit="kg"
    )
    test_db.add(bom)
    test_db.commit()
    test_db.refresh(bom)
    return bom


@pytest.fixture
def sample_bom_fg_to_packaging(test_db, sample_finished_good, sample_packaging):
    """Создаёт BOM запись: FG → PACKAGING."""
    bom = BillOfMaterial(
        parent_product_id=sample_finished_good.id,
        child_product_id=sample_packaging.id,
        quantity=1.0,
        unit="pcs"
    )
    test_db.add(bom)
    test_db.commit()
    test_db.refresh(bom)
    return bom


@pytest.fixture
def sample_bom_bulk_to_raw(test_db, sample_bulk_product, sample_raw_material):
    """Создаёт BOM запись: BULK → RAW_MATERIAL."""
    bom = BillOfMaterial(
        parent_product_id=sample_bulk_product.id,
        child_product_id=sample_raw_material.id,
        quantity=0.15,
        unit="kg"
    )
    test_db.add(bom)
    test_db.commit()
    test_db.refresh(bom)
    return bom


# ============================================================================
# Batch Fixtures
# ============================================================================

@pytest.fixture
def sample_manufacturing_order(test_db, sample_bulk_product):
    """Создаёт ManufacturingOrder для тестов батчей."""
    from datetime import datetime, timezone
    order = ManufacturingOrder(
        order_number="TEST-ORDER-BATCH-001",
        product_id=sample_bulk_product.product_code,
        quantity=1000.0,
        status=OrderStatus.PLANNED,
        due_date=datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc),
        order_type=OrderType.INTERNAL_BULK.value
    )
    test_db.add(order)
    test_db.commit()
    test_db.refresh(order)
    return order


@pytest.fixture
def sample_batch(test_db, sample_bulk_product, sample_work_centers):
    """Создаёт батч для bulk варки."""
    batch = Batch(
        batch_number="BATCH-2026-001",
        product_id=sample_bulk_product.id,
        quantity_kg=1000.0,
        status=BatchStatus.PLANNED.value,
        work_center_id=sample_work_centers[0].id
    )
    test_db.add(batch)
    test_db.commit()
    test_db.refresh(batch)
    return batch


@pytest.fixture
def sample_batch_in_progress(test_db, sample_bulk_product, sample_work_centers):
    """Создаёт батч со статусом IN_PROGRESS."""
    from datetime import datetime, timezone
    batch = Batch(
        batch_number="BATCH-2026-002",
        product_id=sample_bulk_product.id,
        quantity_kg=1500.0,
        status=BatchStatus.IN_PROGRESS.value,
        work_center_id=sample_work_centers[0].id,
        started_at=datetime.now(timezone.utc)
    )
    test_db.add(batch)
    test_db.commit()
    test_db.refresh(batch)
    return batch


# ============================================================================
# Inventory Fixtures
# ============================================================================

@pytest.fixture
def sample_inventory_finished(test_db, sample_bulk_product):
    """Создаёт остаток инвентаря (FINISHED)."""
    from datetime import datetime, timezone, timedelta
    inventory = InventoryBalance(
        product_id=sample_bulk_product.id,
        location="CUB_1",
        quantity=650.0,
        unit="kg",
        product_status=ProductStatus.FINISHED.value,
        reserved_quantity=100.0,
        production_date=datetime.now(timezone.utc),
        expiry_date=datetime.now(timezone.utc) + timedelta(days=7)
    )
    test_db.add(inventory)
    test_db.commit()
    test_db.refresh(inventory)
    return inventory


@pytest.fixture
def sample_inventory_semi_finished(test_db, sample_finished_good):
    """Создаёт остаток инвентаря (SEMI_FINISHED)."""
    inventory = InventoryBalance(
        product_id=sample_finished_good.id,
        location="WAREHOUSE_SEMI",
        quantity=500.0,
        unit="pcs",
        product_status=ProductStatus.SEMI_FINISHED.value,
        reserved_quantity=0.0
    )
    test_db.add(inventory)
    test_db.commit()
    test_db.refresh(inventory)
    return inventory


# ============================================================================
# WorkCenterCapacity Fixtures
# ============================================================================

@pytest.fixture
def sample_wc_capacity_tubing_cream(test_db, sample_work_centers, sample_finished_good):
    """Создаёт WorkCenterCapacity: машина тубирования → крем 100мл."""
    capacity = WorkCenterCapacity(
        work_center_id=sample_work_centers[0].id,
        product_id=sample_finished_good.id,
        capacity_per_shift=15000.0,
        unit="pcs"
    )
    test_db.add(capacity)
    test_db.commit()
    test_db.refresh(capacity)
    return capacity


@pytest.fixture
def sample_wc_capacity_reactor_bulk(test_db, sample_work_centers, sample_bulk_product):
    """Создаёт WorkCenterCapacity: реактор → bulk крем."""
    capacity = WorkCenterCapacity(
        work_center_id=sample_work_centers[0].id,
        product_id=sample_bulk_product.id,
        capacity_per_shift=2000.0,
        unit="kg"
    )
    test_db.add(capacity)
    test_db.commit()
    test_db.refresh(capacity)
    return capacity
