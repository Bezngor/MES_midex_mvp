"""
Unit тесты для DSIZMRPService.

Покрытие: 90%+ (все основные сценарии).
"""

import pytest
from datetime import date, datetime, timezone, timedelta
from uuid import uuid4
from unittest.mock import patch

from backend.customizations.dsiz.services.dsiz_mrp_service import (
    DSIZMRPService, NetRequirement, BatchOrder
)
from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.product import Product
from backend.core.models.bill_of_material import BillOfMaterial
from backend.core.models.inventory_balance import InventoryBalance
from backend.core.models.enums import (
    OrderStatus, OrderType, ProductType, ProductStatus
)


# ============================================================================
# calculate_net_requirement Tests
# ============================================================================

def test_calculate_net_requirement_with_orders(test_db):
    """Тест: расчёт нетто-потребности с заказами ГП."""
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
    test_db.flush()
    
    # Создаём BOM: 1 ГП = 0.5 кг Bulk
    bom = BillOfMaterial(
        id=uuid4(),
        parent_product_id=fg_product.id,
        child_product_id=bulk_product.id,
        quantity=0.5,
        unit="кг"
    )
    test_db.add(bom)
    test_db.commit()
    test_db.flush()
    
    # Создаём заказы ГП
    order = ManufacturingOrder(
        order_number="ORD-001",
        product_id=str(fg_product.id),
        quantity=1000.0,  # 1000 шт ГП
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=10)
    )
    test_db.add(order)
    test_db.commit()
    test_db.flush()
    
    # Расчёт нетто-потребности
    service = DSIZMRPService(test_db)
    result = service.calculate_net_requirement("FG_PASTE_200ML", horizon_days=30)
    
    # 1000 шт * 0.5 кг = 500 кг
    assert result.fg_sku == "FG_PASTE_200ML"
    assert result.gross_requirement_kg == 500.0
    assert result.bulk_product_sku == "BULK_PASTE"


def test_calculate_net_requirement_with_bulk_inventory(test_db):
    """Тест: расчёт нетто-потребности с учётом остатков Bulk."""
    # Создаём ГП продукт
    fg_product = Product(
        id=uuid4(),
        product_code="FG_CREAM_100ML",
        product_name="Крем 100мл",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="шт"
    )
    
    # Создаём Bulk продукт
    bulk_product = Product(
        id=uuid4(),
        product_code="BULK_CREAM",
        product_name="Крем Bulk",
        product_type=ProductType.BULK.value,
        unit_of_measure="кг",
        shelf_life_days=30
    )
    
    test_db.add_all([fg_product, bulk_product])
    test_db.commit()
    
    # Создаём BOM: 1 ГП = 0.3 кг Bulk
    bom = BillOfMaterial(
        id=uuid4(),
        parent_product_id=fg_product.id,
        child_product_id=bulk_product.id,
        quantity=0.3,
        unit="кг"
    )
    test_db.add(bom)
    test_db.commit()
    
    # Создаём заказы ГП (1000 шт = 300 кг Bulk)
    order = ManufacturingOrder(
        order_number="ORD-002",
        product_id=str(fg_product.id),
        quantity=1000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=15)
    )
    test_db.add(order)
    test_db.commit()
    
    # Создаём остаток Bulk (200 кг с достаточным сроком годности)
    # expiry_date должен быть >= horizon_days (30 дней) от текущей даты
    expiry_date = datetime.now(timezone.utc) + timedelta(days=35)  # >= 30 дней (horizon_days)
    inventory = InventoryBalance(
        id=uuid4(),
        product_id=bulk_product.id,
        location="STORAGE_1",
        quantity=200.0,
        unit="кг",
        product_status=ProductStatus.FINISHED,
        expiry_date=expiry_date
    )
    test_db.add(inventory)
    test_db.commit()
    
    # Расчёт нетто-потребности
    service = DSIZMRPService(test_db)
    result = service.calculate_net_requirement("FG_CREAM_100ML", horizon_days=30)
    
    # 300 кг - 200 кг = 100 кг нетто
    assert result.gross_requirement_kg == 300.0
    assert result.bulk_available_kg == 200.0
    assert result.net_requirement_kg == 100.0


