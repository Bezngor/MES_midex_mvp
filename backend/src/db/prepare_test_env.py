"""
Единый скрипт подготовки тестового окружения MES.

Тестовые данные по маршрутам и правилам выбора РЦ берутся ТОЛЬКО из файлов:
  dataset_routes.xlsx / dataset_routes.csv  и  product_routing_rules.xlsx / product_routing_rules.csv.

Выполняет по порядку:
  1. Загрузка датасета (заказы + BOM) — load_dataset_from_csv
  2. Посев только рабочих центров — seed_work_centers (маршруты НЕ создаются)
  3. Конвертация xlsx → CSV (если есть .xlsx), затем загрузка маршрутов и правил из CSV — load_routes_from_csv

Других источников маршрутов/правил нет (seed_routes и backfill удалены).

После запуска нужно перезапустить backend (uvicorn или контейнер) и обновить страницу «Расписание».

Запуск из корня репозитория (с активированным venv):
  python -m backend.src.db.prepare_test_env

Временный скрипт для тестирования. После завершения тестов можно удалить или архивировать.
"""

from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Пути по умолчанию
DEFAULT_ORDERS = repo_root / ".cursor" / "_olds" / "info" / "dataset_customer_orders.csv"
DEFAULT_BOM = repo_root / ".cursor" / "_olds" / "info" / "dataset_bom.csv"
DEFAULT_BOM_XLSX = repo_root / ".cursor" / "_olds" / "info" / "dataset_bom.xlsx"
DEFAULT_ROUTES_XLSX = repo_root / ".cursor" / "_olds" / "info" / "dataset_routes.xlsx"
DEFAULT_RULES_XLSX = repo_root / ".cursor" / "_olds" / "info" / "product_routing_rules.xlsx"
DEFAULT_ROUTES_CSV = repo_root / ".cursor" / "_olds" / "info" / "dataset_routes.csv"
DEFAULT_RULES_CSV = repo_root / ".cursor" / "_olds" / "info" / "product_routing_rules.csv"


def main() -> None:
    from backend.src.db.load_dataset_from_csv import run as run_load_dataset
    from backend.src.db.seed_work_centers_and_routes import seed_work_centers
    from backend.src.db.load_routes_from_csv import load_routes_and_rules
    from backend.src.db.session import SessionLocal

    orders_path = DEFAULT_ORDERS
    bom_path = DEFAULT_BOM
    routes_xlsx = DEFAULT_ROUTES_XLSX
    rules_xlsx = DEFAULT_RULES_XLSX
    routes_csv = DEFAULT_ROUTES_CSV
    rules_csv = DEFAULT_RULES_CSV

    if not orders_path.exists():
        print(f"Ошибка: не найден файл заказов: {orders_path}")
        sys.exit(1)
    if not bom_path.exists():
        print(f"Ошибка: не найден файл BOM: {bom_path}")
        sys.exit(1)

    # Конвертация BOM из xlsx в CSV (если есть xlsx), чтобы использовать актуальные наименования
    if DEFAULT_BOM_XLSX.exists():
        try:
            from backend.src.db.xlsx_to_csv import convert_bom
            print("=== 0. Конвертация BOM xlsx → CSV ===")
            n_bom = convert_bom(DEFAULT_BOM_XLSX, bom_path)
            print(f"BOM (строк): {n_bom} -> {bom_path}")
        except Exception as e:
            print(f"Предупреждение: конвертация BOM не выполнена: {e}. Используется существующий CSV.")

    print("\n=== 1. Загрузка датасета (заказы + BOM) ===")
    run_load_dataset(orders_path, bom_path, dry_run=False)

    print("\n=== 2. Посев рабочих центров (без маршрутов) ===")
    db = SessionLocal()
    try:
        seed_work_centers(db)
    finally:
        db.close()

    # Шаг 3: xlsx → CSV (если есть xlsx и установлен openpyxl), иначе — используем существующие CSV
    if routes_xlsx.exists() and rules_xlsx.exists():
        try:
            from backend.src.db.xlsx_to_csv import convert_routes, convert_rules
            print("\n=== 3. Конвертация xlsx → CSV ===")
            n_routes = convert_routes(routes_xlsx, routes_csv)
            n_rules = convert_rules(rules_xlsx, rules_csv)
            print(f"Маршрутов (строк): {n_routes}, правил: {n_rules}.")
        except ModuleNotFoundError as e:
            if "openpyxl" in str(e):
                print("\n(Модуль openpyxl не установлен — конвертация xlsx пропущена.)")
                if not routes_csv.exists() or not rules_csv.exists():
                    print("Ошибка: CSV маршрутов/правил нет. Установите openpyxl: pip install openpyxl")
                    sys.exit(1)
            else:
                raise
    else:
        print("\n(Файлы .xlsx маршрутов/правил не найдены, используем существующие CSV.)")

    print("\n=== 4. Загрузка маршрутов и правил из CSV ===")
    if not routes_csv.exists() or not rules_csv.exists():
        print(f"Ошибка: CSV не найдены ({routes_csv}, {rules_csv}). Сначала выполните конвертацию xlsx или положите CSV в .cursor/_olds/info/.")
        sys.exit(1)
    db = SessionLocal()
    try:
        routes_updated, rules_count = load_routes_and_rules(db, routes_csv, rules_csv)
        print(f"Маршруты обновлены: {routes_updated}. Правил загружено: {rules_count}.")
    finally:
        db.close()

    print("\n" + "=" * 60)
    print("Готово. Тестовое окружение подготовлено.")
    print("")
    print("Далее ОБЯЗАТЕЛЬНО:")
    print("  1. Перезапустите backend (остановите uvicorn/Docker и запустите снова).")
    print("  2. Обновите страницу «Расписание» в браузере (F5) и нажмите «Проверить снова».")
    print("=" * 60)


if __name__ == "__main__":
    main()
