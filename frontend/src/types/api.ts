/**
 * API response envelope type matching backend format.
 */
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}

/**
 * Manufacturing Order types matching backend schemas.
 */
export type OrderStatus = 
  | "PLANNED"
  | "RELEASED"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "ON_HOLD"
  | "CANCELLED"
  | "SHIP"
  | "IN_WORK";

export interface ManufacturingOrderRead {
  id: string;
  order_number: string;
  product_id: string;
  quantity: number;
  status: OrderStatus;
  due_date: string;
  created_at: string;
  updated_at: string;
}

export interface ManufacturingOrderCreate {
  product_id: string;
  quantity: number;
  order_number: string;
  due_date: string;
}

/**
 * Production Task types matching backend schemas.
 */
export type TaskStatus = 
  | "QUEUED"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED";

export interface ProductionTaskRead {
  id: string;
  order_id: string;
  operation_id: string;
  work_center_id: string;
  status: TaskStatus;
  assigned_to: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * DSIZ Planning types
 */
export interface ManualBlock {
  work_center_id: string;
  shift_date: string;
  shift_num: 1 | 2;
  reason?: string;
}

export interface DsizPlanningRequest {
  planning_date: string;
  horizon_days?: number;
  manual_blocks?: ManualBlock[];
  workforce_state?: Record<string, Record<string, number>>;
}

export interface PlanningOperation {
  bulk_product_sku: string;
  quantity_kg: number;
  mode: string;
  shift_date: string;
  shift_num: 1 | 2;
  reactor_slot: 1 | 2;
}

export interface PlanningWarning {
  level: 'WARNING' | 'ERROR';
  message: string;
  context?: Record<string, any>;
}

export interface DsizPlanningResponse {
  success: boolean;
  plan_id: string;
  planning_date: string;
  horizon_days: number;
  operations: PlanningOperation[];
  warnings: PlanningWarning[];
  summary: Record<string, any>;
}

/**
 * DSIZ Dispatching types
 */
export interface DispatchRunRequest {
  manufacturing_order_ids: string[];
  work_center_id?: string;
}

export interface GanttTaskPreview {
  task_id: string;
  order_id: string;
  work_center_id: string;
  work_center_name: string;
  task_start: string;
  task_end: string;
  duration_hours: number;
  changeover_minutes: number;
  status: string;
  priority: string;
}

export interface ConflictInfo {
  task_id: string;
  conflict_with: string;
  work_center_id: string;
  overlap_start: string;
  overlap_end: string;
}

export interface DispatchPreviewResponse {
  success: boolean;
  data: {
    gantt_preview: GanttTaskPreview[];
    conflicts: ConflictInfo[];
  };
}

/**
 * Order Changes types for identifying new/changed orders
 */
export interface OrderChangeInfo {
  order_id?: string | null; // Может быть null для удалённых заказов
  order_number: string;
  product_id: string;
  product_name?: string | null;
  quantity?: number | null; // Количество ГП в заказе
  due_date?: string | null; // Дата выполнения заказа (ISO string)
  priority?: 'URGENT' | 'HIGH' | 'NORMAL' | 'LOW' | null; // Приоритет заказа
  is_new: boolean;
  is_changed: boolean;
  is_deleted?: boolean; // Новое поле для удалённых заказов
  last_snapshot_date?: string | null;
  current_updated_at?: string | null;
  changes?: Record<string, [any, any]> | null; // {field: [old_value, new_value]}
}

export interface OrderChangesListResponse {
  success: boolean;
  new_orders: OrderChangeInfo[];
  changed_orders: OrderChangeInfo[];
  deleted_orders: OrderChangeInfo[]; // Новое поле для удалённых заказов
  total_new: number;
  total_changed: number;
  total_deleted: number; // Новое поле
}

export interface OrderChangeDetailResponse {
  success: boolean;
  data: OrderChangeInfo | null;
}
