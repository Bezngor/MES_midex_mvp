"""
Скрипт для добавления маршрутов и правил маршрутизации для масс (BULK продуктов).

Читает dataset_bom.csv, определяет уникальные массы, генерирует для них коды
и добавляет маршруты в dataset_routes.csv и правила в product_routing_rules.csv.

Запуск из корня репозитория:
  python -m backend.src.db.add_mass_routes
"""

from __future__ import annotations

import csv
import sys
import re
from pathlib import Path
from collections import OrderedDict

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


def slug_code(name: str, prefix: str = "") -> str:
    """Уникальный код из наименования для продукта (латиница, цифры, подчёркивание)."""
    s = name.strip()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s-]+", "_", s).strip("_")[:80]
    s = s or "unnamed"
    return (prefix + "_" + s) if prefix else s


def determine_work_center_for_mass(mass_name: str) -> tuple[str, str]:
    """
    Определяет рабочий центр для варки массы на основе её наименования.
    
    Логика распределения:
    - Миксер (WC_MIXER): жидкие массы (жидкое мыло, спреи, дезинфицирующие средства)
    - Реактор (WC_REACTOR_MAIN): вязкие массы (кремы, пасты, гели)
    
    Returns:
        (work_center_name, operation_name) - например, ("WC_MIXER", "Смешивание массы")
    """
    mass_lower = mass_name.lower()
    
    # Ключевые слова для миксера (жидкие продукты)
    mixer_keywords = [
        "жидкое мыло",
        "дезинфицирующее",
        "средство дезинфицирующее",
        "спрей",
        "репелент",
    ]
    
    # Ключевые слова для реактора (вязкие/пастообразные продукты)
    reactor_keywords = [
        "крем",
        "паста",
        "гель",
        "средство для очистки",
    ]
    
    # Проверяем ключевые слова для миксера
    for keyword in mixer_keywords:
        if keyword in mass_lower:
            return ("WC_MIXER", "Смешивание массы")
    
    # Проверяем ключевые слова для реактора
    for keyword in reactor_keywords:
        if keyword in mass_lower:
            return ("WC_REACTOR_MAIN", "Варка массы")
    
    # По умолчанию - реактор (для большинства масс)
    return ("WC_REACTOR_MAIN", "Варка массы")

DEFAULT_BOM_CSV = repo_root / ".cursor" / "_olds" / "info" / "dataset_bom.csv"
DEFAULT_ROUTES_CSV = repo_root / ".cursor" / "_olds" / "info" / "dataset_routes.csv"
DEFAULT_RULES_CSV = repo_root / ".cursor" / "_olds" / "info" / "product_routing_rules.csv"


def _norm(s: str | None) -> str:
    return (s or "").strip()


