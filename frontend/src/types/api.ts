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
