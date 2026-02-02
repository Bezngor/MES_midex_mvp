"""
Загрузка тестового датасета из CSV: заказы покупателей + BOM.

- Читает dataset_customer_orders.csv и dataset_bom.csv (разделитель ;, UTF-8).
- Оставляет только ГП, задействованные и в заказах, и в BOM (по наименованию).
- Загружает только продукты и BOM, реально используемые в этих заказах.
- Очищает таблицы: manufacturing_orders, production_tasks, batches, bill_of_materials,
  inventory_balances, work_center_capacities, manufacturing_routes, route_operations,
  products (и зависимые), затем создаёт продукты, BOM и заказы со статусом SHIP.

Запуск из корня репозитория:
  python -m backend.src.db.load_dataset_from_csv
  python -m backend.src.db.load_dataset_from_csv --orders path/to/orders.csv --bom path/to/bom.csv
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal

# Корень репозитория в PYTHONPATH
repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.src.db.session import engine, SessionLocal, DATABASE_URL
from backend.core.models.product import Product
from backend.core.models.bill_of_material import BillOfMaterial
from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.enums import (
    ProductType,
    OrderStatus,
    OrderPriority,
)

# Русские названия месяцев для парсинга даты "16 января 2026 г."
RU_MONTH = {
    "января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6,
    "июля": 7, "августа": 8, "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12,
}

# Порядок очистки таблиц (соблюдение FK)
TABLES_CLEAR_ORDER = [
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


def parse_russian_date(s: str) -> datetime | None:
    """Парсит дату вида '16 января 2026 г.' в datetime (UTC)."""
    s = (s or "").strip()
    # "16 января 2026 г." или "26 декабря 2025 г."
    m = re.match(r"(\d{1,2})\s+(\S+)\s+(\d{4})\s*", s)
    if not m:
        return None
    day, month_name, year = int(m.group(1)), m.group(2).strip().lower(), int(m.group(3))
    month = RU_MONTH.get(month_name)
    if month is None:
        return None
    try:
        return datetime(year, month, day, tzinfo=timezone.utc)
    except ValueError:
        return None


def normalize_source_status(status: str) -> str:
    """Нормализует статус заказа из 1С: Отгрузить, Образец, В работе."""
    s = (status or "").strip()
    if not s:
        return "Отгрузить"
    lower = s.lower()
    if "отгрузить" in lower:
        return "Отгрузить"
    if "образец" in lower:
        return "Образец"
    if "работе" in lower or "в работе" in lower:
        return "В работе"
    return s


def status_to_priority(status: str) -> str:
    """При загрузке: Отгрузить/Образец -> HIGH, В работе -> NORMAL (для MRP приоритет считается по source_status и дате)."""
    s = (status or "").strip().lower()
    if "работе" in s or "в работе" in s:
        return OrderPriority.NORMAL.value
    if "отгрузить" in s or "образец" in s:
        return OrderPriority.HIGH.value
    return OrderPriority.HIGH.value


def slug_code(name: str, prefix: str = "") -> str:
    """Уникальный код из наименования для продукта (латиница, цифры, подчёркивание)."""
    s = name.strip()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s-]+", "_", s).strip("_")[:80]
    s = s or "unnamed"
    return (prefix + "_" + s) if prefix else s


def _normalize_row_keys(row: dict) -> dict:
    """Убирает BOM и пробелы из ключей (utf-8-sig даёт \\ufeff в первом ключе)."""
    return {k.strip().lstrip("\ufeff"): v for k, v in row.items()}


def load_orders_csv(path: Path) -> list[dict]:
    """Загружает заказы: Наименование;Код продукции;Статус заказа;Дата отгрузки;Номер заказа;Покупатель;Количество."""
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            row = _normalize_row_keys(row)
            row["quantity"] = _parse_decimal(row.get("Количество", "0"))
            row["due_date"] = parse_russian_date(row.get("Дата отгрузки", ""))
            raw_status = (row.get("Статус заказа") or "").strip()
            row["source_status"] = normalize_source_status(raw_status)
            row["priority"] = status_to_priority(raw_status)
            rows.append(row)
    return rows


def load_bom_csv(path: Path) -> list[dict]:
    """Загружает BOM: Номенклатура;_Наименование;Доля;Категория."""
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            row = _normalize_row_keys(row)
            q = _parse_decimal(row.get("Доля", "0"))
            row["quantity"] = q
            rows.append(row)
    return rows


def _parse_decimal(s: str) -> Decimal:
    s = (s or "0").strip().replace(",", ".")
    try:
        return Decimal(s)
    except Exception:
        return Decimal("0")


def build_fg_set_from_orders(orders: list[dict]) -> set[tuple[str, str]]:
    """Уникальные пары (Код продукции; Наименование) из заказов."""
    out = set()
    for r in orders:
        code = (r.get("Код продукции") or "").strip()
        name = (r.get("Наименование") or "").strip()
        if code and name:
            out.add((code, name))
    return out


def build_fg_names_in_bom(bom_rows: list[dict]) -> set[str]:
    """Наименования ГП из BOM (родитель при Категория=Продукция)."""
    return {
        (r.get("_Наименование") or "").strip()
        for r in bom_rows
        if (r.get("Категория") or "").strip() == "Продукция"
    }


def intersect_fg(orders_fg: set[tuple[str, str]], bom_fg_names: set[str]) -> set[tuple[str, str]]:
    """ГП только те, что есть и в заказах, и в BOM (по наименованию)."""
    return {(code, name) for code, name in orders_fg if name in bom_fg_names}


def exclude_duplicate_code_names(fg_kept: set[tuple[str, str]]) -> tuple[set[tuple[str, str]], list[tuple[str, list[str]]]]:
    """
    Убирает из fg_kept наименования, у которых больше одного кода (ошибка 1С: один продукт — один код).
    Возвращает (очищенный fg_kept, список исключённых: [(наименование, [коды])]).
    """
    from collections import defaultdict
    name_to_codes: dict[str, set[str]] = defaultdict(set)
    for code, name in fg_kept:
        name_to_codes[name].add(code)
    duplicates = [(name, sorted(codes)) for name, codes in name_to_codes.items() if len(codes) > 1]
    if not duplicates:
        return fg_kept, []
    excluded_names = {name for name, _ in duplicates}
    cleaned = {(code, name) for code, name in fg_kept if name not in excluded_names}
    return cleaned, duplicates


def filter_orders_by_fg(orders: list[dict], fg_kept: set[tuple[str, str]]) -> list[dict]:
    """Оставляем только заказы по ГП из fg_kept (по наименованию)."""
    names_kept = {name for _, name in fg_kept}
    return [r for r in orders if (r.get("Наименование") or "").strip() in names_kept]


def _norm(s: str) -> str:
    return (s or "").strip()


def _q(r: dict) -> Decimal:
    return r.get("quantity", Decimal("0")) if isinstance(r.get("quantity"), Decimal) else _parse_decimal(r.get("Доля", "0"))


def build_product_sets_and_bom(
    fg_kept: set[tuple[str, str]],
    bom_rows: list[dict],
) -> tuple[dict[str, tuple[str, str]], list[tuple[str, str, Decimal, str]]]:
    """
    Строит:
    - product_by_name: имя -> (product_code, product_type_str)
    - bom_tuples: (parent_name, child_name, quantity, unit)
    Только то, что задействовано от ГП вниз (ГП->Масса/Упаковка, Масса->Сырьё).
    """
    fg_names = {name for _, name in fg_kept}

    bom_produkciya = [r for r in bom_rows if (r.get("Категория") or "").strip() == "Продукция"]
    bom_massa = [r for r in bom_rows if (r.get("Категория") or "").strip() == "Масса"]

    # Родители и дети из BOM Масса (Масса -> Сырьё)
    massa_parent_names = {_norm(r.get("_Наименование")) for r in bom_massa}
    massa_rows = [(_norm(r.get("_Наименование")), _norm(r.get("Номенклатура")), _q(r)) for r in bom_massa]

    # Строки BOM Продукция только для ГП из fg_kept; дети ГП = Масса или Упаковка
    bom_fg_tuples = []
    fg_children = set()
    for r in bom_produkciya:
        parent = _norm(r.get("_Наименование"))
        child = _norm(r.get("Номенклатура"))
        if parent not in fg_names:
            continue
        q = _q(r)
        unit = "kg" if child in massa_parent_names else "pcs"
        bom_fg_tuples.append((parent, child, q, unit))
        fg_children.add(child)

    # Масса, реально используемая как компонент ГП
    mass_names_used = massa_parent_names & fg_children
    # Сырьё: дети из BOM Масса, у которых родитель в mass_names_used
    raw_names = {child for parent, child, _ in massa_rows if parent in mass_names_used}
    # Упаковка: дети ГП, не являющиеся Масса
    packaging_names = fg_children - massa_parent_names

    product_by_name = {}
    for code, name in fg_kept:
        product_by_name[name] = (code, ProductType.FINISHED_GOOD.value)
    for name in mass_names_used:
        if name not in product_by_name:
            product_by_name[name] = (slug_code(name, "BULK"), ProductType.BULK.value)
    for name in raw_names:
        if name not in product_by_name:
            product_by_name[name] = (slug_code(name, "RAW"), ProductType.RAW_MATERIAL.value)
    for name in packaging_names:
        if name not in product_by_name:
            product_by_name[name] = (slug_code(name, "PKG"), ProductType.PACKAGING.value)

    bom_tuples = []
    for parent, child, q, unit in bom_fg_tuples:
        if parent in product_by_name and child in product_by_name:
            bom_tuples.append((parent, child, q, unit))
    for parent, child, q in massa_rows:
        if parent in product_by_name and child in product_by_name:
            bom_tuples.append((parent, child, q, "kg"))

    return product_by_name, bom_tuples


def clear_tables(conn) -> None:
    for table in TABLES_CLEAR_ORDER:
        try:
            conn.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))
        except Exception as e:
            if "does not exist" in str(e).lower():
                continue
            raise


def run(
    orders_path: Path,
    bom_path: Path,
    dry_run: bool = False,
) -> None:
    orders_raw = load_orders_csv(orders_path)
    bom_raw = load_bom_csv(bom_path)

    fg_from_orders = build_fg_set_from_orders(orders_raw)
    fg_names_in_bom = build_fg_names_in_bom(bom_raw)
    fg_kept = intersect_fg(fg_from_orders, fg_names_in_bom)
    fg_kept, duplicate_code_list = exclude_duplicate_code_names(fg_kept)
    if duplicate_code_list:
        print("ВНИМАНИЕ: ГП с неуникальным кодом (ошибка 1С) исключены из загрузки:")
        for name, codes in duplicate_code_list:
            print(f"  — {name!r} (коды: {', '.join(codes)})")
        print("Такие ГП удалены из тестовых датасетов; доведите данные в 1С (один код на продукт).")
    orders = filter_orders_by_fg(orders_raw, fg_kept)

    product_by_name, bom_tuples = build_product_sets_and_bom(fg_kept, bom_raw)

    print("Orders file:", orders_path)
    print("BOM file:", bom_path)
    print("FG from orders (unique code+name):", len(fg_from_orders))
    print("FG in BOM (parent names Продукция):", len(fg_names_in_bom))
    print("FG kept (intersection):", len(fg_kept))
    in_work_count = sum(1 for r in orders if (r.get("source_status") or "").strip() == "В работе")
    print("Orders after filter:", len(orders), f"(из них «В работе»: {in_work_count})")
    print("Products to create:", len(product_by_name))
    print("BOM rows to create:", len(bom_tuples))

    if dry_run:
        print("Dry run — no DB changes.")
        return

    with engine.begin() as conn:
        clear_tables(conn)

    db: Session = SessionLocal()
    try:
        name_to_product_id = {}
        used_codes = set()
        # Создаём продукты (product_code уникален)
        for name, (code, ptype) in product_by_name.items():
            while code in used_codes:
                code = f"{code}_{len(used_codes)}"
            used_codes.add(code)
            unit = "kg" if ptype in (ProductType.BULK.value, ProductType.RAW_MATERIAL.value) else "pcs"
            kwargs = {"product_code": code, "product_name": name, "product_type": ptype, "unit_of_measure": unit}
            if ptype == ProductType.BULK.value:
                kwargs["min_batch_size_kg"] = 500
                kwargs["batch_size_step_kg"] = 1000
                kwargs["shelf_life_days"] = 7
            p = Product(**kwargs)
            db.add(p)
            db.flush()
            name_to_product_id[name] = (p.id, code)

        db.commit()

        # BOM (name_to_product_id уже заполнен id из flush выше)
        for parent_name, child_name, qty, unit in bom_tuples:
            pid_p = name_to_product_id.get(parent_name)
            pid_c = name_to_product_id.get(child_name)
            if not pid_p or not pid_c:
                continue
            bom = BillOfMaterial(
                parent_product_id=pid_p[0],
                child_product_id=pid_c[0],
                quantity=float(qty),
                unit=unit,
            )
            db.add(bom)
        db.commit()

        # Заказы (product_id — UUID продукта строкой). Номер заказа уникален.
        order_numbers_seen = set()
        for r in orders:
            name = (r.get("Наименование") or "").strip()
            qty = r.get("quantity", Decimal("0"))
            if qty is None or qty <= 0:
                continue
            pid, _ = name_to_product_id.get(name, (None, None))
            if not pid:
                continue
            due = r.get("due_date")
            if not due:
                due = datetime.now(timezone.utc)
            base = (r.get("Номер заказа") or "").strip() or "ORD"
            order_number = base
            n = 0
            while order_number in order_numbers_seen:
                n += 1
                order_number = f"{base}-{n}"
            order_numbers_seen.add(order_number)
            priority = r.get("priority") or OrderPriority.NORMAL.value
            order = ManufacturingOrder(
                order_number=order_number,
                product_id=str(pid),
                quantity=r.get("quantity", Decimal("0")),
                due_date=due,
                status=OrderStatus.SHIP,
                order_type="CUSTOMER",
                priority=priority,
                source_status=r.get("source_status"),
            )
            db.add(order)
        db.commit()
        print("Done: products, BOM, manufacturing orders (SHIP) created.")
    finally:
        db.close()


def main() -> None:
    import argparse
    default_orders = repo_root / ".cursor" / "_olds" / "info" / "dataset_customer_orders.csv"
    default_bom = repo_root / ".cursor" / "_olds" / "info" / "dataset_bom.csv"
    parser = argparse.ArgumentParser(description="Load dataset from customer orders + BOM CSV")
    parser.add_argument("--orders", type=Path, default=default_orders, help="Path to orders CSV")
    parser.add_argument("--bom", type=Path, default=default_bom, help="Path to BOM CSV")
    parser.add_argument("--dry-run", action="store_true", help="Only print stats, do not change DB")
    args = parser.parse_args()
    if not args.orders.exists():
        print("Orders file not found:", args.orders)
        sys.exit(1)
    if not args.bom.exists():
        print("BOM file not found:", args.bom)
        sys.exit(1)
    print("Database:", DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "(from env)")
    run(args.orders, args.bom, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
