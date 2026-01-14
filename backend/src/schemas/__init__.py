"""
Pydantic-схемы / DTO для API.
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
    TaskStartPayload,
    TaskCompletePayload,
    TaskFailPayload,
)
from backend.src.schemas.manufacturing_route import (
    ManufacturingRouteBase,
    ManufacturingRouteCreate,
    ManufacturingRouteRead,
    ManufacturingRouteWithOperationsRead,
)
from backend.src.schemas.route_operation import (
    RouteOperationBase,
    RouteOperationCreate,
    RouteOperationRead,
    RouteOperationUpdate,
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
from backend.src.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from backend.src.schemas.bom import BOMCreate, BOMResponse
from backend.src.schemas.batch import BatchCreate, BatchUpdate, BatchResponse
from backend.src.schemas.inventory import InventoryResponse, InventoryAdjust
from backend.src.schemas.work_center_capacity import CapacityCreate, CapacityResponse

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
    "TaskStartPayload",
    "TaskCompletePayload",
    "TaskFailPayload",
    "ManufacturingRouteBase",
    "ManufacturingRouteCreate",
    "ManufacturingRouteRead",
    "ManufacturingRouteWithOperationsRead",
    "RouteOperationBase",
    "RouteOperationCreate",
    "RouteOperationRead",
    "RouteOperationUpdate",
    "GenealogyRecordBase",
    "GenealogyRecordCreate",
    "GenealogyRecordRead",
    "QualityInspectionBase",
    "QualityInspectionCreate",
    "QualityInspectionRead",
    "QualityInspectionUpdate",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "BOMCreate",
    "BOMResponse",
    "BatchCreate",
    "BatchUpdate",
    "BatchResponse",
    "InventoryResponse",
    "InventoryAdjust",
    "CapacityCreate",
    "CapacityResponse",
]
