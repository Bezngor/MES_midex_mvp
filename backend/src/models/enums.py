"""
Enum types for MES domain statuses.
"""

import enum


class OrderStatus(str, enum.Enum):
    """Manufacturing order status."""

    PLANNED = "PLANNED"
    RELEASED = "RELEASED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ON_HOLD = "ON_HOLD"
    CANCELLED = "CANCELLED"


class TaskStatus(str, enum.Enum):
    """Production task status."""

    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class WorkCenterStatus(str, enum.Enum):
    """Work center status."""

    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    MAINTENANCE = "MAINTENANCE"
    DOWN = "DOWN"


class QualityStatus(str, enum.Enum):
    """Quality inspection status."""

    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    REWORK = "REWORK"
