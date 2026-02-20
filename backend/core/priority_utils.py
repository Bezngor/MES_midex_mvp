"""
Общая логика расчёта приоритета срочности заказа.

Правила совпадают с MRP (см. MRP_GUIDE.md и mrp_service):
- «Отгрузить» / «Образец»: по дням до due_date → URGENT (<7), HIGH (7–14), NORMAL (14–30), LOW (>30).
- «В работе»: по дням до due_date → NORMAL (<30), LOW (≥30).

Используется при загрузке из CSV и при отдаче списков изменений заказов (единообразие с вкладкой MRP).
"""

from datetime import datetime, timezone
from typing import Optional

from backend.core.models.enums import OrderPriority


def compute_order_priority(
    due_date: Optional[datetime],
    source_status: Optional[str],
) -> str:
    """
    Вычислить приоритет заказа по due_date и source_status (те же правила, что в MRP).

    Args:
        due_date: Дата выполнения заказа (может быть None).
        source_status: Статус из 1С: «Отгрузить», «Образец», «В работе».

    Returns:
        URGENT | HIGH | NORMAL | LOW
    """
    now_utc = datetime.now(timezone.utc)
    if due_date is None:
        days_until_due = 999
    else:
        due = due_date if due_date.tzinfo else due_date.replace(tzinfo=timezone.utc)
        days_until_due = (due - now_utc).days

    status = (source_status or "").strip()
    is_in_work = "работе" in status.lower() or status == "В работе"

    if is_in_work:
        if days_until_due < 30:
            return OrderPriority.NORMAL.value
        return OrderPriority.LOW.value
    # Отгрузить / Образец
    if days_until_due < 7:
        return OrderPriority.URGENT.value
    if days_until_due < 14:
        return OrderPriority.HIGH.value
    if days_until_due < 30:
        return OrderPriority.NORMAL.value
    return OrderPriority.LOW.value
