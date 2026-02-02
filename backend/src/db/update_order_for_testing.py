"""
Скрипт для изменения заказа в БД (имитация обновления из 1С).

Использование:
    python -m backend.src.db.update_order_for_testing --order-number H000-003925-3 --quantity 150.5
    python -m backend.src.db.update_order_for_testing --order-number H000-003925-3 --quantity 200 --due-date "2026-02-15"
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from backend.src.db.session import SessionLocal
from backend.core.models.manufacturing_order import ManufacturingOrder


def main():
    parser = argparse.ArgumentParser(description="Изменить заказ в БД (имитация обновления из 1С)")
    parser.add_argument(
        "--order-number",
        type=str,
        required=True,
        help="Номер заказа (order_number) для изменения"
    )
    parser.add_argument(
        "--quantity",
        type=float,
        help="Новое количество"
    )
    parser.add_argument(
        "--due-date",
        type=str,
        help="Новая дата выполнения (формат: YYYY-MM-DD или YYYY-MM-DD HH:MM:SS)"
    )
    parser.add_argument(
        "--priority",
        type=str,
        choices=["URGENT", "HIGH", "NORMAL", "LOW"],
        help="Новый приоритет"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только показать, что будет изменено, без фактического изменения"
    )

    args = parser.parse_args()

    db: Session = SessionLocal()
    try:
        # Находим заказ по order_number
        order = db.query(ManufacturingOrder).filter(
            ManufacturingOrder.order_number == args.order_number
        ).first()

        if not order:
            print(f"❌ Заказ с номером '{args.order_number}' не найден")
            sys.exit(1)

        print(f"Найден заказ:")
        print(f"  ID: {order.id}")
        print(f"  Номер: {order.order_number}")
        print(f"  Продукт: {order.product_id}")
        print(f"  Текущее количество: {order.quantity}")
        print(f"  Текущая дата выполнения: {order.due_date}")
        print(f"  Текущий приоритет: {order.priority}")
        print(f"  Обновлён: {order.updated_at}")

        changes = []
        if args.quantity is not None:
            old_qty = float(order.quantity)
            new_qty = Decimal(str(args.quantity))
            changes.append(f"quantity: {old_qty} → {new_qty}")
            if not args.dry_run:
                order.quantity = new_qty

        if args.due_date is not None:
            try:
                # Пробуем разные форматы даты
                if len(args.due_date) == 10:  # YYYY-MM-DD
                    new_due_date = datetime.strptime(args.due_date, "%Y-%m-%d")
                else:
                    new_due_date = datetime.strptime(args.due_date, "%Y-%m-%d %H:%M:%S")
                
                old_due_date = order.due_date
                changes.append(f"due_date: {old_due_date} → {new_due_date}")
                if not args.dry_run:
                    order.due_date = new_due_date
            except ValueError as e:
                print(f"❌ Ошибка парсинга даты: {e}")
                sys.exit(1)

        if args.priority is not None:
            old_priority = order.priority
            changes.append(f"priority: {old_priority} → {args.priority}")
            if not args.dry_run:
                order.priority = args.priority

        if not changes:
            print("⚠️  Не указано ни одного поля для изменения")
            sys.exit(1)

        print(f"\nИзменения:")
        for change in changes:
            print(f"  - {change}")

        if args.dry_run:
            print("\n[DRY RUN] Изменения не применены")
            return

        # Обновляем updated_at автоматически (через SQLAlchemy onupdate)
        db.commit()
        print(f"\n✅ Заказ успешно обновлён")
        print(f"   Обновлён: {order.updated_at}")

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
