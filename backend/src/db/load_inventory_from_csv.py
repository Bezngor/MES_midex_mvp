"""
Загрузка остатков (inventory_balances) из CSV.

Ожидаемые колонки CSV (разделитель ;, UTF-8):
  product_code  — код продукта (или product_id — UUID)
  location      — локация (например CUB_1, MAIN)
  quantity      — количество (число)
  product_status — FINISHED или SEMI_FINISHED (по умолчанию FINISHED)
  reserved_quantity — зарезервировано (по умолчанию 0)

Строки без product_code/product_id, location или quantity пропускаются.
Уникальность: (product_id, location, product_status) — при совпадении запись обновляется.

Запуск из корня репозитория:
  python -m backend.src.db.load_inventory_from_csv -f path/to/inventory.csv
"""

from __future__ import annotations

import csv
import sys
import uuid
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db.session import SessionLocal
from backend.core.models.product import Product
from backend.core.models.inventory_balance import InventoryBalance
from backend.core.models.enums import ProductStatus


DEFAULT_CSV = repo_root / ".cursor" / "_olds" / "info" / "inventory.csv"

# Допустимые имена колонок (по первому совпадению)
COL_PRODUCT_CODE = ["product_code", "Код", "product code", "код продукта"]
COL_PRODUCT_NAME = ["product_name", "Наименование", "наименование", "product name", "product_name"]
COL_PRODUCT_ID = ["product_id", "id", "uuid"]
COL_LOCATION = ["location", "Локация", "локация", "Location"]
COL_QUANTITY = ["quantity", "Количество", "количество", "Quantity", "qty"]
COL_PRODUCT_STATUS = ["product_status", "Статус", "статус", "product status", "ProductStatus"]
COL_RESERVED = ["reserved_quantity", "reserved", "Зарезервировано", "зарезервировано"]


def _norm(s: str | None) -> str:
    if s is None:
        return ""
    return str(s).strip()


def _get_val(row: dict, row_lower: dict, candidates: list[str]) -> str:
    for c in candidates:
        if c in row and _norm(row.get(c)):
            return _norm(row[c])
        for k, v in row_lower.items():
            if k == c.lower().strip() and v:
                return _norm(v)
    return ""


def _parse_float(s: str) -> float | None:
    if not s:
        return None
    s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def load_csv(path: Path) -> list[dict]:
    """Читает CSV с разделителем ;, UTF-8. Первая строка — заголовки."""
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for r in reader:
            rows.append({k: (v or "").strip() for k, v in r.items() if k})
    return rows


