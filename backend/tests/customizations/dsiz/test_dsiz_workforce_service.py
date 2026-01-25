"""
Unit тесты для DSIZWorkforceService.

Покрытие: 90%+ (все основные сценарии).
"""

import pytest
from backend.customizations.dsiz.services.dsiz_workforce_service import DSIZWorkforceService


# ============================================================================
# can_run Tests
# ============================================================================

def test_tube_line_no_packer():
    """Тест: тубировка не может работать без упаковщика."""
    workforce = DSIZWorkforceService()
    assert not workforce.can_run("WC_TUBE_LINE_1", {"OPERATOR": 1, "PACKER": 0})


def test_tube_line_no_operator():
    """Тест: тубировка не может работать без оператора."""
    workforce = DSIZWorkforceService()
    assert not workforce.can_run("WC_TUBE_LINE_1", {"OPERATOR": 0, "PACKER": 1})


def test_tube_line_with_both():
    """Тест: тубировка может работать с оператором и упаковщиком."""
    workforce = DSIZWorkforceService()
    assert workforce.can_run("WC_TUBE_LINE_1", {"OPERATOR": 1, "PACKER": 1})


def test_reactor_needs_operator():
    """Тест: реактор требует оператора."""
    workforce = DSIZWorkforceService()
    assert not workforce.can_run("WC_REACTOR_MAIN", {"OPERATOR": 0})
    assert workforce.can_run("WC_REACTOR_MAIN", {"OPERATOR": 1})


def test_reactor_with_extra_operator():
    """Тест: реактор может работать с дополнительным оператором."""
    workforce = DSIZWorkforceService()
    assert workforce.can_run("WC_REACTOR_MAIN", {"OPERATOR": 2})


def test_auto_can_run_with_3():
    """Тест: авто-линия может работать с 3 операторами (degraded mode)."""
    workforce = DSIZWorkforceService()
    assert workforce.can_run("WC_AUTO_LIQUID_SOAP", {"OPERATOR": 3})


def test_auto_can_run_with_4():
    """Тест: авто-линия может работать с 4 операторами (full mode)."""
    workforce = DSIZWorkforceService()
    assert workforce.can_run("WC_AUTO_LIQUID_SOAP", {"OPERATOR": 4})


def test_auto_cannot_run_with_2():
    """Тест: авто-линия не может работать с 2 операторами."""
    workforce = DSIZWorkforceService()
    assert not workforce.can_run("WC_AUTO_LIQUID_SOAP", {"OPERATOR": 2})


def test_auto_cannot_run_with_0():
    """Тест: авто-линия не может работать без операторов."""
    workforce = DSIZWorkforceService()
    assert not workforce.can_run("WC_AUTO_LIQUID_SOAP", {"OPERATOR": 0})


def test_unknown_work_center():
    """Тест: неизвестный центр может работать (нет ограничений)."""
    workforce = DSIZWorkforceService()
    assert workforce.can_run("WC_UNKNOWN", {"OPERATOR": 0})
    assert workforce.can_run("WC_UNKNOWN", {})


# ============================================================================
# get_effective_rate Tests
# ============================================================================

def test_auto_degradation_3_operators():
    """Тест: авто-линия с 3 операторами даёт 0.5 rate."""
    workforce = DSIZWorkforceService()
    rate = workforce.get_effective_rate("WC_AUTO_LIQUID_SOAP", {"OPERATOR": 3}, 1000)
    assert rate == 500


def test_auto_full_rate_4_operators():
    """Тест: авто-линия с 4 операторами даёт полную скорость."""
    workforce = DSIZWorkforceService()
    rate = workforce.get_effective_rate("WC_AUTO_LIQUID_SOAP", {"OPERATOR": 4}, 1000)
    assert rate == 1000


def test_auto_full_rate_5_operators():
    """Тест: авто-линия с 5 операторами даёт полную скорость (не более базовой)."""
    workforce = DSIZWorkforceService()
    rate = workforce.get_effective_rate("WC_AUTO_LIQUID_SOAP", {"OPERATOR": 5}, 1000)
    assert rate == 1000


def test_reactor_rate_unchanged():
    """Тест: реактор всегда даёт базовую скорость (нет деградации)."""
    workforce = DSIZWorkforceService()
    rate = workforce.get_effective_rate("WC_REACTOR_MAIN", {"OPERATOR": 1}, 500)
    assert rate == 500


