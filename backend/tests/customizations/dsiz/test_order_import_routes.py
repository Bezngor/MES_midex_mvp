"""
API тесты для эндпоинта импорта заказов POST /api/v1/dsiz/orders/import.
"""

import io
from uuid import uuid4

import pandas as pd

from backend.core.models.product import Product
from backend.core.models.enums import ProductType


def test_import_orders_api_excel_success(client, test_db):
    """API: успешный импорт Excel через Swagger-совместимый endpoint."""
    product = Product(
        id=uuid4(),
        product_code="FG_API_IMPORT_001",
        product_name="Продукт для API-импорта",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="pcs",
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)

    df = pd.DataFrame(
        [
            {
                "order_number": "ORD-API-001",
                "customer": "API Клиент",
                "product_sku": product.product_code,
                "quantity": 25,
                "due_date": "2026-12-01",
                "priority": "Высокий",
            }
        ]
    )
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    response = client.post(
        "/api/v1/dsiz/orders/import",
        files={"file": ("orders.xlsx", buffer.read(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 1
    assert data["imported_count"] == 1
    assert len(data["imported_order_ids"]) == 1
    assert len(data["errors"]) == 0


def test_import_orders_api_csv_success(client, test_db):
    """API: успешный импорт CSV."""
    product = Product(
        id=uuid4(),
        product_code="FG_API_CSV_001",
        product_name="Продукт для CSV",
        product_type=ProductType.FINISHED_GOOD.value,
        unit_of_measure="pcs",
    )
    test_db.add(product)
    test_db.commit()

    csv_content = (
        "order_number,customer,product_sku,quantity,due_date,priority\n"
        f"ORD-API-CSV,Клиент API,{product.product_code},50,2026-12-15,Обычный\n"
    )
    file_bytes = csv_content.encode("utf-8")

    response = client.post(
        "/api/v1/dsiz/orders/import",
        files={"file": ("orders.csv", file_bytes, "text/csv")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["imported_count"] == 1


def test_import_orders_api_unsupported_format_returns_400(client):
    """API: неверный формат файла возвращает 400."""
    response = client.post(
        "/api/v1/dsiz/orders/import",
        files={"file": ("data.pdf", b"binary content", "application/pdf")},
    )
    assert response.status_code == 400
    assert "Поддерживаемые" in response.json().get("detail", "")


def test_import_orders_api_empty_file_returns_400(client):
    """API: пустой файл возвращает 400."""
    response = client.post(
        "/api/v1/dsiz/orders/import",
        files={
            "file": (
                "empty.xlsx",
                b"",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert response.status_code == 400
    assert "пуст" in response.json().get("detail", "").lower()
