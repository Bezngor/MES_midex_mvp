/**
 * API клиент для MES backend с использованием Axios
 */

import axios from 'axios';
import type {
  Product,
  ProductCreate,
  BOM,
  BOMCreate,
  Batch,
  BatchCreate,
  InventoryBalance,
  InventoryAdjustment,
  Task,
  GanttData,
  WorkCenterLoad,
  ManufacturingOrder,
  MRPConsolidation,
  MRPExplosion,
  NetRequirement,
} from './types';
import type {
  ApiResponse,
  ManufacturingOrderRead,
  ProductionTaskRead,
  DsizPlanningRequest,
  DsizPlanningResponse,
  DispatchRunRequest,
  DispatchPreviewResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Axios instance с interceptors
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (добавить auth token если нужно)
api.interceptors.request.use(
  (config) => {
    // const token = localStorage.getItem('token');
    // if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (обработка ошибок глобально)
api.interceptors.response.use(
  (response) => {
    // Backend возвращает { success: true, data: ... } или { success: false, error: ... }
    return response.data;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    const errorMessage = error.response?.data?.detail || error.response?.data?.error || error.message;
    return Promise.reject(new Error(errorMessage));
  }
);

// =====================
// Products API
// =====================
export const productsAPI = {
  getAll: async (): Promise<ApiResponse<Product[]>> => {
    return api.get('/products');
  },
  getById: async (id: string): Promise<ApiResponse<Product>> => {
    return api.get(`/products/${id}`);
  },
  create: async (data: ProductCreate): Promise<ApiResponse<Product>> => {
    return api.post('/products', data);
  },
  update: async (id: string, data: Partial<ProductCreate>): Promise<ApiResponse<Product>> => {
    return api.patch(`/products/${id}`, data);
  },
  delete: async (id: string): Promise<ApiResponse<void>> => {
    return api.delete(`/products/${id}`);
  },
};

// =====================
// BOM API
// =====================
export const bomAPI = {
  getAll: async (parentProductId?: string, childProductId?: string): Promise<ApiResponse<BOM[]>> => {
    const params: Record<string, string> = {};
    if (parentProductId) params.parent_product_id = parentProductId;
    if (childProductId) params.child_product_id = childProductId;
    return api.get('/bill-of-materials', { params });
  },
  getByProduct: async (productId: string): Promise<ApiResponse<BOM[]>> => {
    return api.get('/bill-of-materials', { params: { parent_product_id: productId } });
  },
  getById: async (id: string): Promise<ApiResponse<BOM>> => {
    return api.get(`/bill-of-materials/${id}`);
  },
  create: async (data: BOMCreate): Promise<ApiResponse<BOM>> => {
    return api.post('/bill-of-materials', data);
  },
  delete: async (id: string): Promise<ApiResponse<void>> => {
    return api.delete(`/bill-of-materials/${id}`);
  },
  explode: async (productId: string, quantity: number): Promise<ApiResponse<MRPExplosion>> => {
    return api.post('/mrp/explode-bom', { product_id: productId, quantity });
  },
};

// =====================
// Batches API
// =====================
export const batchesAPI = {
  getAll: async (status?: string): Promise<ApiResponse<Batch[]>> => {
    const params = status ? { status } : {};
    return api.get('/batches', { params });
  },
  getById: async (id: string): Promise<ApiResponse<Batch>> => {
    return api.get(`/batches/${id}`);
  },
  create: async (data: BatchCreate): Promise<ApiResponse<Batch>> => {
    return api.post('/batches', data);
  },
  start: async (id: string): Promise<ApiResponse<Batch>> => {
    return api.patch(`/batches/${id}/start`);
  },
  complete: async (id: string): Promise<ApiResponse<Batch>> => {
    return api.patch(`/batches/${id}/complete`);
  },
  updateStatus: async (id: string, status: string): Promise<ApiResponse<Batch>> => {
    // Используем start/complete endpoints или общий update
    if (status === 'IN_PROGRESS') {
      return api.patch(`/batches/${id}/start`);
    } else if (status === 'COMPLETED') {
      return api.patch(`/batches/${id}/complete`);
    }
    throw new Error(`Неподдерживаемый статус: ${status}`);
  },
};

// =====================
// Inventory API
// =====================
export const inventoryAPI = {
  getAll: async (productId?: string, location?: string, productStatus?: 'FINISHED' | 'SEMI_FINISHED'): Promise<ApiResponse<InventoryBalance[]>> => {
    const params: Record<string, string> = {};
    if (productId) params.product_id = productId;
    if (location) params.location = location;
    if (productStatus) params.product_status = productStatus;
    return api.get('/inventory', { params });
  },
  getByProduct: async (productId: string): Promise<ApiResponse<InventoryBalance[]>> => {
    return api.get('/inventory', { params: { product_id: productId } });
  },
  adjust: async (productId: string, adjustment: InventoryAdjustment): Promise<ApiResponse<InventoryBalance>> => {
    return api.patch(`/inventory/${productId}/adjust`, adjustment);
  },
};

// =====================
// Dispatching API
// =====================
export const dispatchingAPI = {
  releaseOrder: async (orderId: string, releaseDate?: string): Promise<ApiResponse<{ order: ManufacturingOrder; tasks_created: number }>> => {
    return api.post('/dispatching/release-order', { order_id: orderId, release_date: releaseDate });
  },
  dispatchTask: async (taskId: string, workCenterId: string, scheduledStart: string): Promise<ApiResponse<Task>> => {
    return api.post('/dispatching/dispatch-task', {
      task_id: taskId,
      work_center_id: workCenterId,
      scheduled_start: scheduledStart,
    });
  },
  getSchedule: async (horizonDays: number = 7, workCenterId?: string): Promise<ApiResponse<Task[]>> => {
    const params: Record<string, string | number> = { horizon_days: horizonDays };
    if (workCenterId) params.work_center_id = workCenterId;
    return api.get('/dispatching/schedule', { params });
  },
  getGanttData: async (startDate: string, endDate: string): Promise<ApiResponse<GanttData>> => {
    return api.get('/dispatching/gantt-data', {
      params: { start_date: startDate, end_date: endDate },
    });
  },
  getWorkCenterLoad: async (workCenterId: string, date: string): Promise<ApiResponse<WorkCenterLoad>> => {
    return api.get(`/dispatching/work-center-load/${workCenterId}`, { params: { date } });
  },
};

// =====================
// MRP API
// =====================
export const mrpAPI = {
  consolidateOrders: async (horizonDays: number = 30): Promise<ApiResponse<{ consolidated_orders: MRPConsolidation[]; total_products: number; total_orders: number }>> => {
    return api.post('/mrp/consolidate', { horizon_days: horizonDays });
  },
  explodeBOM: async (productId: string, quantity: number): Promise<ApiResponse<MRPExplosion>> => {
    return api.post('/mrp/explode-bom', { product_id: productId, quantity });
  },
  calculateNetRequirement: async (productId: string, grossRequirement: number): Promise<ApiResponse<NetRequirement>> => {
    return api.get(`/mrp/net-requirement/${productId}`, { params: { gross_requirement: grossRequirement } });
  },
  createBulkOrder: async (parentOrderId: string, bulkProductId: string, quantityKg: number, dueDate: string): Promise<ApiResponse<ManufacturingOrder>> => {
    return api.post('/mrp/create-bulk-order', {
      parent_order_id: parentOrderId,
      bulk_product_id: bulkProductId,
      quantity_kg: quantityKg,
      due_date: dueDate,
    });
  },
};

// =====================
// Manufacturing Orders API (legacy, для совместимости)
// =====================
export const ordersAPI = {
  getAll: async (params?: { status?: string; limit?: number; offset?: number }): Promise<ApiResponse<ManufacturingOrder[]>> => {
    return api.get('/manufacturing-orders', { params });
  },
  getById: async (orderId: string): Promise<ApiResponse<ManufacturingOrder>> => {
    return api.get(`/manufacturing-orders/${orderId}`);
  },
  create: async (data: {
    product_id: string;
    quantity: number;
    order_number: string;
    due_date: string;
    order_type?: 'CUSTOMER' | 'INTERNAL_BULK';
    status?: string;
    priority?: string;
  }): Promise<ApiResponse<ManufacturingOrder>> => {
    return api.post('/manufacturing-orders', data);
  },
};

// =====================
// Production Tasks API (legacy, для совместимости)
// =====================
export const tasksAPI = {
  getAll: async (params?: {
    status?: string;
    work_center_id?: string;
    order_id?: string;
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<Task[]>> => {
    return api.get('/production-tasks', { params });
  },
  getById: async (taskId: string): Promise<ApiResponse<Task>> => {
    return api.get(`/production-tasks/${taskId}`);
  },
};

// =====================
// Legacy named exports for backward compatibility
// =====================
export async function createManufacturingOrder(
  payload: {
    product_id: string;
    quantity: number;
    order_number: string;
    due_date: string;
  }
): Promise<ApiResponse<ManufacturingOrderRead>> {
  const result = await ordersAPI.create(payload);
  // Convert ManufacturingOrder to ManufacturingOrderRead format if needed
  return result as ApiResponse<ManufacturingOrderRead>;
}

export async function getManufacturingOrders(params?: {
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<ApiResponse<ManufacturingOrderRead[]>> {
  const result = await ordersAPI.getAll(params);
  // Convert ManufacturingOrder[] to ManufacturingOrderRead[] format if needed
  return result as ApiResponse<ManufacturingOrderRead[]>;
}

export async function getProductionTasks(params?: {
  status?: string;
  work_center_id?: string;
  order_id?: string;
  limit?: number;
  offset?: number;
}): Promise<ApiResponse<ProductionTaskRead[]>> {
  const result = await tasksAPI.getAll(params);
  // Convert Task[] to ProductionTaskRead[] format if needed
  return result as ApiResponse<ProductionTaskRead[]>;
}

// =====================
// DSIZ Planning API
// =====================
export const dsizPlanningAPI = {
  runPlanning: async (request: DsizPlanningRequest): Promise<ApiResponse<DsizPlanningResponse>> => {
    return api.post('/dsiz/planning/run', request);
  },
};

// =====================
// DSIZ Dispatching API
// =====================
export const dsizDispatchingAPI = {
  runDispatching: async (request: DispatchRunRequest): Promise<ApiResponse<DispatchPreviewResponse>> => {
    return api.post('/dsiz/dispatching/run', request);
  },
};

export default api;
