"""
Сервис импорта производственных заказов из CSV/Excel файлов.
"""

import io
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

import pandas as pd
from sqlalchemy.orm import Session

from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.order_snapshot import OrderSnapshot
from backend.core.models.product import Product
from backend.core.models.enums import OrderStatus, OrderType
from backend.customizations.dsiz.schemas.order_import import (
    ImportError,
    ImportResult,
    PRIORITY_MAPPING,
    VALID_PRIORITIES,
    DEFAULT_PRIORITY,
)

# Ожидаемые колонки в файле (поддержка разных вариантов написания)
COLUMN_ALIASES = {
    "order_number": ["order_number", "order number", "Номер заказа", "номер заказа"],
    "customer": ["customer", "Customer", "Клиент", "клиент", "Покупатель", "покупатель"],
    "product_sku": ["product_sku", "product sku", "sku", "Код продукции", "код продукции"],
    "quantity": ["quantity", "Quantity", "Количество", "количество"],
    "due_date": ["due_date", "due date", "Due Date", "Дата отгрузки", "дата отгрузки"],
    "priority": ["priority", "Priority", "Приоритет", "приоритет"],
}


def _normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Нормализует имена колонок к стандартным (snake_case)."""
    mapping = {}
    for std_name, aliases in COLUMN_ALIASES.items():
        for col in df.columns:
            col_stripped = str(col).strip().lower().replace(" ", "_")
            for alias in aliases:
                if col_stripped == alias.lower().replace(" ", "_"):
                    mapping[col] = std_name
                    break
    return df.rename(columns=mapping)


def _parse_date(val: Any) -> date | None:
    """Парсит дату из строки/значения. Поддержка YYYY-MM-DD, DD.MM.YYYY."""
    if pd.isna(val):
        return None
    if isinstance(val, date):
        return val
    if isinstance(val, datetime):
        return val.date()
    s = str(val).strip()
    if not s:
        return None
    # YYYY-MM-DD
    if len(s) == 10 and s[4] == "-" and s[7] == "-":
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            pass
    # DD.MM.YYYY
    if len(s) == 10 and s[2] == "." and s[5] == ".":
        try:
            return datetime.strptime(s, "%d.%m.%Y").date()
        except ValueError:
            pass
    return None


def _parse_priority(val: Any) -> str:
    """Нормализует приоритет или возвращает дефолт."""
    if pd.isna(val):
        return DEFAULT_PRIORITY
    s = str(val).strip()
    return s if s in VALID_PRIORITIES else DEFAULT_PRIORITY


def _parse_quantity(val: Any) -> Decimal | None:
    """Парсит количество."""
    if pd.isna(val):
        return None
    try:
        return Decimal(str(val).strip().replace(",", "."))
    except Exception:
        return None


class OrderImportService:
    """Сервис импорта заказов из CSV/Excel."""

    def __init__(self, db: Session):
        self.db = db

    def import_from_excel(self, file_bytes: bytes, filename: str) -> ImportResult:
        """
        Импорт заказов из Excel (.xlsx).

        Args:
            file_bytes: Байты файла
            filename: Имя файла (для логирования)

        Returns:
            ImportResult с результатами импорта
        """
        try:
            df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
        except Exception as e:
            return ImportResult(
                total_rows=0,
                imported_count=0,
                errors=[ImportError(row_number=0, column="file", value=filename, error_message=str(e))],
                imported_order_ids=[],
            )
        return self._process_dataframe(df)

    def import_from_csv(self, file_bytes: bytes, filename: str) -> ImportResult:
        """
        Импорт заказов из CSV.

        Args:
            file_bytes: Байты файла
            filename: Имя файла (для логирования)

        Returns:
            ImportResult с результатами импорта
        """
        try:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8-sig", dtype=str)
        except Exception as e:
            return ImportResult(
                total_rows=0,
                imported_count=0,
                errors=[ImportError(row_number=0, column="file", value=filename, error_message=str(e))],
                imported_order_ids=[],
            )
        return self._process_dataframe(df)

    def _process_dataframe(self, df: pd.DataFrame) -> ImportResult:
        """Валидация и импорт данных из DataFrame."""
        df = _normalize_column_names(df)

        required = {"order_number", "customer", "product_sku", "quantity", "due_date"}
        missing = required - set(df.columns)
        if missing:
            return ImportResult(
                total_rows=len(df),
                imported_count=0,
                errors=[
                    ImportError(
                        row_number=0,
                        column="file",
                        value="",
                        error_message=f"Отсутствуют обязательные колонки: {', '.join(sorted(missing))}",
                    )
                ],
                imported_order_ids=[],
            )

        if "priority" not in df.columns:
            df["priority"] = DEFAULT_PRIORITY

        today = datetime.now(timezone.utc).date()
        seen_order_numbers: set[str] = set()
        errors: list[ImportError] = []
        valid_rows: list[dict[str, Any]] = []

        for idx, row in df.iterrows():
            row_num = int(idx) + 2  # 1-based, +1 for header
            order_num = str(row.get("order_number", "")).strip()
            customer_val = str(row.get("customer", "")).strip()
            product_sku_val = str(row.get("product_sku", "")).strip()
            quantity_val = _parse_quantity(row.get("quantity"))
            due_date_val = _parse_date(row.get("due_date"))
            priority_val = _parse_priority(row.get("priority"))

            # Валидация order_number
            if not order_num:
                errors.append(
                    ImportError(
                        row_number=row_num,
                        column="order_number",
                        value=str(row.get("order_number", "")),
                        error_message="Номер заказа не может быть пустым",
                    )
                )
                continue
            if order_num in seen_order_numbers:
                errors.append(
                    ImportError(
                        row_number=row_num,
                        column="order_number",
                        value=order_num,
                        error_message="Дубликат номера заказа в рамках загрузки",
                    )
                )
                continue

            # Валидация customer
            if not customer_val:
                errors.append(
                    ImportError(
                        row_number=row_num,
                        column="customer",
                        value=str(row.get("customer", "")),
                        error_message="Поле клиента не может быть пустым",
                    )
                )
                continue

            # Валидация product_sku (существование в products)
            product = self.db.query(Product).filter(Product.product_code == product_sku_val).first()
            if not product:
                errors.append(
                    ImportError(
                        row_number=row_num,
                        column="product_sku",
                        value=product_sku_val,
                        error_message=f"Продукт с SKU '{product_sku_val}' не найден в справочнике",
                    )
                )
                continue

            # Валидация quantity
            if quantity_val is None or quantity_val <= 0:
                errors.append(
                    ImportError(
                        row_number=row_num,
                        column="quantity",
                        value=str(row.get("quantity", "")),
                        error_message="Количество должно быть больше 0",
                    )
                )
                continue

            # Валидация due_date
            if due_date_val is None:
                errors.append(
                    ImportError(
                        row_number=row_num,
                        column="due_date",
                        value=str(row.get("due_date", "")),
                        error_message="Некорректный формат даты (ожидается YYYY-MM-DD или DD.MM.YYYY)",
                    )
                )
                continue
            if due_date_val < today:
                errors.append(
                    ImportError(
                        row_number=row_num,
                        column="due_date",
                        value=str(due_date_val),
                        error_message="Дата выполнения не может быть в прошлом",
                    )
                )
                continue

            seen_order_numbers.add(order_num)
            valid_rows.append(
                {
                    "order_number": order_num,
                    "product_id": str(product.id),
                    "quantity": quantity_val,
                    "due_date": due_date_val,
                    "priority": PRIORITY_MAPPING.get(priority_val, "NORMAL"),
                }
            )

        if not valid_rows:
            return ImportResult(
                total_rows=len(df),
                imported_count=0,
                errors=errors,
                imported_order_ids=[],
            )

        # Batch insert: всё в одной транзакции
        imported_ids: list[UUID] = []
        try:
            for row_data in valid_rows:
                due_dt = datetime.combine(
                    row_data["due_date"],
                    datetime.min.time(),
                    tzinfo=timezone.utc,
                )
                order = ManufacturingOrder(
                    order_number=row_data["order_number"],
                    product_id=row_data["product_id"],
                    quantity=row_data["quantity"],
                    status=OrderStatus.PLANNED,
                    due_date=due_dt,
                    order_type=OrderType.CUSTOMER.value,
                    priority=row_data["priority"],
                    source_status="IMPORT",
                )
                self.db.add(order)
                self.db.flush()

                snapshot = OrderSnapshot(
                    order_id=order.id,
                    order_number=order.order_number,
                    product_id=order.product_id,
                    quantity=order.quantity,
                    status=order.status.value,
                    due_date=order.due_date,
                    order_type=order.order_type,
                    priority=order.priority,
                    source_status=order.source_status,
                    parent_order_id=order.parent_order_id,
                    source_order_ids=order.source_order_ids,
                    is_consolidated=order.is_consolidated,
                    snapshot_type="IMPORT",
                    notes="Импорт из файла",
                )
                self.db.add(snapshot)
                imported_ids.append(order.id)

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            errors.append(
                ImportError(
                    row_number=0,
                    column="transaction",
                    value="",
                    error_message=f"Ошибка при сохранении в БД: {e}",
                )
            )
            return ImportResult(
                total_rows=len(df),
                imported_count=0,
                errors=errors,
                imported_order_ids=[],
            )

        return ImportResult(
            total_rows=len(df),
            imported_count=len(imported_ids),
            errors=errors,
            imported_order_ids=imported_ids,
        )