def test_calculate_net_requirement_with_expired_bulk(test_db):
    """Тест: остатки Bulk с истёкшим сроком годности не учитываются."""
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
    
    # Создаём заказы ГП (1000 шт = 500 кг Bulk)
    order = ManufacturingOrder(
        order_number="ORD-003",
        product_id=str(fg_product.id),
        quantity=1000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=10)
    )
    test_db.add(order)
    test_db.commit()
    
    # Создаём остаток Bulk с недостаточным сроком годности
    # expiry_date должен быть < horizon_days (30 дней) от текущей даты
    expiry_date = datetime.now(timezone.utc) + timedelta(days=25)  # < 30 дней (horizon_days)
    inventory = InventoryBalance(
        id=uuid4(),
        product_id=bulk_product.id,
        location="STORAGE_1",
        quantity=200.0,
        unit="кг",
        product_status=ProductStatus.FINISHED,
        expiry_date=expiry_date
    )
    test_db.add(inventory)
    test_db.commit()
    
    # Расчёт нетто-потребности
    service = DSIZMRPService(test_db)
    result = service.calculate_net_requirement("FG_PASTE_200ML", horizon_days=30)
    
    # Остаток не учитывается (истёкший срок) → нетто = валовая потребность
    assert result.gross_requirement_kg == 500.0
    assert result.bulk_available_kg == 0.0
    assert result.net_requirement_kg == 500.0


def test_calculate_net_requirement_no_orders(test_db):
    """Тест: расчёт нетто-потребности без заказов."""
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
    
    # Расчёт нетто-потребности
    service = DSIZMRPService(test_db)
    result = service.calculate_net_requirement("FG_PASTE_200ML", horizon_days=30)
    
    # Нет заказов → нетто = 0
    assert result.gross_requirement_kg == 0.0
    assert result.net_requirement_kg == 0.0


def test_calculate_net_requirement_sufficient_bulk(test_db):
    """Тест: остаток Bulk покрывает потребность → нетто = 0."""
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
    
    # Создаём заказы ГП (1000 шт = 500 кг Bulk)
    order = ManufacturingOrder(
        order_number="ORD-004",
        product_id=str(fg_product.id),
        quantity=1000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=20)
    )
    test_db.add(order)
    test_db.commit()
    
    # Создаём достаточный остаток Bulk (600 кг)
    # expiry_date должен быть >= horizon_days (30 дней) от текущей даты
    expiry_date = datetime.now(timezone.utc) + timedelta(days=35)  # >= 30 дней (horizon_days)
    inventory = InventoryBalance(
        id=uuid4(),
        product_id=bulk_product.id,
        location="STORAGE_1",
        quantity=600.0,
        unit="кг",
        product_status=ProductStatus.FINISHED,
        expiry_date=expiry_date
    )
    test_db.add(inventory)
    test_db.commit()
    
    # Расчёт нетто-потребности
    service = DSIZMRPService(test_db)
    result = service.calculate_net_requirement("FG_PASTE_200ML", horizon_days=30)
    
    # 500 кг - 600 кг = 0 кг нетто (достаточно остатка)
    assert result.gross_requirement_kg == 500.0
    assert result.bulk_available_kg == 600.0
    assert result.net_requirement_kg == 0.0


# ============================================================================
# plan_reactor_batches Tests
# ============================================================================

def test_plan_reactor_batches_cip_monday_shift1(test_db):
    """Тест: CIP понедельник смена 1 → нет варок."""
    # Создаём Bulk продукт
    bulk_product = Product(
        id=uuid4(),
        product_code="BULK_PASTE",
        product_name="Паста Bulk",
        product_type=ProductType.BULK.value,
        unit_of_measure="кг"
    )
    test_db.add(bulk_product)
    test_db.commit()
    
    # Понедельник, смена 1
    monday = date(2026, 1, 26)  # Понедельник
    mass_demand = {"BULK_PASTE": 1000.0}
    
    service = DSIZMRPService(test_db)
    batches = service.plan_reactor_batches(mass_demand, monday, shift_num=1)
    
    # CIP → нет варок
    assert batches == []


