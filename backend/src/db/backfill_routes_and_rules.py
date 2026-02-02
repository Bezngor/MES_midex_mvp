"""
Backfill: для каждого ГП без маршрута (с операциями) или без правила выбора РЦ —
создать минимальные данные, чтобы валидация «Система готова к запуску» проходила.

Временный модуль для тестового окружения. После тестирования можно удалить или архивировать.
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timezone

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from sqlalchemy import select, exists
from sqlalchemy.orm import Session

from backend.src.db.session import SessionLocal
from backend.core.models.product import Product
from backend.core.models.work_center import WorkCenter
from backend.core.models.manufacturing_route import ManufacturingRoute
from backend.core.models.route_operation import RouteOperation
from backend.core.models.product_routing_rule import ProductRoutingRule
from backend.core.models.enums import ProductType


def _norm(s: str | None) -> str:
    return (s or "").strip()


def backfill_routes_and_rules(db: Session) -> tuple[int, int]:
    """
    Для каждого ГП: если нет маршрута с операциями — создать маршрут с одной операцией;
    если нет правила выбора РЦ (по нормализованному product_code или базовому коду) — добавить правило.
    Возвращает (добавлено маршрутов, добавлено правил).
    """
    wc_row = db.execute(
        select(WorkCenter).where(WorkCenter.name == "WC_TUBE_LINE_1")
    ).scalars().first()
    wc = wc_row
    if not wc:
        raise RuntimeError("Рабочий центр WC_TUBE_LINE_1 не найден. Сначала выполните seed_work_centers_and_routes.")

    fg_products = db.execute(
        select(Product).where(Product.product_type == ProductType.FINISHED_GOOD.value)
    ).scalars().all()

    routes_with_ops = db.execute(
        select(ManufacturingRoute.product_id).join(
            RouteOperation, RouteOperation.route_id == ManufacturingRoute.id
        ).distinct()
    ).scalars().all()
    product_ids_with_route = {str(r[0]) for r in routes_with_ops}

    rules_codes = {_norm(r[0]) for r in db.execute(
        select(ProductRoutingRule.product_code).distinct()
    ).scalars().all()}

    def has_rule(norm_code: str) -> bool:
        if norm_code in rules_codes:
            return True
        if "_" in norm_code and norm_code.rsplit("_", 1)[-1].isdigit():
            base = norm_code.rsplit("_", 1)[0]
            if base in rules_codes:
                return True
        return False

    def rule_exists_in_db(norm_code: str, work_center_id) -> bool:
        """Проверка по текущему состоянию БД (надёжно при разных сессиях/коммитах)."""
        subq = exists(
            select(ProductRoutingRule).where(
                ProductRoutingRule.product_code == norm_code,
                ProductRoutingRule.work_center_id == work_center_id,
            )
        )
        return db.execute(select(subq)).scalar()

    now = datetime.now(timezone.utc)
    routes_added = 0
    rules_added = 0

    for product in fg_products:
        pid = str(product.id)
        norm_code = _norm(product.product_code)

        if pid not in product_ids_with_route:
            route = ManufacturingRoute(
                product_id=pid,
                route_name=f"{product.product_name[:80]} — маршрут (backfill)",
                description="Минимальный маршрут для теста",
                created_at=now,
                updated_at=now,
            )
            db.add(route)
            db.flush()
            op = RouteOperation(
                route_id=route.id,
                operation_sequence=1,
                operation_name="Сборка/Упаковка",
                work_center_id=wc.id,
                estimated_duration_minutes=60,
            )
            db.add(op)
            routes_added += 1

        if not has_rule(norm_code):
            if not rule_exists_in_db(norm_code, wc.id):
                db.add(ProductRoutingRule(
                    product_code=norm_code,
                    work_center_id=wc.id,
                    priority_order=1,
                    min_quantity=None,
                    max_quantity=None,
                ))
                rules_added += 1
            rules_codes.add(norm_code)

    db.commit()
    return routes_added, rules_added
