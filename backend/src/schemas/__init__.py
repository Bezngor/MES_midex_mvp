"""
Pydantic schemas / DTOs for API validation and serialization.
"""

from backend.src.schemas.manufacturing_order import (
    ManufacturingOrderBase,
    ManufacturingOrderCreate,
    ManufacturingOrderRead,
    ManufacturingOrderWithTasksRead,
    ManufacturingOrderUpdate,
)
from backend.src.schemas.work_center import (
    WorkCenterBase,
    WorkCenterCreate,
    WorkCenterRead,
    WorkCenterUpdate,
)
from backend.src.schemas.production_task import (
    ProductionTaskBase,
    ProductionTaskRead,
    ProductionTaskUpdate,
)
from backend.src.schemas.manufacturing_route import (
    ManufacturingRouteBase,
    ManufacturingRouteCreate,
    ManufacturingRouteRead,
)
from backend.src.schemas.route_operation import (
    RouteOperationBase,
    RouteOperationCreate,
    RouteOperationRead,
)
from backend.src.schemas.genealogy_record import (
    GenealogyRecordBase,
    GenealogyRecordCreate,
    GenealogyRecordRead,
)
from backend.src.schemas.quality_inspection import (
    QualityInspectionBase,
    QualityInspectionCreate,
    QualityInspectionRead,
    QualityInspectionUpdate,
)

__all__ = [
    "ManufacturingOrderBase",
    "ManufacturingOrderCreate",
    "ManufacturingOrderRead",
    "ManufacturingOrderWithTasksRead",
    "ManufacturingOrderUpdate",
    "WorkCenterBase",
    "WorkCenterCreate",
    "WorkCenterRead",
    "WorkCenterUpdate",
    "ProductionTaskBase",
    "ProductionTaskRead",
    "ProductionTaskUpdate",
    "ManufacturingRouteBase",
    "ManufacturingRouteCreate",
    "ManufacturingRouteRead",
    "RouteOperationBase",
    "RouteOperationCreate",
    "RouteOperationRead",
    "GenealogyRecordBase",
    "GenealogyRecordCreate",
    "GenealogyRecordRead",
    "QualityInspectionBase",
    "QualityInspectionCreate",
    "QualityInspectionRead",
    "QualityInspectionUpdate",
]
