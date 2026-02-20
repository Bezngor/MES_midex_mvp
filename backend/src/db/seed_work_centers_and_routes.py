"""
Посев рабочих центров и маршрутов после загрузки датасета из CSV.

- Вставляет 9 рабочих центров (Реактор, Тубировка 1/2, Линия розлива 1/2, Зона ЧЗ, полуавтоматы, розлив из емкости), если их ещё нет.
- Для каждого продукта типа FINISHED_GOOD создаёт маршрут с одной операцией
  «Сборка/Упаковка» на WC_TUBE_LINE_1, чтобы заказы можно было выпускать в производство.

Запуск из корня репозитория (после load_dataset_from_csv):
  python -m backend.src.db.seed_work_centers_and_routes
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timezone
from uuid import UUID

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db.session import SessionLocal
from backend.core.models.work_center import WorkCenter
from backend.core.models.manufacturing_route import ManufacturingRoute
from backend.core.models.route_operation import RouteOperation
from backend.core.models.product import Product
from backend.core.models.enums import ProductType, WorkCenterStatus

# UUID рабочих центров (совпадают с FG_PRODUCTS_AND_ROUTES.md)
WC_IDS = {
    "REACTOR": UUID("00000000-0000-0000-0000-000000000001"),
    "MIXER": UUID("00000000-0000-0000-0000-000000000010"),  # Миксер (электромешалка, куб 1 м³)
    "TUBE_LINE": UUID("00000000-0000-0000-0000-000000000002"),
    "FILL_LINE_1": UUID("00000000-0000-0000-0000-000000000003"),
    "FILL_LINE_2": UUID("00000000-0000-0000-0000-000000000004"),
    "CHZ_MANUAL_AREA": UUID("00000000-0000-0000-0000-000000000005"),
    "TUBE_LINE_2": UUID("00000000-0000-0000-0000-000000000006"),
    "SEMI_AUTO_VISCOUS": UUID("00000000-0000-0000-0000-000000000007"),
    "SEMI_AUTO_LIQUID": UUID("00000000-0000-0000-0000-000000000008"),
    "BULK_POUR": UUID("00000000-0000-0000-0000-000000000009"),
}


def seed_work_centers(db: Session) -> None:
    """Вставить рабочих центров для маршрутов и правил выбора РЦ (см. WC_IDS)."""
    existing = {r[0]: r[1] for r in db.execute(select(WorkCenter.id, WorkCenter.name)).all()}
    existing_ids = set(existing.keys())
    to_add = [uid for uid in WC_IDS.values() if uid not in existing_ids]
    now = datetime.now(timezone.utc)
    wcs = [
        WorkCenter(
            id=WC_IDS["REACTOR"],
            name="WC_REACTOR_MAIN",
            resource_type="MACHINE",
            status=WorkCenterStatus.AVAILABLE,
            capacity_units_per_hour=100.0,
            batch_capacity_kg=2000.0,
            cycles_per_shift=2,
            parallel_capacity=1,
            created_at=now,
            updated_at=now,
        ),
        WorkCenter(
            id=WC_IDS["MIXER"],
            name="WC_MIXER",
            resource_type="MACHINE",
            status=WorkCenterStatus.AVAILABLE,
            capacity_units_per_hour=150.0,
            batch_capacity_kg=1000.0,  # Куб 1 м³
            cycles_per_shift=3,
            parallel_capacity=1,
            created_at=now,
            updated_at=now,
        ),
        WorkCenter(
            id=WC_IDS["TUBE_LINE"],
            name="WC_TUBE_LINE_1",
            resource_type="MACHINE",
            status=WorkCenterStatus.AVAILABLE,
            capacity_units_per_hour=150.0,
            batch_capacity_kg=None,
            cycles_per_shift=None,
            parallel_capacity=1,
            created_at=now,
            updated_at=now,
        ),
        WorkCenter(
            id=WC_IDS["FILL_LINE_1"],
            name="WC_FILL_LINE_1",
            resource_type="MACHINE",
            status=WorkCenterStatus.AVAILABLE,
            capacity_units_per_hour=200.0,
            batch_capacity_kg=None,
            cycles_per_shift=None,
            parallel_capacity=4,
            created_at=now,
            updated_at=now,
        ),
        WorkCenter(
            id=WC_IDS["FILL_LINE_2"],
            name="WC_FILL_LINE_2",
            resource_type="MACHINE",
            status=WorkCenterStatus.AVAILABLE,
            capacity_units_per_hour=200.0,
            batch_capacity_kg=None,
            cycles_per_shift=None,
            parallel_capacity=4,
            created_at=now,
            updated_at=now,
        ),
        WorkCenter(
            id=WC_IDS["CHZ_MANUAL_AREA"],
            name="WC_CHZ_MANUAL_AREA",
            resource_type="WORKSTATION",
            status=WorkCenterStatus.AVAILABLE,
            capacity_units_per_hour=100.0,
            batch_capacity_kg=None,
            cycles_per_shift=None,
            parallel_capacity=10,
            created_at=now,
            updated_at=now,
        ),
        WorkCenter(
            id=WC_IDS["TUBE_LINE_2"],
            name="WC_TUBE_LINE_2",
            resource_type="MACHINE",
            status=WorkCenterStatus.AVAILABLE,
            capacity_units_per_hour=150.0,
            batch_capacity_kg=None,
            cycles_per_shift=None,
            parallel_capacity=1,
            created_at=now,
            updated_at=now,
        ),
        WorkCenter(
            id=WC_IDS["SEMI_AUTO_VISCOUS"],
            name="WC_SEMI_AUTO_VISCOUS",
            resource_type="MACHINE",
            status=WorkCenterStatus.AVAILABLE,
            capacity_units_per_hour=50.0,
            batch_capacity_kg=None,
            cycles_per_shift=None,
            parallel_capacity=1,
            created_at=now,
            updated_at=now,
        ),
        WorkCenter(
            id=WC_IDS["SEMI_AUTO_LIQUID"],
            name="WC_SEMI_AUTO_LIQUID",
            resource_type="MACHINE",
            status=WorkCenterStatus.AVAILABLE,
            capacity_units_per_hour=50.0,
            batch_capacity_kg=None,
            cycles_per_shift=None,
            parallel_capacity=1,
            created_at=now,
            updated_at=now,
        ),
        WorkCenter(
            id=WC_IDS["BULK_POUR"],
            name="WC_BULK_POUR",
            resource_type="MACHINE",
            status=WorkCenterStatus.AVAILABLE,
            capacity_units_per_hour=30.0,
            batch_capacity_kg=None,
            cycles_per_shift=None,
            parallel_capacity=1,
            created_at=now,
            updated_at=now,
        ),
    ]
    for wc in wcs:
        if wc.id not in existing_ids:
            db.add(wc)
    # Переименовать старый WC_AUTO_LIQUID_SOAP в WC_FILL_LINE_1, если он уже есть в БД
    old_name = "WC_AUTO_LIQUID_SOAP"
    wc_third_id = WC_IDS["FILL_LINE_1"]
    if wc_third_id in existing_ids and existing.get(wc_third_id) == old_name:
        row = db.get(WorkCenter, wc_third_id)
        if row:
            row.name = "WC_FILL_LINE_1"
            row.updated_at = now
    db.commit()
    print("Work centers seeded.")


def seed_routes_for_fg(db: Session) -> None:
    """Для каждого ГП создать маршрут с одной операцией на WC_TUBE_LINE_1."""
    wc_tube_id = WC_IDS["TUBE_LINE"]
    fg_products = db.execute(
        select(Product).where(Product.product_type == ProductType.FINISHED_GOOD.value)
    ).scalars().all()
    existing_routes = db.execute(
        select(ManufacturingRoute.product_id).where(
            ManufacturingRoute.product_id.in_([str(p.id) for p in fg_products])
        )
    ).scalars().all()
    existing_product_ids = {str(r[0]) for r in existing_routes}
    created = 0
    for product in fg_products:
        if str(product.id) in existing_product_ids:
            continue
        route = ManufacturingRoute(
            product_id=str(product.id),
            route_name=f"{product.product_name[:80]} — маршрут",
            description="Маршрут по умолчанию (одна операция)",
        )
        db.add(route)
        db.flush()
        op = RouteOperation(
            route_id=route.id,
            operation_sequence=1,
            operation_name="Сборка/Упаковка",
            work_center_id=wc_tube_id,
            estimated_duration_minutes=60,
        )
        db.add(op)
        created += 1
    db.commit()
    print(f"Manufacturing routes created for {created} FG products.")


def main() -> None:
    db = SessionLocal()
    try:
        seed_work_centers(db)
        seed_routes_for_fg(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