def main() -> None:
    import argparse
    p = argparse.ArgumentParser(description="Загрузка остатков из CSV в inventory_balances")
    p.add_argument("-f", "--file", type=Path, default=DEFAULT_CSV, help="Путь к CSV с остатками")
    p.add_argument("--dry-run", action="store_true", help="Только показать, что будет загружено, не писать в БД")
    args = p.parse_args()

    if not args.file.exists():
        print(f"Ошибка: файл не найден: {args.file}")
        sys.exit(1)

    rows = load_csv(args.file)
    if not rows:
        print("Нет строк в CSV.")
        sys.exit(0)

    # Определяем колонки по первой строке
    first = rows[0]
    row_lower = {k.strip().lower(): k for k in first.keys()}

    def col(name_candidates: list[str]) -> str | None:
        for c in name_candidates:
            if c in first:
                return c
            for low, orig in row_lower.items():
                if c.lower().strip() == low:
                    return orig
        return None

    product_code_col = col(COL_PRODUCT_CODE)
    product_name_col = col(COL_PRODUCT_NAME)
    product_id_col = col(COL_PRODUCT_ID)
    location_col = col(COL_LOCATION)
    quantity_col = col(COL_QUANTITY)
    product_status_col = col(COL_PRODUCT_STATUS)
    reserved_col = col(COL_RESERVED)

    if not location_col or not quantity_col:
        print("Ошибка: в CSV должны быть колонки location (Локация) и quantity (Количество).")
        sys.exit(1)
    if not product_code_col and not product_id_col and not product_name_col:
        print("Ошибка: в CSV должна быть колонка product_code (Код), product_name (Наименование) или product_id.")
        sys.exit(1)

    db: Session = SessionLocal()
    try:
        created = 0
        updated = 0
        skipped = 0
        errors = []

        for i, row in enumerate(rows):
            product_code = _norm(row.get(product_code_col, "")) if product_code_col else ""
            product_name = _norm(row.get(product_name_col, "")) if product_name_col else ""
            product_id_str = _norm(row.get(product_id_col, "")) if product_id_col else ""
            location = _norm(row.get(location_col, ""))
            qty_val = _parse_float(_norm(row.get(quantity_col, "")))
            status_str = _norm(row.get(product_status_col, "")).upper() if product_status_col else "FINISHED"
            reserved_val = _parse_float(_norm(row.get(reserved_col, ""))) if reserved_col else 0.0

            if not location or qty_val is None or qty_val < 0:
                skipped += 1
                continue

            # Определить product_id: по UUID из CSV только если такой продукт есть в БД,
            # иначе — по product_code (чтобы старый CSV работал после prepare_test_env с новыми UUID).
            product_id = None
            if product_id_str:
                try:
                    uid = uuid.UUID(product_id_str)
                    if db.get(Product, uid) is not None:
                        product_id = uid
                except ValueError:
                    pass
            if not product_id and product_code:
                stmt = select(Product.id).where(Product.product_code == product_code).limit(1)
                res = db.execute(stmt).scalar_one_or_none()
                if res is not None:
                    product_id = res
            # Фолбэк по наименованию продукта (важно для связки dataset_customer_orders + inventory.xlsx):
            # если коды отличаются, но наименование совпадает.
            if not product_id and product_name:
                stmt = select(Product.id).where(Product.product_name == product_name).limit(1)
                res = db.execute(stmt).scalar_one_or_none()
                if res is not None:
                    product_id = res
            if not product_id:
                errors.append(
                    f"Строка {i + 2}: продукт не найден (name={product_name!r}, code={product_code!r}, id={product_id_str!r})"
                )
                skipped += 1
                continue

            # Статус
            if status_str in ("FINISHED", "SEMI_FINISHED"):
                product_status = ProductStatus.FINISHED if status_str == "FINISHED" else ProductStatus.SEMI_FINISHED
            else:
                product_status = ProductStatus.FINISHED
            reserved_val = reserved_val if reserved_val is not None else 0.0

            # Единица из продукта
            prod = db.get(Product, product_id)
            unit = prod.unit_of_measure if prod else "kg"

            existing = db.execute(
                select(InventoryBalance).where(
                    InventoryBalance.product_id == product_id,
                    InventoryBalance.location == location,
                    InventoryBalance.product_status == product_status,
                )
            ).scalar_one_or_none()

            if existing:
                existing.quantity = qty_val
                existing.reserved_quantity = reserved_val
                existing.unit = unit
                updated += 1
            else:
                inv = InventoryBalance(
                    product_id=product_id,
                    location=location,
                    quantity=qty_val,
                    unit=unit,
                    product_status=product_status,
                    reserved_quantity=reserved_val,
                )
                db.add(inv)
                created += 1

        if errors:
            for e in errors:
                print(e)
        if args.dry_run:
            print(f"[dry-run] Будет создано: {created}, обновлено: {updated}, пропущено: {skipped}")
            sys.exit(0)

        db.commit()
        print(f"Остатки загружены: создано {created}, обновлено {updated}, пропущено: {skipped}.")
        if skipped > 0:
            print(
                "Пропущенные строки — продукт не найден в БД (нет ни по UUID, ни по коду). "
                "Это нормально, если CSV содержит больше продуктов, чем создано в prepare_test_env. "
                "Чтобы загружать только существующие продукты, используйте export_products_for_inventory после prepare_test_env, заполните количество и загрузите получившийся CSV."
            )
    except Exception as e:
        db.rollback()
        print(f"Ошибка: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
