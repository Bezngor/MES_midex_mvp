"""
Enum-типы домена MES.
"""

import enum


class OrderStatus(str, enum.Enum):
    """Статус производственного заказа."""

    PLANNED = "PLANNED"
    RELEASED = "RELEASED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ON_HOLD = "ON_HOLD"
    CANCELLED = "CANCELLED"
    SHIP = "SHIP"
    IN_WORK = "IN_WORK"


class TaskStatus(str, enum.Enum):
    """Статус производственной задачи."""

    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class WorkCenterStatus(str, enum.Enum):
    """Статус рабочего центра."""

    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    MAINTENANCE = "MAINTENANCE"
    DOWN = "DOWN"


class QualityStatus(str, enum.Enum):
    """Статус проверки качества."""

    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    REWORK = "REWORK"


class ProductType(str, enum.Enum):
    """Тип продукта."""

    RAW_MATERIAL = "RAW_MATERIAL"
    BULK = "BULK"
    PACKAGING = "PACKAGING"
    FINISHED_GOOD = "FINISHED_GOOD"


class BatchStatus(str, enum.Enum):
    """Статус батча."""

    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ProductStatus(str, enum.Enum):
    """Статус продукта в инвентаре."""

    FINISHED = "FINISHED"
    SEMI_FINISHED = "SEMI_FINISHED"


class OrderType(str, enum.Enum):
    """Тип производственного заказа."""

    CUSTOMER = "CUSTOMER"
    INTERNAL_BULK = "INTERNAL_BULK"


class OrderPriority(str, enum.Enum):
    """Приоритет производственного заказа."""

    URGENT = "URGENT"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"
