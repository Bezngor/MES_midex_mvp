"""
Unit-тесты для OrderImportService.

Покрытие: импорт Excel/CSV, валидация, OrderSnapshot, маппинг приоритетов.
"""

import io
from datetime import date, datetime, timezone
from uuid import uuid4

import pandas as pd
import pytest

from backend.customizations.dsiz.services.order_import_service import OrderImportService
from backend.customizations.dsiz.schemas.order_import import PRIORITY_MAPPING
from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.order_snapshot import OrderSnapshot
from backend.core.models.product import Product
from backend.core.models.enums import OrderStatus, OrderType, ProductType


@pytest.fixture
def sample_product_for_import(test_db):
    """Продукт для тестов импорта (FG по product_code)."""
    product = Product(
        id=uuid4(),
        product_code="FG_IMPORT_TEST_001",
        product_name="Тестовый продукт для импорта",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="pcs",
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)
    return product


# ---------------------------------------------------------------------------
# Excel импорт
# ---------------------------------------------------------------------------


def test_import_excel_valid_success(test_db, sample_product_for_import):
    """Успешный импорт валидного Excel файла."""
    df = pd.DataFrame(
        [
            {
                "order_number": "ORD-IMPORT-001",
                "customer": "Тестовый клиент",
                "product_sku": sample_product_for_import.product_code,
                "quantity": 100,
                "due_date": "2026-03-15",
                "priority": "Обычный",
            }
        ]
    )
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)
    file_bytes = buffer.read()

    service = OrderImportService(test_db)
    result = service.import_from_excel(file_bytes, "test.xlsx")

    assert result.total_rows == 1
    assert result.imported_count == 1
    assert len(result.errors) == 0
    assert len(result.imported_order_ids) == 1

    order = test_db.query(ManufacturingOrder).filter(
        ManufacturingOrder.order_number == "ORD-IMPORT-001"
    ).first()
    assert order is not None
    assert order.order_type == OrderType.CUSTOMER.value
    assert order.priority == "NORMAL"
    assert order.status == OrderStatus.PLANNED
    assert str(order.product_id) == str(sample_product_for_import.id)
    assert float(order.quantity) == 100
    assert order.source_status == "IMPORT"


def test_import_excel_creates_order_snapshot(test_db, sample_product_for_import):
    """Проверка создания OrderSnapshot для каждого импортированного заказа."""
    df = pd.DataFrame(
        [
            {
                "order_number": "ORD-SNAPSHOT-001",
                "customer": "Клиент",
                "product_sku": sample_product_for_import.product_code,
                "quantity": 50,
                "due_date": "2026-04-01",
                "priority": "Высокий",
            }
        ]
    )
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    service = OrderImportService(test_db)
    result = service.import_from_excel(buffer.read(), "test.xlsx")

    assert result.imported_count == 1
    order_id = result.imported_order_ids[0]

    snapshot = test_db.query(OrderSnapshot).filter(
        OrderSnapshot.order_id == order_id,
        OrderSnapshot.snapshot_type == "IMPORT",
    ).first()
    assert snapshot is not None
    assert snapshot.order_number == "ORD-SNAPSHOT-001"
    assert snapshot.product_id == str(sample_product_for_import.id)
    assert float(snapshot.quantity) == 50
    assert snapshot.priority == "HIGH"  # Высокий -> HIGH
    assert snapshot.order_type == OrderType.CUSTOMER.value


# ---------------------------------------------------------------------------
# CSV импорт
# ---------------------------------------------------------------------------


def test_import_csv_valid_success(test_db, sample_product_for_import):
    """Успешный импорт валидного CSV файла."""
    csv_content = (
        "order_number,customer,product_sku,quantity,due_date,priority\n"
        f"ORD-CSV-001,Клиент CSV,{sample_product_for_import.product_code},200,2026-05-10,Срочно\n"
    )
    file_bytes = csv_content.encode("utf-8")

    service = OrderImportService(test_db)
    result = service.import_from_csv(file_bytes, "orders.csv")

    assert result.total_rows == 1
    assert result.imported_count == 1
    assert len(result.errors) == 0
    assert len(result.imported_order_ids) == 1

    order = test_db.query(ManufacturingOrder).filter(
        ManufacturingOrder.order_number == "ORD-CSV-001"
    ).first()
    assert order is not None
    assert order.priority == "URGENT"  # Срочно -> URGENT
    assert order.order_type == OrderType.CUSTOMER.value


