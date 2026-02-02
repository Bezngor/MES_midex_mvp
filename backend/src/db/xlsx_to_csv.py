"""
Конвертация dataset_routes.xlsx, product_routing_rules.xlsx и dataset_bom.xlsx в CSV (разделитель ;, UTF-8).

Используется как единственный источник тестовых данных по маршрутам, правилам и BOM.
Пустые строки и строки без product_code/work_center_name пропускаются (маршруты/правила).
Запуск из корня репозитория:
  python -m backend.src.db.xlsx_to_csv
  python -m backend.src.db.xlsx_to_csv --routes ... --rules ... --bom ...
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

DEFAULT_ROUTES_XLSX = repo_root / ".cursor" / "_olds" / "info" / "dataset_routes.xlsx"
DEFAULT_RULES_XLSX = repo_root / ".cursor" / "_olds" / "info" / "product_routing_rules.xlsx"
DEFAULT_BOM_XLSX = repo_root / ".cursor" / "_olds" / "info" / "dataset_bom.xlsx"
DEFAULT_ROUTES_CSV = repo_root / ".cursor" / "_olds" / "info" / "dataset_routes.csv"
DEFAULT_RULES_CSV = repo_root / ".cursor" / "_olds" / "info" / "product_routing_rules.csv"
DEFAULT_BOM_CSV = repo_root / ".cursor" / "_olds" / "info" / "dataset_bom.csv"
DEFAULT_INVENTORY_XLSX = repo_root / ".cursor" / "_olds" / "info" / "inventory.xlsx"
DEFAULT_INVENTORY_CSV = repo_root / ".cursor" / "_olds" / "info" / "inventory.csv"


def _norm(s) -> str:
    if s is None:
        return ""
    return str(s).strip()


def _sheet_to_rows(path: Path) -> list[dict]:
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    rows = []
    headers = None
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        row = [None if c is None else str(c).strip() for c in row]
        if i == 0:
            headers = [h or f"_col{j}" for j, h in enumerate(row)]
            continue
        if not any(row):
            continue
        d = dict(zip(headers, row))
        d = {_norm(k): _norm(v) for k, v in d.items()}
        rows.append(d)
    wb.close()
    return rows


def _routes_headers() -> list[str]:
    return [
        "product_code", "route_key", "operation_sequence", "operation_name", "work_center_name",
        "norming_type", "capacity_pcs_per_shift", "capacity_pcs_per_shift_per_person", "shift_minutes",
        "marking_type", "crew_size", "min_crew_to_operate", "crew_productivity_rule", "crew_notes",
        "estimated_duration_minutes",
    ]


def _rules_headers() -> list[str]:
    return ["product_code", "work_center_name", "priority_order", "min_quantity", "max_quantity"]


def _get_val(row: dict, candidates: list[str]) -> str:
    row_lower = {k.lower().strip(): v for k, v in row.items()}
    for c in candidates:
        v = row.get(c)
        if v is not None and _norm(str(v)):
            return _norm(str(v))
        for k, v in row_lower.items():
            if _norm(c).lower() == k and v is not None and _norm(str(v)):
                return _norm(str(v))
    return ""


def _map_routes_row(row: dict) -> dict:
    """Маппинг из xlsx (могут быть другие имена колонок) в стандартные имена."""
    key_map = {
        "product_code": ["product_code", "Код продукции", "product code"],
        "route_key": ["route_key", "route_variant", "маршрут", "вариант"],
        "operation_sequence": ["operation_sequence", "№ операции", "operation_sequence"],
        "operation_name": ["operation_name", "Наименование операции", "operation_name"],
        "work_center_name": ["work_center_name", "РЦ", "Рабочий центр", "work_center_name"],
        "norming_type": ["norming_type"],
        "capacity_pcs_per_shift": ["capacity_pcs_per_shift"],
        "capacity_pcs_per_shift_per_person": ["capacity_pcs_per_shift_per_person"],
        "shift_minutes": ["shift_minutes"],
        "marking_type": ["marking_type"],
        "crew_size": ["crew_size"],
        "min_crew_to_operate": ["min_crew_to_operate"],
        "crew_productivity_rule": ["crew_productivity_rule"],
        "crew_notes": ["crew_notes"],
        "estimated_duration_minutes": ["estimated_duration_minutes"],
    }
    return {std_name: _get_val(row, candidates) for std_name, candidates in key_map.items()}


def _map_rules_row(row: dict) -> dict:
    key_map = {
        "product_code": ["product_code", "Код продукции", "product code"],
        "work_center_name": ["work_center_name", "РЦ", "Рабочий центр"],
        "priority_order": ["priority_order", "Приоритет", "priority_order"],
        "min_quantity": ["min_quantity", "Мин. кол-во", "min_quantity"],
        "max_quantity": ["max_quantity", "Макс. кол-во", "max_quantity"],
    }
    return {std_name: _get_val(row, candidates) for std_name, candidates in key_map.items()}


def _inventory_headers() -> list[str]:
    return ["product_code", "location", "quantity", "product_status", "reserved_quantity"]


def _map_inventory_row(row: dict) -> dict:
    """Маппинг из xlsx в колонки для загрузки остатков."""
    product_code = _get_val_any_key(
        row, "product_code", "Код", "product code", "код продукта", "product_code"
    )
    location = _get_val_any_key(
        row, "location", "Локация", "локация", "Location"
    )
    quantity = _get_val_any_key(
        row, "quantity", "Количество", "количество", "Quantity", "qty"
    )
    product_status = _get_val_any_key(
        row, "product_status", "Статус", "статус", "product status", "ProductStatus"
    )
    reserved = _get_val_any_key(
        row, "reserved_quantity", "reserved", "Зарезервировано", "зарезервировано"
    )
    return {
        "product_code": product_code,
        "location": location,
        "quantity": quantity or "0",
        "product_status": product_status or "FINISHED",
        "reserved_quantity": reserved or "0",
    }


def convert_inventory(xlsx_path: Path, csv_path: Path) -> int:
    """Конвертирует xlsx с остатками в CSV (product_code;location;quantity;product_status;reserved_quantity)."""
    rows = _sheet_to_rows(xlsx_path)
    out_rows = []
    for row in rows:
        mapped = _map_inventory_row(row)
        if not mapped.get("product_code") and not mapped.get("location"):
            continue
        if not mapped.get("location") or not mapped.get("quantity"):
            continue
        out_rows.append(mapped)
    headers = _inventory_headers()
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in out_rows:
            w.writerow({h: r.get(h, "") for h in headers})
    return len(out_rows)


def _bom_headers() -> list[str]:
    return ["Номенклатура", "_Наименование", "Доля", "Категория"]


def _get_val_any_key(row: dict, *candidates: str) -> str:
    """Возвращает значение по первому совпадению ключа (без учёта регистра)."""
    row_norm = {k.strip().lower(): (k, v) for k, v in row.items()}
    for c in candidates:
        c_lower = c.strip().lower()
        for k, (orig_k, v) in row_norm.items():
            if k == c_lower and v is not None and _norm(str(v)):
                return _norm(str(v))
        if c in row and row[c] is not None and _norm(str(row[c])):
            return _norm(str(row[c]))
    return ""


def _map_bom_row(row: dict) -> dict:
    """Маппинг из xlsx в колонки, ожидаемые load_bom_csv: Номенклатура, _Наименование, Доля, Категория."""
    # Поддержка разных имён колонок в Excel (в т.ч. с BOM/пробелами)
    nomenclature = _get_val_any_key(
        row, "Номенклатура", "Nomenclature", "Компонент", "Child", "Код", "Номенклатура"
    )
    name_parent = _get_val_any_key(
        row, "_Наименование", "Наименование", "Parent", "Родитель", "Продукт", "_Наименование"
    )
    share = row.get("Доля")
    if share is None:
        for k, v in row.items():
            if (k or "").strip().lower() in ("доля", "quantity", "количество", "share", "qty"):
                share = v
                break
    if share is None and "_col2" in row:
        share = row.get("_col2")
    if share is not None:
        share = str(share).strip().replace(",", ".")
    else:
        share = ""
    category = _get_val_any_key(
        row, "Категория", "Category", "Тип", "Category", "Категория"
    )
    if not category and "_col3" in row:
        category = _norm(str(row.get("_col3", "")))
    if not nomenclature and "_col0" in row:
        nomenclature = _norm(str(row.get("_col0", "")))
    if not name_parent and "_col1" in row:
        name_parent = _norm(str(row.get("_col1", "")))
    return {
        "Номенклатура": nomenclature,
        "_Наименование": name_parent,
        "Доля": share or "0",
        "Категория": category,
    }


def convert_bom(xlsx_path: Path, csv_path: Path) -> int:
    """Конвертирует dataset_bom.xlsx в CSV (Номенклатура;_Наименование;Доля;Категория). Строки без родителя/компонента пропускаются."""
    rows = _sheet_to_rows(xlsx_path)
    out_rows = []
    for row in rows:
        mapped = _map_bom_row(row)
        if not mapped.get("Номенклатура") and not mapped.get("_Наименование"):
            continue
        # Пропускаем строки, где в Номенклатуре похоже на UUID (ошибка конвертации/источника)
        nom = mapped.get("Номенклатура", "")
        if len(nom) == 36 and nom.count("-") == 4 and all(c in "0123456789abcdef-" for c in nom.lower()):
            continue
        out_rows.append(mapped)
    headers = _bom_headers()
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in out_rows:
            w.writerow({h: r.get(h, "") for h in headers})
    return len(out_rows)


# Коды ГП с неуникальным кодом (один продукт — несколько кодов в 1С): исключаем из маршрутов/правил.
# Удалены из тестовых датасетов; при конвертации xlsx→CSV строки с этими кодами не попадают в CSV.
EXCLUDED_PRODUCT_CODES = {
    "00-001001", "00-001663",  # GECO Гель дезинфицирующий, 100 мл, Лам, Винт
    "00-000933", "00-000969",  # GECO Крем регенерирующий СП, 100 мл, Лам, Винт
    "00-001802", "00-000781",  # GECO Паста для очистки СП д40, 200 мл, Экст, ФТ
}


def convert_routes(xlsx_path: Path, csv_path: Path) -> int:
    rows = _sheet_to_rows(xlsx_path)
    out_rows = []
    for row in rows:
        mapped = _map_routes_row(row)
        if not mapped.get("product_code") or not mapped.get("work_center_name"):
            continue
        if "route_key" not in mapped or not mapped["route_key"]:
            mapped["route_key"] = ""
        out_rows.append(mapped)
    out_rows = [r for r in out_rows if _norm(r.get("product_code", "")) not in EXCLUDED_PRODUCT_CODES]
    headers = _routes_headers()
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in out_rows:
            w.writerow({h: r.get(h, "") for h in headers})
    return len(out_rows)


def convert_rules(xlsx_path: Path, csv_path: Path) -> int:
    rows = _sheet_to_rows(xlsx_path)
    out_rows = []
    for row in rows:
        mapped = _map_rules_row(row)
        if not mapped.get("product_code") or not mapped.get("work_center_name"):
            continue
        if _norm(mapped.get("product_code", "")) in EXCLUDED_PRODUCT_CODES:
            continue
        out_rows.append(mapped)
    headers = _rules_headers()
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in out_rows:
            w.writerow({h: r.get(h, "") for h in headers})
    return len(out_rows)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser(description="Конвертация xlsx маршрутов, правил и BOM в CSV")
    p.add_argument("--routes", type=Path, default=DEFAULT_ROUTES_XLSX, help="dataset_routes.xlsx")
    p.add_argument("--rules", type=Path, default=DEFAULT_RULES_XLSX, help="product_routing_rules.xlsx")
    p.add_argument("--bom", type=Path, default=DEFAULT_BOM_XLSX, help="dataset_bom.xlsx")
    p.add_argument("--inventory", type=Path, default=None, help="inventory.xlsx (остатки для загрузки)")
    p.add_argument("--out-routes", type=Path, default=DEFAULT_ROUTES_CSV, help="Куда записать dataset_routes.csv")
    p.add_argument("--out-rules", type=Path, default=DEFAULT_RULES_CSV, help="Куда записать product_routing_rules.csv")
    p.add_argument("--out-bom", type=Path, default=DEFAULT_BOM_CSV, help="Куда записать dataset_bom.csv")
    p.add_argument("--out-inventory", type=Path, default=DEFAULT_INVENTORY_CSV, help="Куда записать inventory.csv")
    args = p.parse_args()
    if not args.routes.exists():
        print(f"Ошибка: не найден {args.routes}")
        sys.exit(1)
    if not args.rules.exists():
        print(f"Ошибка: не найден {args.rules}")
        sys.exit(1)
    n_routes = convert_routes(args.routes, args.out_routes)
    n_rules = convert_rules(args.rules, args.out_rules)
    print(f"Маршрутов (строк): {n_routes} -> {args.out_routes}")
    print(f"Правил (строк): {n_rules} -> {args.out_rules}")
    if args.bom.exists():
        n_bom = convert_bom(args.bom, args.out_bom)
        print(f"BOM (строк): {n_bom} -> {args.out_bom}")
    else:
        print(f"BOM xlsx не найден ({args.bom}), пропуск.")
    if args.inventory and args.inventory.exists():
        n_inv = convert_inventory(args.inventory, args.out_inventory)
        print(f"Остатки (строк): {n_inv} -> {args.out_inventory}")
    elif args.inventory:
        print(f"Файл остатков не найден ({args.inventory}), пропуск.")


if __name__ == "__main__":
    main()