def test_tube_line_rate_unchanged():
    """Тест: тубировка всегда даёт базовую скорость (нет деградации)."""
    workforce = DSIZWorkforceService()
    rate = workforce.get_effective_rate("WC_TUBE_LINE_1", {"OPERATOR": 1, "PACKER": 1}, 1000)
    assert rate == 1000


def test_unknown_work_center_rate():
    """Тест: неизвестный центр возвращает базовую скорость."""
    workforce = DSIZWorkforceService()
    rate = workforce.get_effective_rate("WC_UNKNOWN", {"OPERATOR": 0}, 1000)
    assert rate == 1000


def test_auto_rate_with_different_base():
    """Тест: авто-линия с разной базовой скоростью."""
    workforce = DSIZWorkforceService()
    # 3 оператора → 0.5
    rate1 = workforce.get_effective_rate("WC_AUTO_LIQUID_SOAP", {"OPERATOR": 3}, 2000)
    assert rate1 == 1000
    # 4 оператора → 1.0
    rate2 = workforce.get_effective_rate("WC_AUTO_LIQUID_SOAP", {"OPERATOR": 4}, 2000)
    assert rate2 == 2000


# ============================================================================
# calculate_reserve Tests
# ============================================================================

def test_calculate_reserve_basic():
    """Тест: расчёт резерва персонала."""
    workforce = DSIZWorkforceService()
    shift_staff = {"OPERATOR": 5, "PACKER": 2}
    reserve = workforce.calculate_reserve(shift_staff)
    # Минимальные требования: OPERATOR=4 (авто), PACKER=1 (тубировка)
    # Резерв: OPERATOR=1, PACKER=1
    assert reserve["OPERATOR"] == 1
    assert reserve["PACKER"] == 1


def test_calculate_reserve_no_reserve():
    """Тест: расчёт резерва при минимальном штате."""
    workforce = DSIZWorkforceService()
    shift_staff = {"OPERATOR": 4, "PACKER": 1}
    reserve = workforce.calculate_reserve(shift_staff)
    # Резерв должен быть 0
    assert reserve["OPERATOR"] == 0
    assert reserve["PACKER"] == 0


def test_calculate_reserve_extra_staff():
    """Тест: расчёт резерва при избыточном штате."""
    workforce = DSIZWorkforceService()
    shift_staff = {"OPERATOR": 10, "PACKER": 5}
    reserve = workforce.calculate_reserve(shift_staff)
    # Резерв: OPERATOR=6, PACKER=4
    assert reserve["OPERATOR"] == 6
    assert reserve["PACKER"] == 4


def test_calculate_reserve_missing_role():
    """Тест: расчёт резерва при отсутствии роли в штате."""
    workforce = DSIZWorkforceService()
    shift_staff = {"OPERATOR": 5}
    reserve = workforce.calculate_reserve(shift_staff)
    # PACKER отсутствует, но требование есть → резерв отрицательный (0)
    assert reserve.get("PACKER", 0) == 0
    assert reserve["OPERATOR"] == 1


def test_calculate_reserve_empty_staff():
    """Тест: расчёт резерва при пустом штате."""
    workforce = DSIZWorkforceService()
    shift_staff = {}
    reserve = workforce.calculate_reserve(shift_staff)
    # Все резервы должны быть 0
    assert reserve == {}


def test_calculate_reserve_unknown_role():
    """Тест: расчёт резерва с неизвестной ролью."""
    workforce = DSIZWorkforceService()
    shift_staff = {"OPERATOR": 5, "PACKER": 2, "SUPERVISOR": 1}
    reserve = workforce.calculate_reserve(shift_staff)
    # SUPERVISOR не в требованиях → резерв = весь штат
    assert reserve.get("SUPERVISOR", 0) == 1


# ============================================================================
# Integration Tests
# ============================================================================

def test_full_workflow():
    """Тест: полный workflow проверки и расчёта."""
    workforce = DSIZWorkforceService()
    
    # Проверка возможности работы
    assert workforce.can_run("WC_AUTO_LIQUID_SOAP", {"OPERATOR": 3})
    
    # Расчёт эффективной скорости
    rate = workforce.get_effective_rate("WC_AUTO_LIQUID_SOAP", {"OPERATOR": 3}, 1000)
    assert rate == 500
    
    # Расчёт резерва
    shift_staff = {"OPERATOR": 5, "PACKER": 2}
    reserve = workforce.calculate_reserve(shift_staff)
    assert reserve["OPERATOR"] >= 0
    assert reserve["PACKER"] >= 0
