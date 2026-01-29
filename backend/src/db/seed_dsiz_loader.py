"""
Утилита для применения DSIZ seed-данных к базе данных,
сконфигурированной через переменную окружения DATABASE_URL.

Назначение:
- Заполнить DSIZ-специфичные таблицы начальными данными из `seed_dsiz_data.sql`;
- Вывести краткую сводку по количеству записей в ключевых DSIZ-таблицах
  для быстрой проверки корректности загрузки.

Важно:
- Скрипт рассчитан на PostgreSQL (как и основной проект).
- Для тестов в `pytest` используется отдельная SQLite-БД — этот скрипт её не затрагивает.

Пример использования (локально или на тестовой БД):

    # В каталоге backend/
    export DATABASE_URL=postgresql://mes_user:mes_password@localhost:5432/mes_db
    python -m backend.src.db.seed_dsiz_loader
"""

from pathlib import Path

from sqlalchemy import text

from backend.src.db.session import engine


SEED_FILE_NAME = "seed_dsiz_data.sql"

# Таблица, по которой проверяем, что миграции DSIZ уже применены
DSIZ_CHECK_TABLE = "dsiz_work_center_modes"


def _dsiz_tables_exist() -> bool:
    """Проверяет, что в БД есть таблицы DSIZ (миграции применены)."""
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = :name)"
            ),
            {"name": DSIZ_CHECK_TABLE},
        )
        return bool(result.scalar_one())


def load_seed_sql() -> str:
    """
    Загружает содержимое SQL-файла с seed-данными.

    Returns:
        Полный текст SQL-скрипта.
    """
    path = Path(__file__).with_name(SEED_FILE_NAME)
    if not path.exists():
        raise FileNotFoundError(
            f"DSIZ seed file not found: {path}. "
            "Убедитесь, что файл существует и путь корректен."
        )

    return path.read_text(encoding="utf-8")


def _split_sql_statements(sql: str) -> list[str]:
    """
    Очищает SQL от комментариев и разбивает на отдельные выражения.

    - Удаляет строковые комментарии `-- ...`
    - Удаляет блочные комментарии `/* ... */`
    - Делит по `;` и отфильтровывает пустые выражения
    """
    lines = sql.splitlines()
    cleaned_lines: list[str] = []
    in_block_comment = False

    for line in lines:
        stripped = line.strip()

        # Блочные комментарии
        if in_block_comment:
            if "*/" in stripped:
                in_block_comment = False
            continue

        if stripped.startswith("/*"):
            # Если комментарий в одну строку, просто пропускаем её
            if "*/" not in stripped:
                in_block_comment = True
            continue

        # Однострочные комментарии и пустые строки
        if not stripped or stripped.startswith("--"):
            continue

        cleaned_lines.append(line)

    cleaned_sql = "\n".join(cleaned_lines)

    statements: list[str] = []
    for part in cleaned_sql.split(";"):
        stmt = part.strip()
        if stmt:
            statements.append(stmt)

    return statements


def apply_seed(sql: str) -> None:
    """
    Применяет SQL-скрипт к текущей БД (DATABASE_URL).
    """
    print("📦 Применение DSIZ seed-данных...")
    statements = _split_sql_statements(sql)

    if not statements:
        raise ValueError("SQL-скрипт не содержит выражений после очистки комментариев.")

    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))

    print(f"✅ DSIZ seed-данные успешно применены. Выполнено выражений: {len(statements)}.")


def print_seed_summary() -> None:
    """
    Выводит сводку по размеру ключевых DSIZ-таблиц.
    """
    tables = [
        ("Work Center Modes", "dsiz_work_center_modes"),
        ("Changeover Matrix", "dsiz_changeover_matrix"),
        ("Product Routing", "dsiz_product_work_center_routing"),
        ("Base Rates", "dsiz_base_rates"),
        ("Workforce Requirements", "dsiz_workforce_requirements"),
    ]

    print("\n📊 Сводка по DSIZ-таблицам:")
    with engine.connect() as conn:
        for label, table in tables:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar_one()
            except Exception as exc:  # noqa: BLE001
                print(f"  - {label:24s} ({table}): ❌ ошибка запроса: {exc}")
            else:
                print(f"  - {label:24s} ({table}): {count} записей")


def main() -> None:
    """
    Точка входа CLI.
    """
    if not _dsiz_tables_exist():
        raise SystemExit(
            "Таблицы DSIZ в БД не найдены. Сначала примените миграции:\n\n"
            "  cd backend\n"
            "  $env:DATABASE_URL = \"postgresql://mes_user:mes_password@localhost:5432/mes_db\"\n"
            "  alembic upgrade head\n\n"
            "После этого из корня репозитория снова запустите seed_dsiz_loader."
        )
    sql = load_seed_sql()
    apply_seed(sql)
    print_seed_summary()


if __name__ == "__main__":
    main()