def get_unique_masses_from_bom(bom_path: Path) -> list[str]:
    """Извлекает уникальные массы из dataset_bom.csv."""
    masses = OrderedDict()
    if not bom_path.exists():
        print(f"Файл BOM не найден: {bom_path}")
        return []
    
    with open(bom_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            category = _norm(row.get("Категория", ""))
            if category == "Масса":
                mass_name = _norm(row.get("_Наименование", ""))
                if mass_name:
                    masses[mass_name] = True
    
    return sorted(masses.keys())


def get_existing_product_codes(routes_path: Path) -> set[str]:
    """Получает список существующих product_code из dataset_routes.csv."""
    codes = set()
    if not routes_path.exists():
        return codes
    
    with open(routes_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            code = _norm(row.get("product_code", ""))
            if code:
                codes.add(code)
    
    return codes


def add_mass_routes_to_csv(
    routes_path: Path,
    masses: list[str],
    existing_codes: set[str],
) -> int:
    """Добавляет маршруты для масс в dataset_routes.csv. Возвращает количество добавленных."""
    if not routes_path.exists():
        print(f"Файл маршрутов не найден: {routes_path}")
        return 0
    
    # Читаем существующие строки
    existing_rows = []
    headers = None
    with open(routes_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        headers = reader.fieldnames
        existing_rows = list(reader)
    
    if not headers:
        print("Не удалось прочитать заголовки из файла маршрутов")
        return 0
    
    # Генерируем новые строки для масс
    new_rows = []
    updated_rows = []
    added_count = 0
    updated_count = 0
    
    for mass_name in masses:
        # Генерируем код массы (BULK_наименование)
        mass_code = slug_code(mass_name, "BULK")
        
        # Определяем рабочий центр и операцию для массы
        work_center_name, operation_name = determine_work_center_for_mass(mass_name)
        
        # Проверяем, есть ли уже маршрут для этой массы
        if mass_code in existing_codes:
            # Обновляем существующий маршрут, если он не соответствует правильному рабочему центру
            for row in existing_rows:
                if _norm(row.get("product_code", "")) == mass_code:
                    old_wc = _norm(row.get("work_center_name", ""))
                    if old_wc != work_center_name:
                        # Обновляем существующую строку
                        row["work_center_name"] = work_center_name
                        row["operation_name"] = operation_name
                        duration_minutes = "180" if work_center_name == "WC_MIXER" else "240"
                        row["estimated_duration_minutes"] = duration_minutes
                        updated_rows.append(row)
                        updated_count += 1
                        print(f"  Обновлён маршрут для массы '{mass_name}' (код: {mass_code}): {old_wc} -> {work_center_name}")
                    else:
                        print(f"  Пропущена масса '{mass_name}' (код '{mass_code}' уже есть в маршрутах с правильным РЦ)")
                    break
            continue
        
        # Определяем рабочий центр и операцию для массы
        work_center_name, operation_name = determine_work_center_for_mass(mass_name)
        
        # Длительность зависит от рабочего центра
        # Реактор: 240 минут (4 часа) - типичная варка
        # Миксер: 180 минут (3 часа) - смешивание быстрее
        duration_minutes = "180" if work_center_name == "WC_MIXER" else "240"
        
        # Создаём строку маршрута
        route_row = {
            "product_code": mass_code,
            "route_key": "",
            "operation_sequence": "1",
            "operation_name": operation_name,
            "work_center_name": work_center_name,
            "norming_type": "",
            "capacity_pcs_per_shift": "",
            "capacity_pcs_per_shift_per_person": "",
            "shift_minutes": "720",
            "marking_type": "",
            "crew_size": "1",
            "min_crew_to_operate": "1",
            "crew_productivity_rule": "",
            "crew_notes": "",
            "estimated_duration_minutes": duration_minutes,
        }
        
        # Заполняем все колонки заголовков
        for h in headers:
            if h not in route_row:
                route_row[h] = ""
        
        new_rows.append(route_row)
        existing_codes.add(mass_code)
        added_count += 1
        print(f"  Добавлен маршрут для массы '{mass_name}' (код: {mass_code}) -> {work_center_name} ({operation_name})")
    
    # Записываем обратно (существующие + новые)
    if new_rows or updated_rows:
        # Обновляем существующие строки в списке
        if updated_rows:
            for updated_row in updated_rows:
                for i, existing_row in enumerate(existing_rows):
                    if _norm(existing_row.get("product_code", "")) == _norm(updated_row.get("product_code", "")):
                        existing_rows[i] = updated_row
                        break
        
        all_rows = existing_rows + new_rows
        with open(routes_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers, delimiter=";")
            writer.writeheader()
            writer.writerows(all_rows)
        if new_rows:
            print(f"  Записано {len(new_rows)} новых маршрутов в {routes_path}")
        if updated_rows:
            print(f"  Обновлено {len(updated_rows)} существующих маршрутов в {routes_path}")
    
    return added_count + updated_count


def add_mass_rules_to_csv(
    rules_path: Path,
    masses: list[str],
) -> int:
    """Добавляет правила маршрутизации для масс в product_routing_rules.csv. Возвращает количество добавленных."""
    if not rules_path.exists():
        print(f"Файл правил не найден: {rules_path}")
        return 0
    
    # Читаем существующие строки
    existing_rows = []
    headers = None
    existing_pairs = set()  # (product_code, work_center_name)
    
    with open(rules_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        headers = reader.fieldnames
        for row in reader:
            existing_rows.append(row)
            code = _norm(row.get("product_code", ""))
            wc = _norm(row.get("work_center_name", ""))
            if code and wc:
                existing_pairs.add((code, wc))
    
    if not headers:
        print("Не удалось прочитать заголовки из файла правил")
        return 0
    
    # Генерируем новые строки для масс
    new_rows = []
    added_count = 0
    
    for mass_name in masses:
        mass_code = slug_code(mass_name, "BULK")
        
        # Определяем рабочий центр для массы (та же логика, что и в маршрутах)
        work_center_name, _ = determine_work_center_for_mass(mass_name)
        
        # Проверяем, нет ли уже правила для этой массы и рабочего центра
        if (mass_code, work_center_name) in existing_pairs:
            print(f"  Пропущено правило для массы '{mass_name}' (код '{mass_code}' уже есть в правилах для {work_center_name})")
            continue
        
        # Создаём строку правила: масса -> рабочий центр (Реактор или Миксер)
        rule_row = {
            "product_code": mass_code,
            "work_center_name": work_center_name,
            "priority_order": "1",
            "min_quantity": "",
            "max_quantity": "",
        }
        
        # Заполняем все колонки заголовков
        for h in headers:
            if h not in rule_row:
                rule_row[h] = ""
        
        new_rows.append(rule_row)
        existing_pairs.add((mass_code, work_center_name))
        added_count += 1
        print(f"  Добавлено правило для массы '{mass_name}' (код: {mass_code}) -> {work_center_name}")
    
    # Записываем обратно (существующие + новые)
    if new_rows:
        all_rows = existing_rows + new_rows
        with open(rules_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers, delimiter=";")
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"  Записано {len(new_rows)} новых правил в {rules_path}")
    
    return added_count


def main() -> None:
    """Основная функция."""
    print("=== Добавление маршрутов и правил для масс ===\n")
    
    # Шаг 1: Извлекаем уникальные массы из BOM
    print("1. Извлечение масс из dataset_bom.csv...")
    masses = get_unique_masses_from_bom(DEFAULT_BOM_CSV)
    print(f"   Найдено уникальных масс: {len(masses)}")
    if not masses:
        print("   Массы не найдены. Завершение.")
        return
    
    # Шаг 2: Получаем существующие коды из маршрутов
    print("\n2. Проверка существующих маршрутов...")
    existing_codes = get_existing_product_codes(DEFAULT_ROUTES_CSV)
    print(f"   Найдено существующих product_code в маршрутах: {len(existing_codes)}")
    
    # Шаг 3: Добавляем маршруты для масс
    print("\n3. Добавление маршрутов для масс в dataset_routes.csv...")
    routes_added = add_mass_routes_to_csv(DEFAULT_ROUTES_CSV, masses, existing_codes)
    print(f"   Добавлено маршрутов: {routes_added}")
    
    # Шаг 4: Добавляем правила маршрутизации для масс
    print("\n4. Добавление правил маршрутизации для масс в product_routing_rules.csv...")
    rules_added = add_mass_rules_to_csv(DEFAULT_RULES_CSV, masses)
    print(f"   Добавлено правил: {rules_added}")
    
    print(f"\n=== Готово! Добавлено маршрутов: {routes_added}, правил: {rules_added} ===")
    print("\nПримечание: Теперь можно конвертировать CSV в Excel через xlsx_to_csv.py (в обратном направлении)")


if __name__ == "__main__":
    main()
    sys.exit(0)
