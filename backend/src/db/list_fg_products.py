"""
Выводит список всех ГП (product_type=FINISHED_GOOD) из БД: код и наименование.
Для составления маршрутов по каждому ГП.

Запуск из корня репозитория:
  python -m backend.src.db.list_fg_products
"""

from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from sqlalchemy import select
from backend.src.db.session import SessionLocal
from backend.core.models.product import Product
from backend.core.models.enums import ProductType


def main() -> None:
    db = SessionLocal()
    try:
        result = db.execute(
            select(Product.product_code, Product.product_name)
            .where(Product.product_type == ProductType.FINISHED_GOOD.value)
            .order_by(Product.product_name)
        )
        rows = result.all()
        print(f"Всего ГП: {len(rows)}\n")
        print("Код\tНаименование")
        print("-" * 80)
        for code, name in rows:
            print(f"{code}\t{name}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