def test_plan_reactor_batches_underloading(test_db):
    """Тест: underloading 400кг пасты → 750кг batch."""
    # Создаём Bulk продукт
    bulk_product = Product(
        id=uuid4(),
        product_code="BULK_PASTE",
        product_name="Паста Bulk",
        product_type=ProductType.BULK.value,
        unit_of_measure="кг",
        batch_size_step_kg=100.0
    )
    test_db.add(bulk_product)
    test_db.commit()
    
    # Вторник, смена 1 (не CIP)
    tuesday = date(2026, 1, 27)
    mass_demand = {"BULK_PASTE": 400.0}  # 400 кг < min_load (750 кг)
    
    # Мокируем конфиг с режимами
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
    
    # Мокируем загрузку конфига
    with patch.object(DSIZMRPService, '_load_dsiz_config') as mock_load_config:
        mock_load_config.return_value = None
        service = DSIZMRPService(test_db)
        service.config = config_data
        batches = service.plan_reactor_batches(mass_demand, tuesday, shift_num=1)
        
        # Under-loading: 400 кг → 750 кг (min_load)
        assert len(batches) == 1
        assert batches[0].bulk_product_sku == "BULK_PASTE"
        assert batches[0].quantity_kg == 750.0
        assert batches[0].mode == "PASTE_MODE"
        assert batches[0].reactor_slot == 1


def test_plan_reactor_batches_limit_2_per_shift(test_db):
    """Тест: лимит 2 варки/смену."""
    # Создаём Bulk продукты
    bulk_paste = Product(
        id=uuid4(),
        product_code="BULK_PASTE",
        product_name="Паста Bulk",
        product_type=ProductType.BULK.value,
        unit_of_measure="кг"
    )
    bulk_cream = Product(
        id=uuid4(),
        product_code="BULK_CREAM",
        product_name="Крем Bulk",
        product_type=ProductType.BULK.value,
        unit_of_measure="кг"
    )
    bulk_soap = Product(
        id=uuid4(),
        product_code="BULK_SOAP",
        product_name="Мыло Bulk",
        product_type=ProductType.BULK.value,
        unit_of_measure="кг"
    )
    test_db.add_all([bulk_paste, bulk_cream, bulk_soap])
    test_db.commit()
    
    # Вторник, смена 1
    tuesday = date(2026, 1, 27)
    mass_demand = {
        "BULK_PASTE": 1000.0,
        "BULK_CREAM": 800.0,
        "BULK_SOAP": 600.0
    }
    
    config_data = {
        'reactor': {
            'max_cycles_per_shift': 2,
            'cip_schedule': 'monday_shift_1'
        },
        'work_center_modes': {
            'WC_REACTOR_MAIN': {
                'PASTE_MODE': {'min_load_kg': 750.0},
                'CREAM_MODE': {'min_load_kg': 700.0}
            }
        }
    }
    
    # Мокируем загрузку конфига
    with patch.object(DSIZMRPService, '_load_dsiz_config') as mock_load_config:
        mock_load_config.return_value = None
        service = DSIZMRPService(test_db)
        service.config = config_data
        batches = service.plan_reactor_batches(mass_demand, tuesday, shift_num=1)
        
        # Лимит 2 варки → только первые 2 продукта
        assert len(batches) == 2
        assert batches[0].reactor_slot == 1
        assert batches[1].reactor_slot == 2


def test_plan_reactor_batches_cream_mode(test_db):
    """Тест: определение режима CREAM_MODE для крема."""
    # Создаём Bulk продукт (крем)
    bulk_cream = Product(
        id=uuid4(),
        product_code="BULK_CREAM",
        product_name="Крем Bulk",
        product_type=ProductType.BULK.value,
        unit_of_measure="кг"
    )
    test_db.add(bulk_cream)
    test_db.commit()
    
    # Вторник, смена 1
    tuesday = date(2026, 1, 27)
    mass_demand = {"BULK_CREAM": 1000.0}
    
    config_data = {
        'reactor': {
            'max_cycles_per_shift': 2,
            'cip_schedule': 'monday_shift_1'
        },
        'work_center_modes': {
            'WC_REACTOR_MAIN': {
                'CREAM_MODE': {
                    'min_load_kg': 700.0,
                    'max_load_kg': 1400.0
                }
            }
        }
    }
    
    # Мокируем загрузку конфига
    with patch.object(DSIZMRPService, '_load_dsiz_config') as mock_load_config:
        mock_load_config.return_value = None
        service = DSIZMRPService(test_db)
        service.config = config_data
        batches = service.plan_reactor_batches(mass_demand, tuesday, shift_num=1)
        
        # Должен быть CREAM_MODE
        assert len(batches) == 1
        assert batches[0].mode == "CREAM_MODE"
        assert batches[0].bulk_product_sku == "BULK_CREAM"


