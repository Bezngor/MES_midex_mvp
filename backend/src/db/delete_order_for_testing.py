"""
Скрипт для удаления заказа из БД (имитация удаления в 1С).

Использование:
    python -m backend.src.db.delete_order_for_testing --order-number H000-003925-3
"""

import sys
import argparse
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from backend.src.db.session import SessionLocal
from backend.core.models.manufacturing_order import ManufacturingOrder


def main():
    parser = argparse.ArgumentParser(description="Удалить заказ из БД (имитация удаления в 1С)")
    parser.add_argument(
        "--order-number",
        type=str,
        required=True,
        help="Номер заказа (order_number) для удаления"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только показать, что будет удалено, без фактического удаления"
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
        print(f"  Количество: {order.quantity}")
        print(f"  Дата выполнения: {order.due_date}")

        if args.dry_run:
            print("\n[DRY RUN] Заказ НЕ будет удалён")
            return

        # Удаляем заказ
        db.delete(order)
        db.commit()
        print(f"\n✅ Заказ '{args.order_number}' успешно удалён из БД")
        print(f"   (Снимки остаются в таблице order_snapshots для выявления удаления)")

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
