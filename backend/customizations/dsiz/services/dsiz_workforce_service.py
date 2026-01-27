"""
DSIZ Workforce Service.

Управление нормами укомплектованности персоналом и расчёт деградации производительности.

Основные функции:
- Проверка возможности работы центра с текущим штатом (can_run)
- Расчёт эффективной скорости с учётом деградации (get_effective_rate)
- Расчёт резерва персонала (calculate_reserve)
"""

from typing import Dict, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
import yaml
from pathlib import Path


class StaffState(BaseModel):
    """Состояние штата персонала."""
    OPERATOR: int = 0
    PACKER: int = 0


class WorkforceRequirement(BaseModel):
    """Требование к персоналу для рабочего центра."""
    role_name: str
    required_count: int
    is_mandatory: bool = True
    min_count_for_degraded_mode: Optional[int] = None
    degradation_factor: Optional[float] = None


class DSIZWorkforceService:
    """
    Сервис управления персоналом для DSIZ.
    
    Обрабатывает:
    - Нормы укомплектованности по Work Center
    - Деградацию производительности при нехватке персонала
    - Расчёт резерва персонала
    """
    
    def __init__(self, db: Optional[Session] = None):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных (опционально, для будущего использования БД)
        """
        self.db = db
        self._requirements_cache: Dict[str, Dict[str, WorkforceRequirement]] = {}
        self._load_requirements_from_config()
    
    def _load_requirements_from_config(self) -> None:
        """
        Загрузка требований к персоналу из конфига (MVP).
        
        В Phase 2 будет загрузка из таблицы dsiz_workforce_requirements.
        """
        # Пытаемся загрузить из config/dsiz_config.yaml
        config_paths = [
            Path("./config/dsiz_config.yaml"),
            Path("./backend/config/dsiz_config.yaml"),
        ]
        
        config_data = None
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f)
                    break
                except Exception as e:
                    print(f"⚠️  Ошибка загрузки конфига {config_path}: {e}")
        
        # Если конфиг не найден, используем хардкод для MVP
        if config_data is None:
            self._load_default_requirements()
            return
        
        # Загружаем требования из конфига
        workforce_config = config_data.get('workforce', {})
        if not workforce_config:
            self._load_default_requirements()
            return
        
        for wc_id, roles in workforce_config.items():
            self._requirements_cache[wc_id] = {}
            for role_name, role_config in roles.items():
                req = WorkforceRequirement(
                    role_name=role_name,
                    required_count=role_config.get('required_count', 0),
                    is_mandatory=role_config.get('is_mandatory', True),
                    min_count_for_degraded_mode=role_config.get('min_count_for_degraded_mode'),
                    degradation_factor=role_config.get('degradation_factor')
                )
                self._requirements_cache[wc_id][role_name] = req
    
    def _load_default_requirements(self) -> None:
        """
        Загрузка требований по умолчанию (хардкод для MVP).
        
        Согласно спецификации:
        - WC_REACTOR_MAIN: 1 OPERATOR (mandatory)
        - WC_TUBE_LINE_1: 1 OPERATOR + 1 PACKER (оба mandatory)
        - WC_AUTO_LIQUID_SOAP: 4 OPERATOR (min_degraded=3, factor=0.5)
        """
        # Реактор: 1 оператор (обязательно)
        self._requirements_cache["WC_REACTOR_MAIN"] = {
            "OPERATOR": WorkforceRequirement(
                role_name="OPERATOR",
                required_count=1,
                is_mandatory=True
            )
        }
        
        # Тубировка: оператор + упаковщик (оба обязательны)
        self._requirements_cache["WC_TUBE_LINE_1"] = {
            "OPERATOR": WorkforceRequirement(
                role_name="OPERATOR",
                required_count=1,
                is_mandatory=True
            ),
            "PACKER": WorkforceRequirement(
                role_name="PACKER",
                required_count=1,
                is_mandatory=True
            )
        }
        
        # Авто-розлив: 4 оператора (3=0.5 rate)
        self._requirements_cache["WC_AUTO_LIQUID_SOAP"] = {
            "OPERATOR": WorkforceRequirement(
                role_name="OPERATOR",
                required_count=4,
                is_mandatory=False,  # Не обязательны все 4
                min_count_for_degraded_mode=3,
                degradation_factor=0.5
            )
        }
    
    def can_run(self, work_center_id: str, staff_state: Dict[str, int]) -> bool:
        """
        Проверка возможности работы центра с текущим штатом.
        
        Args:
            work_center_id: Идентификатор рабочего центра (например, "WC_REACTOR_MAIN")
            staff_state: Словарь с количеством персонала по ролям
                        {"OPERATOR": 1, "PACKER": 0}
        
        Returns:
            True если центр может работать, False если нет
        
        Примеры:
            - Тубировка: требует 1 OPERATOR + 1 PACKER (оба mandatory)
            - Авто-линия: 4 OPERATOR, 3=degraded OK
        """
        requirements = self._requirements_cache.get(work_center_id)
        
        # Если требований нет - центр может работать (нет ограничений)
        if not requirements:
            return True
        
        # Проверяем все обязательные роли
        for role_name, requirement in requirements.items():
            available_count = staff_state.get(role_name, 0)
            
            # Если роль обязательна - проверяем минимальное количество
            if requirement.is_mandatory:
                min_required = requirement.min_count_for_degraded_mode or requirement.required_count
                if available_count < min_required:
                    return False
            # Если роль не обязательна, но есть минимальное для деградированного режима
            elif requirement.min_count_for_degraded_mode is not None:
                if available_count < requirement.min_count_for_degraded_mode:
                    return False
        
        return True
    
    def get_effective_rate(
        self, 
        work_center_id: str, 
        staff_state: Dict[str, int], 
        base_rate: float
    ) -> float:
        """
        Расчёт эффективной скорости с учётом деградации при нехватке персонала.
        
        Args:
            work_center_id: Идентификатор рабочего центра
            staff_state: Словарь с количеством персонала по ролям
            base_rate: Базовая скорость (единиц/час)
        
        Returns:
            Эффективная скорость с учётом деградации
        
        Примеры:
            - Авто-линия: 3/4 оператора → base_rate * 0.5
            - Полная укомплектованность → base_rate * 1.0
        """
        requirements = self._requirements_cache.get(work_center_id)
        
        # Если требований нет - возвращаем базовую скорость
        if not requirements:
            return base_rate
        
        # Ищем роли с деградацией
        degradation_factor = 1.0
        
        for role_name, requirement in requirements.items():
            available_count = staff_state.get(role_name, 0)
            required_count = requirement.required_count
            
            # Если есть деградация и не хватает персонала
            if (
                requirement.degradation_factor is not None
                and requirement.min_count_for_degraded_mode is not None
                and available_count < required_count
                and available_count >= requirement.min_count_for_degraded_mode
            ):
                # Применяем фактор деградации
                degradation_factor = min(degradation_factor, requirement.degradation_factor)
        
        return base_rate * degradation_factor
    
    def calculate_reserve(self, shift_staff: Dict[str, int]) -> Dict[str, int]:
        """
        Расчёт резерва персонала (неиспользованные люди).
        
        Args:
            shift_staff: Общий штат смены по ролям {"OPERATOR": 5, "PACKER": 2}
        
        Returns:
            Словарь с резервом по ролям {"OPERATOR": 1, "PACKER": 0}
        
        Примечание:
            В MVP упрощённый расчёт: резерв = общий штат - максимальные минимальные требования.
            Используется максимум минимальных требований по всем центрам (предполагается,
            что центры могут работать параллельно, но для упрощения берём максимум).
            В Phase 2 будет учёт фактически задействованных центров.
        """
        # Собираем максимальные минимальные требования по всем центрам
        # Используем максимум, так как центры могут работать параллельно,
        # но для упрощения MVP берём максимальное требование одного центра
        min_requirements: Dict[str, int] = {}
        
        for wc_id, requirements in self._requirements_cache.items():
            for role_name, requirement in requirements.items():
                # Для расчёта резерва используем required_count (полное требование),
                # а не min_count_for_degraded_mode (деградированный режим)
                min_required = requirement.required_count
                current_min = min_requirements.get(role_name, 0)
                min_requirements[role_name] = max(current_min, min_required)
        
        # Резерв = общий штат - максимальные минимальные требования
        reserve: Dict[str, int] = {}
        for role_name, total_staff in shift_staff.items():
            min_required = min_requirements.get(role_name, 0)
            reserve[role_name] = max(0, total_staff - min_required)
        
        return reserve