def test_plan_reactor_batches_paste_mode(test_db):
    """Тест: определение режима PASTE_MODE для пасты."""
    # Создаём Bulk продукт (паста)
    bulk_paste = Product(
        id=uuid4(),
        product_code="BULK_PASTE",
        product_name="Паста Bulk",
        product_type=ProductType.BULK.value,
        unit_of_measure="кг"
    )
    test_db.add(bulk_paste)
    test_db.commit()
    
    # Вторник, смена 1
    tuesday = date(2026, 1, 27)
    mass_demand = {"BULK_PASTE": 1000.0}
    
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
    
    # Мокируем загрузку конфига
    with patch.object(DSIZMRPService, '_load_dsiz_config') as mock_load_config:
        mock_load_config.return_value = None
        service = DSIZMRPService(test_db)
        service.config = config_data
        batches = service.plan_reactor_batches(mass_demand, tuesday, shift_num=1)
        
        # Должен быть PASTE_MODE
        assert len(batches) == 1
        assert batches[0].mode == "PASTE_MODE"
        assert batches[0].bulk_product_sku == "BULK_PASTE"


def test_plan_reactor_batches_batch_rounding(test_db):
    """Тест: округление до кратности batch_size_step_kg."""
    # Создаём Bulk продукт с batch_size_step_kg
    bulk_product = Product(
        id=uuid4(),
        product_code="BULK_PASTE",
        product_name="Паста Bulk",
        product_type=ProductType.BULK.value,
        unit_of_measure="кг",
        batch_size_step_kg=500.0
    )
    test_db.add(bulk_product)
    test_db.commit()
    
    # Вторник, смена 1
    tuesday = date(2026, 1, 27)
    mass_demand = {"BULK_PASTE": 1200.0}  # 1200 кг → округление до 1500 кг (3 батча)
    
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
    
    # Мокируем загрузку конфига
    with patch.object(DSIZMRPService, '_load_dsiz_config') as mock_load_config:
        mock_load_config.return_value = None
        service = DSIZMRPService(test_db)
        service.config = config_data
        batches = service.plan_reactor_batches(mass_demand, tuesday, shift_num=1)
        
        # 1200 кг → округление до 1500 кг (3 * 500)
        assert len(batches) == 1
        assert batches[0].quantity_kg == 1500.0


def test_plan_reactor_batches_tuesday_shift1_allowed(test_db):
    """Тест: вторник смена 1 разрешена (не CIP)."""
    bulk_product = Product(
        id=uuid4(),
        product_code="BULK_PASTE",
        product_name="Паста Bulk",
        product_type=ProductType.BULK.value,
        unit_of_measure="кг"
    )
    test_db.add(bulk_product)
    test_db.commit()
    
    tuesday = date(2026, 1, 27)  # Вторник
    mass_demand = {"BULK_PASTE": 1000.0}
    
    config_data = {
        'reactor': {
            'max_cycles_per_shift': 2,
            'cip_schedule': 'monday_shift_1'
        },
        'work_center_modes': {
            'WC_REACTOR_MAIN': {
                'PASTE_MODE': {'min_load_kg': 750.0}
            }
        }
    }
    
    # Мокируем загрузку конфига
    with patch.object(DSIZMRPService, '_load_dsiz_config') as mock_load_config:
        mock_load_config.return_value = None
        service = DSIZMRPService(test_db)
        service.config = config_data
        batches = service.plan_reactor_batches(mass_demand, tuesday, shift_num=1)
        
        # Вторник не CIP → варки разрешены
        assert len(batches) == 1


