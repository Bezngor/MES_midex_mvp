"""
Скрипт для создания снимков существующих заказов.

Использование:
    python -m backend.src.db.create_order_snapshots [--order-type CUSTOMER|INTERNAL_BULK] [--snapshot-type AUTO|MANUAL|SYNC]

Пример:
    python -m backend.src.db.create_order_snapshots --order-type CUSTOMER --snapshot-type SYNC
"""

import sys
import argparse
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from backend.src.db.session import SessionLocal
from backend.core.services.order_comparison_service import OrderComparisonService
from backend.core.models.enums import OrderType


def main():
    parser = argparse.ArgumentParser(description="Создать снимки существующих заказов")
    parser.add_argument(
        "--order-type",
        type=str,
        choices=["CUSTOMER", "INTERNAL_BULK"],
        default="CUSTOMER",
        help="Тип заказов для создания снимков (по умолчанию: CUSTOMER)"
    )
    parser.add_argument(
        "--snapshot-type",
        type=str,
        choices=["AUTO", "MANUAL", "SYNC"],
        default="SYNC",
        help="Тип снимка (по умолчанию: SYNC)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только показать, сколько снимков будет создано, без фактического создания"
    )

    args = parser.parse_args()

    db: Session = SessionLocal()
    try:
        comparison_service = OrderComparisonService(db)

        # Получаем количество заказов указанного типа
        from backend.core.models.manufacturing_order import ManufacturingOrder
        from sqlalchemy import select, func

        count_query = select(func.count(ManufacturingOrder.id)).where(
            ManufacturingOrder.order_type == args.order_type
        )
        total_orders = db.execute(count_query).scalar()

        print(f"Найдено заказов типа {args.order_type}: {total_orders}")

        if args.dry_run:
            print(f"[DRY RUN] Будет создано снимков: {total_orders}")
            return

        print(f"Создание снимков...")
        snapshots = comparison_service.create_snapshots_for_all_orders(
            order_type=args.order_type,
            snapshot_type=args.snapshot_type,
            notes=f"Автоматическое создание снимков для всех заказов типа {args.order_type}"
        )

        db.commit()
        print(f"✅ Успешно создано снимков: {len(snapshots)}")

        # Проверяем результат
        print("\nПроверка результата:")
        new_orders = comparison_service.identify_new_orders(order_type=args.order_type)
        changed_orders = comparison_service.identify_changed_orders(order_type=args.order_type)
        print(f"  Новых заказов: {len(new_orders)}")
        print(f"  Изменённых заказов: {len(changed_orders)}")

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
