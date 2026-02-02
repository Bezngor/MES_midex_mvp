"""
Экспорт полного списка продуктов (ГП, Масса, Сырьё, Упаковка) в CSV для заполнения остатков.

Колонки: product_id, product_code, product_name, product_type, unit_of_measure,
         location, quantity, product_status, reserved_quantity.
Последние 4 колонки пустые — их заполняет пользователь в Excel, сохраняет как .xlsx.
После заполнения: конвертировать xlsx в CSV (inventory_xlsx_to_csv) и загрузить
(load_inventory_from_csv).

Запуск из корня репозитория:
  python -m backend.src.db.export_products_for_inventory
  python -m backend.src.db.export_products_for_inventory -o path/to/products_for_inventory.csv
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from sqlalchemy import select
from backend.src.db.session import SessionLocal
from backend.core.models.product import Product


# Типы продуктов, по которым считаются остатки (ГП, Масса, Сырьё, Упаковка)
PRODUCT_TYPES = ("FINISHED_GOOD", "BULK", "RAW_MATERIAL", "PACKAGING")

DEFAULT_OUTPUT = repo_root / ".cursor" / "_olds" / "info" / "products_for_inventory.csv"

HEADERS = [
    "product_id",
    "product_code",
    "product_name",
    "product_type",
    "unit_of_measure",
    "location",
    "quantity",
    "product_status",
    "reserved_quantity",
]


def main() -> None:
    import argparse
    p = argparse.ArgumentParser(description="Экспорт списка продуктов для заполнения остатков (CSV)")
    p.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT, help="Путь к выходному CSV")
    args = p.parse_args()

    db = SessionLocal()
    try:
        result = db.execute(
            select(
                Product.id,
                Product.product_code,
                Product.product_name,
                Product.product_type,
                Product.unit_of_measure,
            )
            .where(Product.product_type.in_(PRODUCT_TYPES))
            .order_by(Product.product_type, Product.product_name)
        )
        rows = result.all()
    finally:
        db.close()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(HEADERS)
        for r in rows:
            w.writerow([
                str(r[0]),
                r[1] or "",
                r[2] or "",
                r[3] or "",
                r[4] or "",
                "",  # location — заполняет пользователь
                "",  # quantity
                "",  # product_status: FINISHED или SEMI_FINISHED
                "",  # reserved_quantity
            ])

    print(f"Экспортировано продуктов: {len(rows)} -> {args.output}")
    print("Заполните в Excel колонки: location, quantity, product_status, reserved_quantity.")
    print("Сохраните как .xlsx, затем конвертируйте в CSV и загрузите: load_inventory_from_csv.")


if __name__ == "__main__":
    main()
