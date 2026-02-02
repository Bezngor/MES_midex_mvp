"""
Загрузка маршрутов и правил выбора РЦ из CSV.

- Читает dataset_routes.csv (разделитель ;, UTF-8): product_code, operation_sequence,
  operation_name, work_center_name, norming_type, capacity_*, estimated_duration_minutes и др.
- Читает product_routing_rules.csv: product_code, work_center_name, priority_order,
  min_quantity, max_quantity.
- Все РЦ из CSV должны существовать в БД (запустите seed_work_centers_and_routes до импорта).
- Обновляет/создаёт manufacturing_routes и route_operations по product_code.
- Очищает product_routing_rules и загружает строки из второго файла.

Запуск из корня репозитория (после load_dataset_from_csv и seed_work_centers_and_routes):
  python -m backend.src.db.load_routes_from_csv
  python -m backend.src.db.load_routes_from_csv --routes path/to/routes.csv --rules path/to/rules.csv
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from backend.src.db.session import SessionLocal
from backend.core.models.product import Product
from backend.core.models.work_center import WorkCenter
from backend.core.models.manufacturing_route import ManufacturingRoute
from backend.core.models.route_operation import RouteOperation
from backend.core.models.product_routing_rule import ProductRoutingRule


DEFAULT_ROUTES_CSV = repo_root / ".cursor" / "_olds" / "info" / "dataset_routes.csv"
DEFAULT_RULES_CSV = repo_root / ".cursor" / "_olds" / "info" / "product_routing_rules.csv"


def _norm(s: str | None) -> str:
    return (s or "").strip()


def _int_or_none(s: str | None):
    if s is None:
        return None
    s = _norm(s)
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def _float_or_none(s: str | None):
    if s is None:
        return None
    s = _norm(s)
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _estimate_duration_minutes(row: dict) -> int:
    """Вычисляет estimated_duration_minutes из норм (номинал 1000 шт) или берёт из CSV."""
    est = _int_or_none(row.get("estimated_duration_minutes"))
    if est is not None and est > 0:
        return est
    cap_shift = _float_or_none(row.get("capacity_pcs_per_shift"))
    cap_person = _float_or_none(row.get("capacity_pcs_per_shift_per_person"))
    shift_min = _int_or_none(row.get("shift_minutes")) or 720
    nominal_qty = 1000
    if cap_shift and cap_shift > 0:
        return max(1, int((nominal_qty / cap_shift) * shift_min))
    if cap_person and cap_person > 0:
        return max(1, int((nominal_qty / cap_person) * shift_min))
    return 60


def load_routes_csv(path: Path) -> list[dict]:
    """Читает dataset_routes.csv; возвращает список строк (dict), ключи нормализованы, пустые строки пропущены.
    Опциональная колонка route_key — вариант маршрута (несколько маршрутов на один продукт)."""
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for raw in reader:
            row = {_norm(k): _norm(v) for k, v in raw.items()}
            if not row.get("product_code") or not row.get("work_center_name"):
                continue
            if "route_key" not in row or row.get("route_key") is None:
                row["route_key"] = ""
            else:
                row["route_key"] = _norm(row.get("route_key", ""))
            rows.append(row)
    return rows


def load_rules_csv(path: Path) -> list[dict]:
    """Читает product_routing_rules.csv."""
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for raw in reader:
            row = {_norm(k): _norm(v) for k, v in raw.items()}
            if not row.get("product_code") or not row.get("work_center_name"):
                continue
            rows.append(row)
    return rows


def load_routes_and_rules(
    db: Session,
    routes_path: Path = DEFAULT_ROUTES_CSV,
    rules_path: Path = DEFAULT_RULES_CSV,
) -> tuple[int, int]:
    """
    Загружает маршруты из routes_path и правила из rules_path.
    Возвращает (количество обновлённых маршрутов, количество правил).
    """
    if not routes_path.exists():
        raise FileNotFoundError(f"Файл маршрутов не найден: {routes_path}")
    if not rules_path.exists():
        raise FileNotFoundError(f"Файл правил не найден: {rules_path}")

    route_rows = load_routes_csv(routes_path)
    rules_rows = load_rules_csv(rules_path)

    wc_by_name = {r.name: r.id for r in db.execute(select(WorkCenter)).scalars().all()}
    # Нормализованный код -> список продуктов (один код может быть у нескольких записей из-за пробелов в БД)
    products_by_norm_code: dict[str, list] = defaultdict(list)
    for p in db.execute(select(Product)).scalars().all():
        products_by_norm_code[_norm(p.product_code)].append(p)

    missing_wc = set()
    for row in route_rows:
        wc = _norm(row.get("work_center_name"))
        if wc and wc not in wc_by_name:
            missing_wc.add(wc)
    for row in rules_rows:
        wc = _norm(row.get("work_center_name"))
        if wc and wc not in wc_by_name:
            missing_wc.add(wc)
    if missing_wc:
        raise ValueError(
            f"В БД нет следующих рабочих центров (запустите seed_work_centers_and_routes): {sorted(missing_wc)}"
        )

    # Один маршрут на продукт: берём только строки с пустым route_key (типовой вариант).
    # В маршрутах указывают основной РЦ; правила выбора РЦ задают распределение по количеству и т.д.
    by_product: dict[str, list[dict]] = defaultdict(list)
    for row in route_rows:
        code = _norm(row["product_code"])
        key = _norm(row.get("route_key") or "")
        if key:
            continue
        by_product[code].append(row)

    routes_updated = 0
    skipped_products: list[str] = []
    now = datetime.now(timezone.utc)

    # Сначала удалить все маршруты по продуктам, которые есть в CSV
    products_to_clear: set[str] = set()
    for product_code in by_product:
        products_to_clear.add(product_code)
    for product_code in products_to_clear:
        products = list(products_by_norm_code.get(product_code, []))
        for norm_code, plist in products_by_norm_code.items():
            if norm_code != product_code and norm_code.startswith(product_code + "_"):
                products.extend(plist)
        for product in products:
            for existing_route in db.execute(
                select(ManufacturingRoute).where(ManufacturingRoute.product_id == str(product.id))
            ).scalars().all():
                db.delete(existing_route)
    db.flush()

    for product_code, rows in by_product.items():
        products = list(products_by_norm_code.get(product_code, []))
        for norm_code, plist in products_by_norm_code.items():
            if norm_code != product_code and norm_code.startswith(product_code + "_"):
                products.extend(plist)
        if not products:
            skipped_products.append(product_code)
            continue
        rows_sorted = sorted(rows, key=lambda r: (_int_or_none(r.get("operation_sequence")) or 0, r))
        for product in products:
            route = ManufacturingRoute(
                product_id=str(product.id),
                route_name=f"{product.product_name[:80]} — маршрут",
                description="Маршрут из CSV",
                created_at=now,
                updated_at=now,
            )
            db.add(route)
            db.flush()
            for r in rows_sorted:
                wc_name = _norm(r.get("work_center_name"))
                wc_id = wc_by_name.get(wc_name)
                if not wc_id:
                    continue
                seq = _int_or_none(r.get("operation_sequence")) or 0
                op_name = _norm(r.get("operation_name")) or "Операция"
                duration = _estimate_duration_minutes(r)
                op = RouteOperation(
                    route_id=route.id,
                    operation_sequence=seq,
                    operation_name=op_name,
                    work_center_id=wc_id,
                    estimated_duration_minutes=duration,
                )
                db.add(op)
            routes_updated += 1

    db.commit()

    db.execute(delete(ProductRoutingRule))
    db.commit()

    rules_count = 0
    for row in rules_rows:
        product_code = _norm(row.get("product_code"))
        wc_name = _norm(row.get("work_center_name"))
        priority = _int_or_none(row.get("priority_order")) or 1
        min_q = _int_or_none(row.get("min_quantity"))
        max_q = _int_or_none(row.get("max_quantity"))
        wc_id = wc_by_name.get(wc_name)
        if not wc_id:
            continue
        rule = ProductRoutingRule(
            product_code=product_code,
            work_center_id=wc_id,
            priority_order=priority,
            min_quantity=min_q,
            max_quantity=max_q,
        )
        db.add(rule)
        rules_count += 1
    db.commit()

    if skipped_products:
        print(f"  Пропущены продукты (не найдены в БД): {', '.join(sorted(skipped_products))}")
    return routes_updated, rules_count


def main() -> None:
    import argparse
    p = argparse.ArgumentParser(description="Загрузка маршрутов и правил выбора РЦ из CSV")
    p.add_argument("--routes", type=Path, default=DEFAULT_ROUTES_CSV, help="Путь к dataset_routes.csv")
    p.add_argument("--rules", type=Path, default=DEFAULT_RULES_CSV, help="Путь к product_routing_rules.csv")
    args = p.parse_args()

    db = SessionLocal()
    try:
        routes_updated, rules_count = load_routes_and_rules(db, args.routes, args.rules)
        print(f"Маршруты обновлены: {routes_updated}. Правил выбора РЦ загружено: {rules_count}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