def test_import_csv_date_format_ddmmyyyy(test_db, sample_product_for_import):
    """CSV с датой в формате DD.MM.YYYY."""
    csv_content = (
        "order_number,customer,product_sku,quantity,due_date,priority\n"
        f"ORD-DATE-001,Клиент,{sample_product_for_import.product_code},10,15.06.2026,Низкий\n"
    )
    file_bytes = csv_content.encode("utf-8")

    service = OrderImportService(test_db)
    result = service.import_from_csv(file_bytes, "orders.csv")

    assert result.imported_count == 1
    order = test_db.query(ManufacturingOrder).filter(
        ManufacturingOrder.order_number == "ORD-DATE-001"
    ).first()
    assert order is not None
    assert order.due_date.date() == date(2026, 6, 15)
    assert order.priority == "LOW"  # Низкий -> LOW


# ---------------------------------------------------------------------------
# Валидация: product_sku
# ---------------------------------------------------------------------------


def test_import_skips_invalid_product_sku(test_db, sample_product_for_import):
    """Пропуск строк с несуществующим product_sku."""
    df = pd.DataFrame(
        [
            {
                "order_number": "ORD-VALID",
                "customer": "Клиент",
                "product_sku": sample_product_for_import.product_code,
                "quantity": 10,
                "due_date": "2026-07-01",
                "priority": "Обычный",
            },
            {
                "order_number": "ORD-INVALID-SKU",
                "customer": "Клиент",
                "product_sku": "NONEXISTENT_SKU_XYZ",
                "quantity": 20,
                "due_date": "2026-07-02",
                "priority": "Обычный",
            },
        ]
    )
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    service = OrderImportService(test_db)
    result = service.import_from_excel(buffer.read(), "test.xlsx")

    assert result.total_rows == 2
    assert result.imported_count == 1
    assert len(result.errors) == 1
    assert result.errors[0].column == "product_sku"
    assert "NONEXISTENT_SKU_XYZ" in result.errors[0].error_message
    assert result.errors[0].value == "NONEXISTENT_SKU_XYZ"


# ---------------------------------------------------------------------------
# Валидация: due_date
# ---------------------------------------------------------------------------


def test_import_skips_past_due_date(test_db, sample_product_for_import):
    """Пропуск строк с датой в прошлом."""
    past_date = "2024-01-01"
    df = pd.DataFrame(
        [
            {
                "order_number": "ORD-PAST-DATE",
                "customer": "Клиент",
                "product_sku": sample_product_for_import.product_code,
                "quantity": 5,
                "due_date": past_date,
                "priority": "Обычный",
            }
        ]
    )
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    service = OrderImportService(test_db)
    result = service.import_from_excel(buffer.read(), "test.xlsx")

    assert result.total_rows == 1
    assert result.imported_count == 0
    assert len(result.errors) == 1
    assert "прошлом" in result.errors[0].error_message
    assert result.errors[0].column == "due_date"


def test_import_skips_invalid_date_format(test_db, sample_product_for_import):
    """Пропуск строк с некорректным форматом даты."""
    df = pd.DataFrame(
        [
            {
                "order_number": "ORD-BAD-DATE",
                "customer": "Клиент",
                "product_sku": sample_product_for_import.product_code,
                "quantity": 1,
                "due_date": "not-a-date",
                "priority": "Обычный",
            }
        ]
    )
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    service = OrderImportService(test_db)
    result = service.import_from_excel(buffer.read(), "test.xlsx")

    assert result.imported_count == 0
    assert len(result.errors) == 1
    assert "Некорректный" in result.errors[0].error_message or "формамат" in result.errors[0].error_message


# ---------------------------------------------------------------------------
# Дубликаты order_number
# ---------------------------------------------------------------------------


def test_import_skips_duplicate_order_number(test_db, sample_product_for_import):
    """Пропуск дубликатов order_number в рамках загрузки."""
    df = pd.DataFrame(
        [
            {
                "order_number": "ORD-DUP",
                "customer": "Клиент",
                "product_sku": sample_product_for_import.product_code,
                "quantity": 10,
                "due_date": "2026-08-01",
                "priority": "Обычный",
            },
            {
                "order_number": "ORD-DUP",
                "customer": "Клиент 2",
                "product_sku": sample_product_for_import.product_code,
                "quantity": 20,
                "due_date": "2026-08-02",
                "priority": "Высокий",
            },
        ]
    )
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    service = OrderImportService(test_db)
    result = service.import_from_excel(buffer.read(), "test.xlsx")

    assert result.total_rows == 2
    assert result.imported_count == 1
    assert len(result.errors) == 1
    assert "Дубликат" in result.errors[0].error_message
    assert result.errors[0].column == "order_number"


