"""
Pytest fixtures for MES backend tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from backend.src.main import app
from backend.src.db.session import Base, get_db
from backend.src.models.work_center import WorkCenter
from backend.src.models.manufacturing_route import ManufacturingRoute
from backend.src.models.route_operation import RouteOperation
from backend.src.models.enums import WorkCenterStatus

# Настройка тестовой БД (in-memory SQLite)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """
    Создаёт тестовую БД-сессию с rollback после теста.
    """
    # Создаём все таблицы
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
        # Удаляем все таблицы после теста
        Base.metadata.drop_all(bind=engine)


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
    yield TestClient(app)
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
