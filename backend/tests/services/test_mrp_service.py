"""
Unit тесты для MRPService (Material Requirements Planning).
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from sqlalchemy import select

from backend.src.services.mrp_service import MRPService
from backend.src.models.manufacturing_order import ManufacturingOrder
from backend.src.models.product import Product
from backend.src.models.bill_of_material import BillOfMaterial
from backend.src.models.inventory_balance import InventoryBalance
from backend.src.models.enums import (
    OrderStatus, OrderType, OrderPriority,
    ProductType, ProductStatus
)


# ============================================================================
# Order Consolidation Tests
# ============================================================================

def test_consolidate_orders_single_product(
    test_db, 
    sample_finished_good
):
    """Тест консолидации с одним продуктом и несколькими заказами."""
    # Создаём SHIP заказы с разными датами выполнения
    order1 = ManufacturingOrder(
        order_number="CONS-001",
        product_id=str(sample_finished_good.id),  # product_id - String
        quantity=5000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=5)
    )
    order2 = ManufacturingOrder(
        order_number="CONS-002",
        product_id=str(sample_finished_good.id),
        quantity=3000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=10)
    )
    test_db.add_all([order1, order2])
    test_db.commit()
    
    # Консолидируем
    mrp = MRPService(test_db)
    result = mrp.consolidate_orders(horizon_days=30)
    
    assert len(result) == 1
    assert result[0]["product_id"] == sample_finished_good.id
    assert float(result[0]["total_quantity"]) == 8000.0  # 5000 + 3000
    assert result[0]["order_count"] == 2
    assert result[0]["priority"] == OrderPriority.URGENT.value  # <7 дней


def test_consolidate_orders_multiple_products(
    test_db,
    sample_finished_good,
    sample_packaging
):
    """Тест консолидации с несколькими разными продуктами."""
    order1 = ManufacturingOrder(
        order_number="CONS-003",
        product_id=str(sample_finished_good.id),
        quantity=1000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=5)
    )
    order2 = ManufacturingOrder(
        order_number="CONS-004",
        product_id=str(sample_packaging.id),
        quantity=2000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=5)
    )
    test_db.add_all([order1, order2])
    test_db.commit()
    
    mrp = MRPService(test_db)
    result = mrp.consolidate_orders(horizon_days=30)
    
    assert len(result) == 2
    product_ids = {r["product_id"] for r in result}
    assert sample_finished_good.id in product_ids
    assert sample_packaging.id in product_ids


def test_consolidate_orders_priority_urgent(test_db, sample_finished_good):
    """Тест приоритета URGENT (<7 дней)."""
    order = ManufacturingOrder(
        order_number="PRI-URGENT",
        product_id=str(sample_finished_good.id),
        quantity=1000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=5)
    )
    test_db.add(order)
    test_db.commit()
    
    mrp = MRPService(test_db)
    result = mrp.consolidate_orders(horizon_days=30)
    
    assert len(result) == 1
    assert result[0]["priority"] == OrderPriority.URGENT.value


def test_consolidate_orders_priority_high(test_db, sample_finished_good):
    """Тест приоритета HIGH (7-14 дней)."""
    order = ManufacturingOrder(
        order_number="PRI-HIGH",
        product_id=str(sample_finished_good.id),
        quantity=1000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=10)
    )
    test_db.add(order)
    test_db.commit()
    
    mrp = MRPService(test_db)
    result = mrp.consolidate_orders(horizon_days=30)
    
    assert len(result) == 1
    assert result[0]["priority"] == OrderPriority.HIGH.value


def test_consolidate_orders_priority_normal(test_db, sample_finished_good):
    """Тест приоритета NORMAL (14-30 дней)."""
    order = ManufacturingOrder(
        order_number="PRI-NORMAL",
        product_id=str(sample_finished_good.id),
        quantity=1000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=20)
    )
    test_db.add(order)
    test_db.commit()
    
    mrp = MRPService(test_db)
    result = mrp.consolidate_orders(horizon_days=30)
    
    assert len(result) == 1
    assert result[0]["priority"] == OrderPriority.NORMAL.value


def test_consolidate_orders_priority_low(test_db, sample_finished_good):
    """Тест приоритета LOW (>30 дней)."""
    order = ManufacturingOrder(
        order_number="PRI-LOW",
        product_id=str(sample_finished_good.id),
        quantity=1000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=40)
    )
    test_db.add(order)
    test_db.commit()
    
    mrp = MRPService(test_db)
    result = mrp.consolidate_orders(horizon_days=60)
    
    assert len(result) == 1
    assert result[0]["priority"] == OrderPriority.LOW.value


def test_consolidate_orders_highest_priority_wins(test_db, sample_finished_good):
    """Тест: выбирается наивысший приоритет при наличии нескольких заказов."""
    # Создаём 3 заказа: URGENT, HIGH, NORMAL
    orders = [
        ManufacturingOrder(
            order_number="PRI-MIX-1",
            product_id=str(sample_finished_good.id),
            quantity=1000.0,
            status=OrderStatus.SHIP,
            order_type=OrderType.CUSTOMER.value,
            due_date=datetime.now(timezone.utc) + timedelta(days=5)  # URGENT
        ),
        ManufacturingOrder(
            order_number="PRI-MIX-2",
            product_id=str(sample_finished_good.id),
            quantity=2000.0,
            status=OrderStatus.SHIP,
            order_type=OrderType.CUSTOMER.value,
            due_date=datetime.now(timezone.utc) + timedelta(days=10)  # HIGH
        ),
        ManufacturingOrder(
            order_number="PRI-MIX-3",
            product_id=str(sample_finished_good.id),
            quantity=3000.0,
            status=OrderStatus.SHIP,
            order_type=OrderType.CUSTOMER.value,
            due_date=datetime.now(timezone.utc) + timedelta(days=20)  # NORMAL
        )
    ]
    test_db.add_all(orders)
    test_db.commit()
    
    mrp = MRPService(test_db)
    result = mrp.consolidate_orders(horizon_days=30)
    
    assert len(result) == 1
    assert result[0]["priority"] == OrderPriority.URGENT.value  # Наивысший приоритет
    assert float(result[0]["total_quantity"]) == 6000.0  # Сумма всех заказов


def test_consolidate_orders_horizon_filter(test_db, sample_finished_good):
    """Тест: заказы за пределами горизонта исключаются."""
    order_inside = ManufacturingOrder(
        order_number="HOR-IN",
        product_id=str(sample_finished_good.id),
        quantity=1000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=10)
    )
    order_outside = ManufacturingOrder(
        order_number="HOR-OUT",
        product_id=str(sample_finished_good.id),
        quantity=2000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=40)
    )
    test_db.add_all([order_inside, order_outside])
    test_db.commit()
    
    mrp = MRPService(test_db)
    result = mrp.consolidate_orders(horizon_days=30)
    
    assert len(result) == 1
    assert float(result[0]["total_quantity"]) == 1000.0  # Только order_inside


def test_consolidate_orders_empty_when_no_ship_orders(test_db, sample_finished_good):
    """Тест: консолидация возвращает пустой список, когда нет SHIP заказов."""
    # Создаём только PLANNED заказ (должен быть проигнорирован)
    order = ManufacturingOrder(
        order_number="NOT-SHIP",
        product_id=str(sample_finished_good.id),
        quantity=1000.0,
        status=OrderStatus.PLANNED,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=5)
    )
    test_db.add(order)
    test_db.commit()
    
    mrp = MRPService(test_db)
    result = mrp.consolidate_orders(horizon_days=30)
    
    assert len(result) == 0


def test_consolidate_orders_earliest_latest_dates(test_db, sample_finished_good):
    """Тест: корректно отслеживаются самые ранние и поздние даты выполнения."""
    order1 = ManufacturingOrder(
        order_number="DATE-1",
        product_id=str(sample_finished_good.id),
        quantity=1000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=5)
    )
    order2 = ManufacturingOrder(
        order_number="DATE-2",
        product_id=str(sample_finished_good.id),
        quantity=2000.0,
        status=OrderStatus.SHIP,
        order_type=OrderType.CUSTOMER.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=20)
    )
    test_db.add_all([order1, order2])
    test_db.commit()
    
    mrp = MRPService(test_db)
    result = mrp.consolidate_orders(horizon_days=30)
    
    assert len(result) == 1
    assert result[0]["earliest_due_date"] == order1.due_date
    assert result[0]["latest_due_date"] == order2.due_date


# ============================================================================
# BOM Explosion Tests
# ============================================================================

def test_explode_bom_single_level(
    test_db,
    sample_finished_good,
    sample_bulk_product,
    sample_bom_fg_to_bulk
):
    """Тест взрыва BOM для одного уровня (FG → BULK)."""
    mrp = MRPService(test_db)
    result = mrp.explode_bom(sample_finished_good.id, 10000.0)
    
    assert sample_bulk_product.id in result
    assert result[sample_bulk_product.id] == 900.0  # 10000 * 0.09


def test_explode_bom_multi_level(
    test_db,
    sample_finished_good,
    sample_bulk_product,
    sample_raw_material,
    sample_bom_fg_to_bulk,
    sample_bom_bulk_to_raw
):
    """Тест взрыва BOM для многоуровневого (FG → BULK → RAW)."""
    mrp = MRPService(test_db)
    result = mrp.explode_bom(sample_finished_good.id, 10000.0)
    
    # Проверяем потребность в BULK
    assert sample_bulk_product.id in result
    assert result[sample_bulk_product.id] == 900.0  # 10000 * 0.09
    
    # Проверяем потребность в RAW
    assert sample_raw_material.id in result
    assert result[sample_raw_material.id] == 135.0  # 900 * 0.15


def test_explode_bom_multiple_children(
    test_db,
    sample_finished_good,
    sample_bulk_product,
    sample_packaging
):
    """Тест взрыва BOM с несколькими дочерними продуктами (FG → BULK + PACKAGING)."""
    # Создаём BOM записи
    bom_bulk = BillOfMaterial(
        parent_product_id=sample_finished_good.id,
        child_product_id=sample_bulk_product.id,
        quantity=0.09,
        unit="kg"
    )
    bom_pkg = BillOfMaterial(
        parent_product_id=sample_finished_good.id,
        child_product_id=sample_packaging.id,
        quantity=1.0,
        unit="pcs"
    )
    test_db.add_all([bom_bulk, bom_pkg])
    test_db.commit()
    
    mrp = MRPService(test_db)
    result = mrp.explode_bom(sample_finished_good.id, 10000.0)
    
    assert len(result) == 2
    assert result[sample_bulk_product.id] == 900.0  # 10000 * 0.09
    assert result[sample_packaging.id] == 10000.0  # 10000 * 1


def test_explode_bom_no_children(test_db, sample_raw_material):
    """Тест взрыва BOM для продукта без дочерних продуктов (RAW)."""
    mrp = MRPService(test_db)
    result = mrp.explode_bom(sample_raw_material.id, 1000.0)
    
    assert len(result) == 0  # RAW не имеет компонентов


def test_explode_bom_circular_dependency_protection(
    test_db,
    sample_finished_good,
    sample_bulk_product
):
    """Тест защиты от циклических зависимостей (max_levels)."""
    # Создаём циклический BOM (A → B → A)
    bom1 = BillOfMaterial(
        parent_product_id=sample_finished_good.id,
        child_product_id=sample_bulk_product.id,
        quantity=0.09,
        unit="kg"
    )
    bom2 = BillOfMaterial(
        parent_product_id=sample_bulk_product.id,
        child_product_id=sample_finished_good.id,
        quantity=1.0,
        unit="pcs"
    )
    test_db.add_all([bom1, bom2])
    test_db.commit()
    
    mrp = MRPService(test_db)
    
    with pytest.raises(ValueError, match="превысил максимальный уровень"):
        mrp.explode_bom(sample_finished_good.id, 100.0, max_levels=5)


def test_explode_bom_quantity_accumulation(
    test_db,
    sample_finished_good,
    sample_bulk_product,
    sample_raw_material
):
    """Тест: количества корректно накапливаются в многоуровневом BOM."""
    # FG → BULK (0.09 кг)
    # BULK → RAW (0.15 кг на кг BULK)
    bom1 = BillOfMaterial(
        parent_product_id=sample_finished_good.id,
        child_product_id=sample_bulk_product.id,
        quantity=0.09,
        unit="kg"
    )
    bom2 = BillOfMaterial(
        parent_product_id=sample_bulk_product.id,
        child_product_id=sample_raw_material.id,
        quantity=0.15,
        unit="kg"
    )
    test_db.add_all([bom1, bom2])
    test_db.commit()
    
    mrp = MRPService(test_db)
    result = mrp.explode_bom(sample_finished_good.id, 10000.0)
    
    # Ожидается: 10000 шт FG → 900 кг BULK → 135 кг RAW
    assert result[sample_bulk_product.id] == 900.0
    assert result[sample_raw_material.id] == 135.0


# ============================================================================
# Net Requirement Tests
# ============================================================================

def test_calculate_net_requirement_no_stock(test_db, sample_bulk_product):
    """Тест нетто-потребности без доступного запаса."""
    mrp = MRPService(test_db)
    net = mrp.calculate_net_requirement(sample_bulk_product.id, 1000.0)
    
    assert net == 1000.0


def test_calculate_net_requirement_sufficient_stock(
    test_db,
    sample_bulk_product,
    sample_inventory_finished
):
    """Тест нетто-потребности с достаточным запасом (производство не требуется)."""
    # sample_inventory_finished: 650 кг всего, 100 зарезервировано = 550 доступно
    mrp = MRPService(test_db)
    net = mrp.calculate_net_requirement(sample_bulk_product.id, 500.0)
    
    assert net == 0.0  # 500 - 550 = 0 (ограничено до 0)


def test_calculate_net_requirement_partial_stock(
    test_db,
    sample_bulk_product,
    sample_inventory_finished
):
    """Тест нетто-потребности с частичным запасом."""
    # 550 доступно, нужно 1000
    mrp = MRPService(test_db)
    net = mrp.calculate_net_requirement(sample_bulk_product.id, 1000.0)
    
    assert net == 450.0  # 1000 - 550


def test_calculate_net_requirement_ignores_semi_finished(
    test_db,
    sample_finished_good,
    sample_inventory_semi_finished
):
    """Тест: SEMI_FINISHED инвентарь игнорируется в расчёте нетто."""
    # sample_inventory_semi_finished: 500 шт SEMI_FINISHED (не должно учитываться)
    mrp = MRPService(test_db)
    net = mrp.calculate_net_requirement(sample_finished_good.id, 1000.0)
    
    assert net == 1000.0  # SEMI_FINISHED не учитывается


def test_calculate_net_requirement_ignores_reserved(
    test_db,
    sample_bulk_product
):
    """Тест: зарезервированное количество исключается из доступного запаса."""
    # Создаём инвентарь: 1000 кг всего, 300 зарезервировано = 700 доступно
    inventory = InventoryBalance(
        product_id=sample_bulk_product.id,
        location="WAREHOUSE",
        quantity=1000.0,
        reserved_quantity=300.0,
        unit="kg",
        product_status=ProductStatus.FINISHED.value
    )
    test_db.add(inventory)
    test_db.commit()
    
    mrp = MRPService(test_db)
    net = mrp.calculate_net_requirement(sample_bulk_product.id, 800.0)
    
    assert net == 100.0  # 800 - 700 доступно


def test_calculate_net_requirement_multiple_locations(
    test_db,
    sample_bulk_product
):
    """Тест расчёта нетто-потребности с инвентарём в нескольких локациях."""
    inv1 = InventoryBalance(
        product_id=sample_bulk_product.id,
        location="WAREHOUSE_A",
        quantity=300.0,
        reserved_quantity=0.0,
        unit="kg",
        product_status=ProductStatus.FINISHED.value
    )
    inv2 = InventoryBalance(
        product_id=sample_bulk_product.id,
        location="WAREHOUSE_B",
        quantity=400.0,
        reserved_quantity=100.0,
        unit="kg",
        product_status=ProductStatus.FINISHED.value
    )
    test_db.add_all([inv1, inv2])
    test_db.commit()
    
    mrp = MRPService(test_db)
    net = mrp.calculate_net_requirement(sample_bulk_product.id, 1000.0)
    
    # Всего доступно: (300 - 0) + (400 - 100) = 600
    assert net == 400.0  # 1000 - 600


# ============================================================================
# Batch Rounding Tests
# ============================================================================

def test_round_to_batch_exact_multiple(test_db, sample_bulk_product):
    """Тест округления, когда потребность является точным кратным шага батча."""
    # min=500, step=1000
    mrp = MRPService(test_db)
    rounded = mrp.round_to_batch(sample_bulk_product.id, 2000.0)
    
    assert rounded == 2000.0  # Уже кратное


def test_round_to_batch_round_up(test_db, sample_bulk_product):
    """Тест округления вверх до следующего батча."""
    mrp = MRPService(test_db)
    rounded = mrp.round_to_batch(sample_bulk_product.id, 1200.0)
    
    assert rounded == 2000.0  # Округляется вверх до 2 батчей


def test_round_to_batch_below_minimum(test_db, sample_bulk_product):
    """Тест округления, когда потребность ниже минимального размера батча."""
    mrp = MRPService(test_db)
    rounded = mrp.round_to_batch(sample_bulk_product.id, 300.0)
    
    assert rounded == 500.0  # Использует min_batch_size_kg


def test_round_to_batch_at_minimum(test_db, sample_bulk_product):
    """Тест округления, когда потребность точно равна минимальному размеру батча."""
    mrp = MRPService(test_db)
    rounded = mrp.round_to_batch(sample_bulk_product.id, 500.0)
    
    # Логика: если >= min, округляется до step (1000), а не остаётся на min
    assert rounded == 1000.0  # Округляется до step


def test_round_to_batch_between_min_and_step(test_db, sample_bulk_product):
    """Тест округления, когда потребность между min и step."""
    mrp = MRPService(test_db)
    rounded = mrp.round_to_batch(sample_bulk_product.id, 700.0)
    
    assert rounded == 1000.0  # Округляется вверх до step


def test_round_to_batch_non_bulk_product(test_db, sample_finished_good):
    """Тест ошибки, когда продукт не является типом BULK."""
    mrp = MRPService(test_db)
    
    with pytest.raises(ValueError, match="не является типом BULK"):
        mrp.round_to_batch(sample_finished_good.id, 1000.0)


def test_round_to_batch_product_not_found(test_db):
    """Тест ошибки, когда продукт не существует."""
    mrp = MRPService(test_db)
    
    with pytest.raises(ValueError, match="не найден"):
        mrp.round_to_batch(uuid4(), 1000.0)


def test_round_to_batch_no_step_defined(test_db):
    """Тест ошибки, когда batch_size_step_kg не определён."""
    # Создаём BULK продукт без batch_size_step_kg
    product = Product(
        product_code="BULK_NO_STEP",
        product_name="Bulk Without Step",
        product_type=ProductType.BULK.value,
        unit_of_measure="kg",
        min_batch_size_kg=500.0
        # batch_size_step_kg is None
    )
    test_db.add(product)
    test_db.commit()
    
    mrp = MRPService(test_db)
    
    with pytest.raises(ValueError, match="не имеет определённого batch_size_step_kg"):
        mrp.round_to_batch(product.id, 1000.0)


# ============================================================================
# Create Dependent Order Tests
# ============================================================================

def test_create_dependent_bulk_order(
    test_db,
    sample_bulk_product,
    sample_manufacturing_order
):
    """Тест создания зависимого INTERNAL_BULK заказа."""
    due_date = datetime.now(timezone.utc) + timedelta(days=7)
    
    mrp = MRPService(test_db)
    order = mrp.create_dependent_bulk_order(
        parent_order_id=sample_manufacturing_order.id,
        bulk_product_id=sample_bulk_product.id,
        quantity_kg=1000.0,
        due_date=due_date
    )
    
    assert order.id is not None
    assert order.order_type == OrderType.INTERNAL_BULK.value
    assert order.status == OrderStatus.PLANNED
    assert order.parent_order_id == sample_manufacturing_order.id
    assert float(order.quantity) == 1000.0
    # Сравниваем даты (БД может хранить без tzinfo, нормализуем обе)
    order_due = order.due_date.replace(tzinfo=timezone.utc) if order.due_date.tzinfo is None else order.due_date
    expected_due = due_date
    assert order_due == expected_due
    assert order.order_number.startswith("BULK-")


def test_create_dependent_bulk_order_without_parent(
    test_db,
    sample_bulk_product
):
    """Тест создания INTERNAL_BULK заказа без родителя (независимый заказ)."""
    due_date = datetime.now(timezone.utc) + timedelta(days=7)
    
    mrp = MRPService(test_db)
    order = mrp.create_dependent_bulk_order(
        bulk_product_id=sample_bulk_product.id,
        quantity_kg=1000.0,
        due_date=due_date,
        parent_order_id=None  # Нет родителя
    )
    
    assert order.id is not None
    assert order.parent_order_id is None
    assert order.order_type == OrderType.INTERNAL_BULK.value


def test_create_dependent_bulk_order_non_bulk_product(
    test_db,
    sample_finished_good,
    sample_manufacturing_order
):
    """Тест ошибки, когда продукт не является типом BULK."""
    mrp = MRPService(test_db)
    
    with pytest.raises(ValueError, match="не является типом BULK"):
        mrp.create_dependent_bulk_order(
            parent_order_id=sample_manufacturing_order.id,
            bulk_product_id=sample_finished_good.id,
            quantity_kg=1000.0,
            due_date=datetime.now(timezone.utc)
        )


def test_create_dependent_bulk_order_product_not_found(
    test_db,
    sample_manufacturing_order
):
    """Тест ошибки, когда продукт не существует."""
    mrp = MRPService(test_db)
    
    with pytest.raises(ValueError, match="не найден"):
        mrp.create_dependent_bulk_order(
            parent_order_id=sample_manufacturing_order.id,
            bulk_product_id=uuid4(),
            quantity_kg=1000.0,
            due_date=datetime.now(timezone.utc)
        )


def test_create_dependent_bulk_order_unique_number(
    test_db,
    sample_bulk_product,
    sample_manufacturing_order
):
    """Тест: номера заказов уникальны."""
    due_date = datetime.now(timezone.utc) + timedelta(days=7)
    mrp = MRPService(test_db)
    
    order1 = mrp.create_dependent_bulk_order(
        parent_order_id=sample_manufacturing_order.id,
        bulk_product_id=sample_bulk_product.id,
        quantity_kg=1000.0,
        due_date=due_date
    )
    
    order2 = mrp.create_dependent_bulk_order(
        parent_order_id=sample_manufacturing_order.id,
        bulk_product_id=sample_bulk_product.id,
        quantity_kg=2000.0,
        due_date=due_date
    )
    
    assert order1.order_number != order2.order_number
