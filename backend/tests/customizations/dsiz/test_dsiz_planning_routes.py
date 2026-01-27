"""
Интеграционные тесты для DSIZ Planning API endpoints.
"""

import pytest
from datetime import date, datetime, timezone, timedelta
from uuid import uuid4
from unittest.mock import patch

from backend.customizations.dsiz.services.dsiz_mrp_service import DSIZMRPService
from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.product import Product
from backend.core.models.bill_of_material import BillOfMaterial
from backend.core.models.inventory_balance import InventoryBalance
from backend.core.models.enums import (
    OrderStatus, OrderType, ProductType, ProductStatus
)


def test_run_dsiz_planning_success(client, test_db):
    """Тест: успешный запуск DSIZ планирования."""
    # Создаём ГП продукт
    fg_product = Product(
        id=uuid4(),
        product_code="FG_PASTE_200ML",
        product_name="Паста 200мл",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="шт"
    )
    
    # Создаём Bulk продукт
    bulk_product = Product(
        id=uuid4(),
        product_code="BULK_PASTE",
        product_name="Паста Bulk",
        product_type=ProductType.BULK.value,
        unit_of_measure="кг",
        shelf_life_days=30
    )
    
    test_db.add_all([fg_product, bulk_product])
    test_db.commit()
    
    # Создаём BOM
    bom = BillOfMaterial(
        id=uuid4(),
        parent_product_id=fg_product.id,
        child_product_id=bulk_product.id,
        quantity=0.5,
        unit="кг"
    )
    test_db.add(bom)
    test_db.commit()
    
    # Создаём заказы ГП
    order = ManufacturingOrder(
        order_number="ORD-001",
        product_id=str(fg_product.id),
        quantity=1000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=5)
    )
    test_db.add(order)
    test_db.commit()
    
    # Запускаем планирование
    request_data = {
        "planning_date": "2026-01-27",
        "horizon_days": 7,
        "manual_blocks": [],
        "workforce_state": {}
    }
    
    # Мокируем загрузку конфига для plan_reactor_batches
    config_data = {
        'reactor': {
            'max_cycles_per_shift': 2,
            'cip_schedule': 'monday_shift_1'
        },
        'work_center_modes': {
            'WC_REACTOR_MAIN': {
                'PASTE_MODE': {
                    'min_load_kg': 750.0,
                    'max_load_kg': 1500.0
                }
            }
        }
    }
    
    # Мокируем на уровне модуля роутера
    with patch('backend.customizations.dsiz.routes.dsiz_planning_routes.DSIZMRPService') as mock_service_class:
        # Создаём мок сервиса
        mock_service = mock_service_class.return_value
        mock_service.config = config_data
        
        # Мокируем calculate_net_requirement
        from backend.customizations.dsiz.services.dsiz_mrp_service import NetRequirement
        mock_service.calculate_net_requirement.return_value = NetRequirement(
            fg_sku="FG_PASTE_200ML",
            gross_requirement_kg=500.0,
            bulk_available_kg=0.0,
            net_requirement_kg=500.0,
            bulk_product_sku="BULK_PASTE"
        )
        
        # Мокируем plan_reactor_batches
        from backend.customizations.dsiz.services.dsiz_mrp_service import BatchOrder
        mock_service.plan_reactor_batches.return_value = [
            BatchOrder(
                bulk_product_sku="BULK_PASTE",
                quantity_kg=750.0,
                mode="PASTE_MODE",
                shift_date=date(2026, 1, 27),
                shift_num=1,
                reactor_slot=1
            )
        ]
        
        response = client.post("/api/v1/dsiz/planning/run", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "plan_id" in data
    assert data["planning_date"] == "2026-01-27"
    assert data["horizon_days"] == 7
    assert "operations" in data
    assert "warnings" in data
    assert "summary" in data


def test_run_dsiz_planning_with_manual_blocks(client, test_db):
    """Тест: планирование с ручными блокировками."""
    # Создаём ГП продукт
    fg_product = Product(
        id=uuid4(),
        product_code="FG_PASTE_200ML",
        product_name="Паста 200мл",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="шт"
    )
    
    # Создаём Bulk продукт
    bulk_product = Product(
        id=uuid4(),
        product_code="BULK_PASTE",
        product_name="Паста Bulk",
        product_type=ProductType.BULK.value,
        unit_of_measure="кг",
        shelf_life_days=30
    )
    
    test_db.add_all([fg_product, bulk_product])
    test_db.commit()
    
    # Создаём BOM
    bom = BillOfMaterial(
        id=uuid4(),
        parent_product_id=fg_product.id,
        child_product_id=bulk_product.id,
        quantity=0.5,
        unit="кг"
    )
    test_db.add(bom)
    test_db.commit()
    
    # Создаём заказы ГП
    order = ManufacturingOrder(
        order_number="ORD-002",
        product_id=str(fg_product.id),
        quantity=1000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=5)
    )
    test_db.add(order)
    test_db.commit()
    
    # Запускаем планирование с ручной блокировкой
    request_data = {
        "planning_date": "2026-01-27",
        "horizon_days": 7,
        "manual_blocks": [
            {
                "work_center_id": "WC_REACTOR_MAIN",
                "shift_date": "2026-01-27",
                "shift_num": 1,
                "reason": "Техническое обслуживание"
            }
        ],
        "workforce_state": {}
    }
    
    # Мокируем сервис
    with patch('backend.customizations.dsiz.routes.dsiz_planning_routes.DSIZMRPService') as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.config = {
            'reactor': {'max_cycles_per_shift': 2, 'cip_schedule': 'monday_shift_1'},
            'work_center_modes': {'WC_REACTOR_MAIN': {'PASTE_MODE': {'min_load_kg': 750.0}}}
        }
        
        from backend.customizations.dsiz.services.dsiz_mrp_service import NetRequirement
        mock_service.calculate_net_requirement.return_value = NetRequirement(
            fg_sku="FG_PASTE_200ML",
            gross_requirement_kg=500.0,
            bulk_available_kg=0.0,
            net_requirement_kg=500.0,
            bulk_product_sku="BULK_PASTE"
        )
        
        from backend.customizations.dsiz.services.dsiz_mrp_service import BatchOrder
        mock_service.plan_reactor_batches.return_value = []
        
        response = client.post("/api/v1/dsiz/planning/run", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Должно быть предупреждение о блокировке
    warnings = [w for w in data["warnings"] if "заблокирована" in w.get("message", "")]
    assert len(warnings) > 0


def test_run_dsiz_planning_no_fg_products(client, test_db):
    """Тест: планирование без ГП продуктов."""
    # Не создаём ГП продукты
    
    request_data = {
        "planning_date": "2026-01-27",
        "horizon_days": 7,
        "manual_blocks": [],
        "workforce_state": {}
    }
    
    response = client.post("/api/v1/dsiz/planning/run", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["operations"]) == 0
    # Должно быть предупреждение
    assert len(data["warnings"]) > 0
    assert "не найдено" in data["warnings"][0]["message"].lower()


def test_run_dsiz_planning_invalid_request(client, test_db):
    """Тест: невалидный запрос (отрицательный horizon_days)."""
    request_data = {
        "planning_date": "2026-01-27",
        "horizon_days": -1,  # Невалидное значение
        "manual_blocks": [],
        "workforce_state": {}
    }
    
    response = client.post("/api/v1/dsiz/planning/run", json=request_data)
    
    # Должна быть ошибка валидации
    assert response.status_code == 422


def test_run_dsiz_planning_with_workforce_state(client, test_db):
    """Тест: планирование с указанием состояния персонала."""
    # Создаём ГП продукт
    fg_product = Product(
        id=uuid4(),
        product_code="FG_PASTE_200ML",
        product_name="Паста 200мл",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="шт"
    )
    
    # Создаём Bulk продукт
    bulk_product = Product(
        id=uuid4(),
        product_code="BULK_PASTE",
        product_name="Паста Bulk",
        product_type=ProductType.BULK.value,
        unit_of_measure="кг",
        shelf_life_days=30
    )
    
    test_db.add_all([fg_product, bulk_product])
    test_db.commit()
    
    # Создаём BOM
    bom = BillOfMaterial(
        id=uuid4(),
        parent_product_id=fg_product.id,
        child_product_id=bulk_product.id,
        quantity=0.5,
        unit="кг"
    )
    test_db.add(bom)
    test_db.commit()
    
    # Создаём заказы ГП
    order = ManufacturingOrder(
        order_number="ORD-003",
        product_id=str(fg_product.id),
        quantity=1000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=5)
    )
    test_db.add(order)
    test_db.commit()
    
    # Запускаем планирование с состоянием персонала
    request_data = {
        "planning_date": "2026-01-27",
        "horizon_days": 7,
        "manual_blocks": [],
        "workforce_state": {
            "2026-01-27": {
                "OPERATOR": 5,
                "PACKER": 2
            }
        }
    }
    
    # Мокируем сервис
    with patch('backend.customizations.dsiz.routes.dsiz_planning_routes.DSIZMRPService') as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.config = {
            'reactor': {'max_cycles_per_shift': 2, 'cip_schedule': 'monday_shift_1'},
            'work_center_modes': {'WC_REACTOR_MAIN': {'PASTE_MODE': {'min_load_kg': 750.0}}}
        }
        
        from backend.customizations.dsiz.services.dsiz_mrp_service import NetRequirement
        mock_service.calculate_net_requirement.return_value = NetRequirement(
            fg_sku="FG_PASTE_200ML",
            gross_requirement_kg=500.0,
            bulk_available_kg=0.0,
            net_requirement_kg=500.0,
            bulk_product_sku="BULK_PASTE"
        )
        
        from backend.customizations.dsiz.services.dsiz_mrp_service import BatchOrder
        mock_service.plan_reactor_batches.return_value = [
            BatchOrder(
                bulk_product_sku="BULK_PASTE",
                quantity_kg=750.0,
                mode="PASTE_MODE",
                shift_date=date(2026, 1, 27),
                shift_num=1,
                reactor_slot=1
            )
        ]
        
        response = client.post("/api/v1/dsiz/planning/run", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "summary" in data
    assert data["summary"]["total_operations"] >= 0


def test_run_dsiz_planning_with_calculation_error(client, test_db):
    """Тест: обработка ошибки при расчёте нетто-потребности."""
    # Создаём ГП продукт
    fg_product = Product(
        id=uuid4(),
        product_code="FG_PASTE_200ML",
        product_name="Паста 200мл",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="шт"
    )
    
    test_db.add(fg_product)
    test_db.commit()
    
    request_data = {
        "planning_date": "2026-01-27",
        "horizon_days": 7,
        "manual_blocks": [],
        "workforce_state": {}
    }
    
    # Мокируем сервис, чтобы calculate_net_requirement выбрасывал ValueError
    with patch('backend.customizations.dsiz.routes.dsiz_planning_routes.DSIZMRPService') as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.config = {
            'reactor': {'max_cycles_per_shift': 2, 'cip_schedule': 'monday_shift_1'},
            'work_center_modes': {}
        }
        
        # Мокируем ошибку при расчёте
        mock_service.calculate_net_requirement.side_effect = ValueError("Продукт не найден")
        
        response = client.post("/api/v1/dsiz/planning/run", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Должно быть предупреждение об ошибке
    warnings = [w for w in data["warnings"] if "ошибка расчёта" in w.get("message", "").lower()]
    assert len(warnings) > 0


def test_run_dsiz_planning_with_general_exception(client, test_db):
    """Тест: обработка общего исключения при планировании."""
    # Создаём ГП продукт
    fg_product = Product(
        id=uuid4(),
        product_code="FG_PASTE_200ML",
        product_name="Паста 200мл",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="шт"
    )
    
    test_db.add(fg_product)
    test_db.commit()
    
    request_data = {
        "planning_date": "2026-01-27",
        "horizon_days": 7,
        "manual_blocks": [],
        "workforce_state": {}
    }
    
    # Мокируем сервис, чтобы выбрасывал общее исключение при вызове метода
    with patch('backend.customizations.dsiz.routes.dsiz_planning_routes.DSIZMRPService') as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.config = {
            'reactor': {'max_cycles_per_shift': 2, 'cip_schedule': 'monday_shift_1'},
            'work_center_modes': {}
        }
        # Мокируем ошибку при расчёте
        mock_service.calculate_net_requirement.side_effect = Exception("Критическая ошибка")
        
        response = client.post("/api/v1/dsiz/planning/run", json=request_data)
    
    # Должна быть ошибка 500
    assert response.status_code == 500
    data = response.json()
    assert "ошибка выполнения" in data.get("detail", "").lower()