def test_plan_reactor_batches_monday_shift2_allowed(test_db):
    """Тест: понедельник смена 2 разрешена (CIP только смена 1)."""
    bulk_product = Product(
        id=uuid4(),
        product_code="BULK_PASTE",
        product_name="Паста Bulk",
        product_type=ProductType.BULK.value,
        unit_of_measure="кг"
    )
    test_db.add(bulk_product)
    test_db.commit()
    
    monday = date(2026, 1, 26)  # Понедельник
    mass_demand = {"BULK_PASTE": 1000.0}
    
    config_data = {
        'reactor': {
            'max_cycles_per_shift': 2,
            'cip_schedule': 'monday_shift_1'
        },
        'work_center_modes': {
            'WC_REACTOR_MAIN': {
                'PASTE_MODE': {'min_load_kg': 750.0}
            }
        }
    }
    
    # Мокируем загрузку конфига
    with patch.object(DSIZMRPService, '_load_dsiz_config') as mock_load_config:
        mock_load_config.return_value = None
        service = DSIZMRPService(test_db)
        service.config = config_data
        batches = service.plan_reactor_batches(mass_demand, monday, shift_num=2)
        
        # Понедельник смена 2 не CIP → варки разрешены
        assert len(batches) == 1


# ============================================================================
# Integration Tests
# ============================================================================

def test_full_workflow_net_requirement_to_batches(test_db):
    """Тест: полный workflow от расчёта нетто до планирования варок."""
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
        shelf_life_days=30,
        batch_size_step_kg=500.0
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
        order_number="ORD-005",
        product_id=str(fg_product.id),
        quantity=2000.0,  # 2000 шт = 1000 кг Bulk
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=20)
    )
    test_db.add(order)
    test_db.commit()
    
    # Создаём остаток Bulk (200 кг)
    expiry_date = datetime.now(timezone.utc) + timedelta(days=50)
    inventory = InventoryBalance(
        id=uuid4(),
        product_id=bulk_product.id,
        location="STORAGE_1",
        quantity=200.0,
        unit="кг",
        product_status=ProductStatus.FINISHED,
        expiry_date=expiry_date
    )
    test_db.add(inventory)
    test_db.commit()
    
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
    
    # Мокируем загрузку конфига
    with patch.object(DSIZMRPService, '_load_dsiz_config') as mock_load_config:
        mock_load_config.return_value = None
        service = DSIZMRPService(test_db)
        service.config = config_data
        
        # 1. Расчёт нетто-потребности
        net_req = service.calculate_net_requirement("FG_PASTE_200ML", horizon_days=30)
        
        # 2. Планирование варок
        tuesday = date(2026, 1, 27)
        mass_demand = {net_req.bulk_product_sku: net_req.net_requirement_kg}
        batches = service.plan_reactor_batches(mass_demand, tuesday, shift_num=1)
        
        # Проверки
        assert net_req.net_requirement_kg == 800.0  # 1000 - 200
        assert len(batches) == 1
        assert batches[0].quantity_kg == 1000.0  # Округление 800 → 1000 (2 батча)


def test_calculate_net_requirement_invalid_fg_sku(test_db):
    """Тест: ошибка при несуществующем SKU ГП."""
    service = DSIZMRPService(test_db)
    
    with pytest.raises(ValueError, match="не найден"):
        service.calculate_net_requirement("INVALID_SKU", horizon_days=30)


def test_calculate_net_requirement_not_finished_good(test_db):
    """Тест: ошибка при продукте не типа FINISHED_GOOD."""
    bulk_product = Product(
        id=uuid4(),
        product_code="BULK_PASTE",
        product_name="Паста Bulk",
        product_type=ProductType.BULK.value,
        unit_of_measure="кг"
    )
    test_db.add(bulk_product)
    test_db.commit()
    
    service = DSIZMRPService(test_db)
    
    with pytest.raises(ValueError, match="не является типом FINISHED_GOOD"):
        service.calculate_net_requirement("BULK_PASTE", horizon_days=30)
