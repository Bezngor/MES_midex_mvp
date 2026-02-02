"""
Очистка всех таблиц БД (для чистого тестирования).
Запуск из корня репозитория: python -m backend.src.db.clear_all_tables

Внимание: необратимо удаляет все данные. Использовать только в dev/test.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Корень репозитория в PYTHONPATH для импорта backend
repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from sqlalchemy import text
from backend.src.db.session import engine, DATABASE_URL


# Порядок: от таблиц-зависимостей к корневым (соблюдение FK).
TABLES_ORDER = [
    "genealogy_records",
    "quality_inspections",
    "production_tasks",
    "route_operations",
    "manufacturing_orders",
    "batches",
    "work_center_capacities",
    "inventory_balances",
    "bill_of_materials",
    "dsiz_workforce_requirements",
    "dsiz_base_rates",
    "dsiz_product_work_center_routing",
    "dsiz_changeover_matrix",
    "dsiz_work_center_modes",
    "manufacturing_routes",
    "product_routing_rules",
    "products",
    "work_centers",
]


def clear_all_tables() -> None:
    with engine.begin() as conn:
        for table in TABLES_ORDER:
            try:
                conn.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))
            except Exception as e:
                if "does not exist" in str(e).lower():
                    continue
                raise
    print("All tables cleared.")


if __name__ == "__main__":
    print("Database:", DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "(from env)")
    print("Clearing all tables...")
    clear_all_tables()