# ---------------------------------------------------------------------------
# Маппинг приоритетов
# ---------------------------------------------------------------------------


def test_priority_mapping_all_values(test_db, sample_product_for_import):
    """Проверка маппинга всех приоритетов: Срочно/Высокий/Обычный/Низкий."""
    for i, (rus, db_val) in enumerate(PRIORITY_MAPPING.items()):
        df = pd.DataFrame(
            [
                {
                    "order_number": f"ORD-PRIO-{i}",
                    "customer": "Клиент",
                    "product_sku": sample_product_for_import.product_code,
                    "quantity": 1,
                    "due_date": "2026-09-01",
                    "priority": rus,
                }
            ]
        )
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)

        service = OrderImportService(test_db)
        result = service.import_from_excel(buffer.read(), "test.xlsx")
        assert result.imported_count == 1, f"Priority {rus} failed"

        order = test_db.query(ManufacturingOrder).filter(
            ManufacturingOrder.order_number == f"ORD-PRIO-{i}"
        ).first()
        assert order.priority == db_val


# ---------------------------------------------------------------------------
# quantity validation
# ---------------------------------------------------------------------------


def test_import_skips_zero_quantity(test_db, sample_product_for_import):
    """Пропуск строк с quantity <= 0."""
    df = pd.DataFrame(
        [
            {
                "order_number": "ORD-ZERO",
                "customer": "Клиент",
                "product_sku": sample_product_for_import.product_code,
                "quantity": 0,
                "due_date": "2026-10-01",
                "priority": "Обычный",
            }
        ]
    )
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    service = OrderImportService(test_db)
    result = service.import_from_excel(buffer.read(), "test.xlsx")

    assert result.imported_count == 0
    assert len(result.errors) == 1
    assert "Количество" in result.errors[0].error_message or "больше" in result.errors[0].error_message


# ---------------------------------------------------------------------------
# Missing columns
# ---------------------------------------------------------------------------


def test_import_fails_missing_required_columns(test_db):
    """Ошибка при отсутствии обязательных колонок."""
    df = pd.DataFrame([{"order_number": "ORD-1", "quantity": 10}])  # нет customer, product_sku, due_date
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    service = OrderImportService(test_db)
    result = service.import_from_excel(buffer.read(), "test.xlsx")

    assert result.imported_count == 0
    assert len(result.errors) >= 1
    assert "Отсутствуют" in result.errors[0].error_message or "обязательные" in result.errors[0].error_message


# ---------------------------------------------------------------------------
# Empty file / invalid file
# ---------------------------------------------------------------------------


def test_import_empty_dataframe_returns_zero_imported(test_db, sample_product_for_import):
    """Пустой DataFrame возвращает 0 импортированных."""
    df = pd.DataFrame(columns=["order_number", "customer", "product_sku", "quantity", "due_date", "priority"])
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    service = OrderImportService(test_db)
    result = service.import_from_excel(buffer.read(), "empty.xlsx")

    assert result.total_rows == 0
    assert result.imported_count == 0
    assert len(result.imported_order_ids) == 0


def test_import_multiple_valid_rows_batch(test_db, sample_product_for_import):
    """Импорт нескольких валидных строк за один раз."""
    df = pd.DataFrame(
        [
            {
                "order_number": "ORD-BATCH-001",
                "customer": "Клиент A",
                "product_sku": sample_product_for_import.product_code,
                "quantity": 10,
                "due_date": "2026-11-01",
                "priority": "Обычный",
            },
            {
                "order_number": "ORD-BATCH-002",
                "customer": "Клиент B",
                "product_sku": sample_product_for_import.product_code,
                "quantity": 20,
                "due_date": "2026-11-02",
                "priority": "Высокий",
            },
        ]
    )
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    service = OrderImportService(test_db)
    result = service.import_from_excel(buffer.read(), "batch.xlsx")

    assert result.total_rows == 2
    assert result.imported_count == 2
    assert len(result.imported_order_ids) == 2

    # Проверяем, что созданы оба заказа и снимки
    for ord_num in ["ORD-BATCH-001", "ORD-BATCH-002"]:
        order = test_db.query(ManufacturingOrder).filter(
            ManufacturingOrder.order_number == ord_num
        ).first()
        assert order is not None
        snapshot = test_db.query(OrderSnapshot).filter(
            OrderSnapshot.order_id == order.id,
            OrderSnapshot.snapshot_type == "IMPORT",
        ).first()
        assert snapshot is not None
