"""
Проверка полноты данных для запуска системы: маршруты и правила выбора РЦ для всех ГП.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.models.product import Product
from backend.core.models.manufacturing_route import ManufacturingRoute
from backend.core.models.route_operation import RouteOperation
from backend.core.models.product_routing_rule import ProductRoutingRule
from backend.core.models.enums import ProductType


def _norm_code(s: str | None) -> str:
    """Нормализация кода продукта для сравнения (убираем пробелы)."""
    return (s or "").strip()


def _base_code(norm_code: str) -> str:
    """Базовый код без суффикса _N (при дублировании в датасете)."""
    if "_" in norm_code:
        rest = norm_code.rsplit("_", 1)[-1]
        if rest.isdigit():
            return norm_code.rsplit("_", 1)[0]
    return norm_code


def _as_product(row_or_product):
    """Из результата select(Product) извлечь Product (Row с одним столбцом или сам Product)."""
    if hasattr(row_or_product, "__getitem__") and hasattr(row_or_product, "__len__") and len(row_or_product) == 1:
        return row_or_product[0]
    return row_or_product


def get_routes_and_rules_validation(db: Session) -> dict:
    """
    Проверяет, что у всех ГП (FINISHED_GOOD) есть хотя бы один маршрут с операциями
    и хотя бы одна запись в правилах выбора РЦ.

    Возвращает:
    - ok: True, если нет пропусков
    - missing_in_routes: список product_code без маршрута (или без операций)
    - missing_in_rules: список product_code без правил выбора РЦ
    - product_count: всего ГП
    - routes_ok_count, rules_ok_count: количество ГП с данными
    - routes_with_ops_count: число различных product_id, у которых есть маршрут с операциями (для диагностики)
    - details: список { product_code, product_name, in_routes, in_rules }
    """
    fg_rows = db.execute(
        select(Product).where(Product.product_type == ProductType.FINISHED_GOOD.value)
    ).scalars().all()
    fg_products = [_as_product(r) for r in fg_rows]
    fg_codes = {_norm_code(p.product_code) for p in fg_products}
    product_by_code = {_norm_code(p.product_code): p for p in fg_products}

    routes_with_ops = db.execute(
        select(ManufacturingRoute.product_id).join(
            RouteOperation, RouteOperation.route_id == ManufacturingRoute.id
        ).distinct()
    ).all()
    product_ids_with_route = {str(r[0]) for r in routes_with_ops if r[0] is not None}
    routes_with_ops_count = len(product_ids_with_route)

    codes_with_route = set()
    for p in fg_products:
        pid = str(p.id)
        if pid in product_ids_with_route:
            codes_with_route.add(_norm_code(p.product_code))

    rules_codes = {_norm_code(r[0]) for r in db.execute(
        select(ProductRoutingRule.product_code).distinct()
    ).all()}

    def has_rules(norm_code: str) -> bool:
        return norm_code in rules_codes or _base_code(norm_code) in rules_codes

    missing_in_routes = sorted(fg_codes - codes_with_route)
    missing_in_rules = sorted(c for c in fg_codes if not has_rules(c))
    ok = len(missing_in_routes) == 0 and len(missing_in_rules) == 0

    details = []
    for code in sorted(fg_codes):
        p = product_by_code.get(code)
        details.append({
            "product_code": p.product_code if p else code,
            "product_name": p.product_name if p else None,
            "in_routes": code in codes_with_route,
            "in_rules": has_rules(code),
        })

    return {
        "ok": ok,
        "missing_in_routes": missing_in_routes,
        "missing_in_rules": missing_in_rules,
        "product_count": len(fg_codes),
        "routes_ok_count": len(codes_with_route),
        "rules_ok_count": sum(1 for c in fg_codes if has_rules(c)),
        "routes_with_ops_count": routes_with_ops_count,
        "details": details,
    }
