/**
 * TypeScript интерфейсы для всех сущностей MES платформы
 */

export enum ProductType {
  RAW_MATERIAL = 'RAW_MATERIAL',
  BULK = 'BULK',
  PACKAGING = 'PACKAGING',
  FINISHED_GOOD = 'FINISHED_GOOD',
}

export enum BatchStatus {
  PLANNED = 'PLANNED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
}

export enum OrderStatus {
  PLANNED = 'PLANNED',
  RELEASED = 'RELEASED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  ON_HOLD = 'ON_HOLD',
  CANCELLED = 'CANCELLED',
  SHIP = 'SHIP',
  IN_WORK = 'IN_WORK',
}

export enum TaskStatus {
  QUEUED = 'QUEUED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED',
}

export enum WorkCenterStatus {
  AVAILABLE = 'AVAILABLE',
  BUSY = 'BUSY',
  MAINTENANCE = 'MAINTENANCE',
  DOWN = 'DOWN',
}

export interface Product {
  id: string;
  product_code: string;
  product_name: string;
  product_type: ProductType;
  unit_of_measure: string;
  min_batch_size_kg?: number;
  batch_size_step_kg?: number;
  shelf_life_days?: number;
  created_at: string;
  updated_at?: string;
}

export interface ProductCreate {
  product_code: string;
  product_name: string;
  product_type: ProductType;
  unit_of_measure: string;
  min_batch_size_kg?: number;
  batch_size_step_kg?: number;
  shelf_life_days?: number;
}

export interface BOM {
  id: string;
  parent_product_id: string;
  child_product_id: string;
  quantity: number;
  unit: string;
  parent_product?: Product;
  child_product?: Product;
}

export interface BOMCreate {
  parent_product_id: string;
  child_product_id: string;
  quantity: number;
  unit: string;
}

export interface Batch {
  id: string;
  batch_number: string;
  product_id: string;
  /** Наименование продукта (из API, для отображения в UI вместо UUID). */
  product_name?: string | null;
  quantity_kg: number;
  status: BatchStatus;
  work_center_id?: string;
  parent_order_id?: string;
  started_at?: string;
  completed_at?: string;
  product?: Product;
  created_at: string;
  updated_at?: string;
}

export interface BatchCreate {
  product_id: string;
  quantity_kg: number;
  work_center_id?: string;
  parent_order_id?: string;
}

export interface InventoryBalance {
  id: string;
  product_id: string;
  location: string;
  quantity: number;
  unit: string;
  product_status: 'FINISHED' | 'SEMI_FINISHED';
  production_date?: string;
  expiry_date?: string;
  reserved_quantity: number;
  available_quantity: number;
  product?: Product;
  created_at: string;
  updated_at?: string;
}

export interface InventoryAdjustment {
  quantity: number;
  reason: string;
}

export interface Task {
  id: string;
  order_id: string;
  operation_id: string;
  work_center_id?: string;
  status: TaskStatus;
  priority?: string;
  scheduled_start?: string;
  scheduled_end?: string;
  started_at?: string;
  completed_at?: string;
  duration_hours?: number;
  assigned_to?: string;
  created_at: string;
  updated_at?: string;
}

export interface GanttData {
  work_centers: {
    id: string;
    name: string;
    tasks: {
      id: string;
      name: string;
      start: string;
      end: string;
      priority: string;
      status: string;
      order_number?: string;
    }[];
  }[];
  start_date: string;
  end_date: string;
}

export interface WorkCenter {
  id: string;
  name: string;
  status: WorkCenterStatus;
  capacity_per_shift?: number;
  batch_capacity_kg?: number;
  cycles_per_shift?: number;
  parallel_capacity?: number;
  created_at: string;
  updated_at?: string;
}

export interface WorkCenterLoad {
  work_center_id: string;
  work_center_name: string;
  date: string;
  load_percentage: number;
  status: 'AVAILABLE' | 'BUSY' | 'OVERLOADED';
  tasks_count: number;
}

export interface ManufacturingOrder {
  id: string;
  order_number: string;
  product_id: string;
  quantity: number;
  status: OrderStatus;
  order_type?: 'CUSTOMER' | 'INTERNAL_BULK';
  priority?: 'URGENT' | 'HIGH' | 'NORMAL' | 'LOW';
  due_date: string;
  parent_order_id?: string;
  created_at: string;
  updated_at?: string;
}

export interface MRPConsolidation {
  product_id: string;
  total_quantity: number;
  priority: string;
  earliest_due_date: string;
  source_orders: string[];
}

export interface MRPExplosion {
  requirements: Record<string, { quantity: number; unit: string }>;
}

export interface NetRequirement {
  product_id: string;
  gross_requirement: number;
  available_quantity: number;
  net_requirement: number;
  unit: string;
}
