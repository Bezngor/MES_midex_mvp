"""
Pydantic-схемы / DTO для API.
"""

from backend.core.schemas.manufacturing_order import (
    ManufacturingOrderBase,
    ManufacturingOrderCreate,
    ManufacturingOrderRead,
    ManufacturingOrderWithTasksRead,
    ManufacturingOrderUpdate,
)
from backend.core.schemas.work_center import (
    WorkCenterBase,
    WorkCenterCreate,
    WorkCenterRead,
    WorkCenterUpdate,
)
from backend.core.schemas.production_task import (
    ProductionTaskBase,
    ProductionTaskRead,
    ProductionTaskUpdate,
    TaskStartPayload,
    TaskCompletePayload,
    TaskFailPayload,
)
from backend.core.schemas.manufacturing_route import (
    ManufacturingRouteBase,
    ManufacturingRouteCreate,
    ManufacturingRouteRead,
    ManufacturingRouteWithOperationsRead,
)
from backend.core.schemas.route_operation import (
    RouteOperationBase,
    RouteOperationCreate,
    RouteOperationRead,
    RouteOperationUpdate,
)
from backend.core.schemas.genealogy_record import (
    GenealogyRecordBase,
    GenealogyRecordCreate,
    GenealogyRecordRead,
)
from backend.core.schemas.quality_inspection import (
    QualityInspectionBase,
    QualityInspectionCreate,
    QualityInspectionRead,
    QualityInspectionUpdate,
)
from backend.core.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from backend.core.schemas.bom import BOMCreate, BOMResponse
from backend.core.schemas.batch import BatchCreate, BatchUpdate, BatchResponse
from backend.core.schemas.inventory import InventoryResponse, InventoryAdjust
from backend.core.schemas.work_center_capacity import CapacityCreate, CapacityResponse
from backend.core.schemas.mrp import (
    ConsolidateOrdersRequest,
    ConsolidateOrdersResponse,
    ExplodeBOMRequest,
    ExplodeBOMResponse,
    NetRequirementRequest,
    NetRequirementResponse,
    CreateBulkOrderRequest,
    CreateBulkOrderResponse,
)
from backend.core.schemas.dispatching import (
    ReleaseOrderRequest,
    ReleaseOrderResponse,
    DispatchTaskRequest,
    DispatchTaskResponse,
    ScheduleResponse,
    WorkCenterLoadResponse,
    GanttDataResponse,
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
    "ConsolidateOrdersRequest",
    "ConsolidateOrdersResponse",
    "ExplodeBOMRequest",
    "ExplodeBOMResponse",
    "NetRequirementRequest",
    "NetRequirementResponse",
    "CreateBulkOrderRequest",
    "CreateBulkOrderResponse",
    "ReleaseOrderRequest",
    "ReleaseOrderResponse",
    "DispatchTaskRequest",
    "DispatchTaskResponse",
    "ScheduleResponse",
    "WorkCenterLoadResponse",
    "GanttDataResponse",
]
