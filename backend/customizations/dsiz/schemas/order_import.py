"""
Pydantic-схемы для импорта заказов из CSV/Excel.
"""

from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field


# Маппинг приоритетов из файла в значения БД
PRIORITY_MAPPING = {
    "Срочно": "URGENT",
    "Высокий": "HIGH",
    "Обычный": "NORMAL",
    "Низкий": "LOW",
}
VALID_PRIORITIES = set(PRIORITY_MAPPING.keys())
DEFAULT_PRIORITY = "Обычный"


class OrderImportRow(BaseModel):
    """Строка заказа из импортируемого файла."""

    order_number: str
    customer: str
    product_sku: str
    quantity: Decimal = Field(gt=0)
    due_date: date
    priority: str = Field(default=DEFAULT_PRIORITY)


class ImportError(BaseModel):
    """Ошибка валидации строки при импорте."""

    row_number: int
    column: str
    value: str
    error_message: str


class ImportResult(BaseModel):
    """Результат импорта заказов."""

    total_rows: int
    imported_count: int
    errors: list[ImportError] = Field(default_factory=list)
    imported_order_ids: list[UUID] = Field(default_factory=list)
