/**
 * API client for MES backend.
 */

import type {
  ApiResponse,
  ManufacturingOrderRead,
  ManufacturingOrderCreate,
  ProductionTaskRead,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

/**
 * Fetch wrapper that handles API response envelope.
 */
async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        data: data as T,
        error: data.detail || `HTTP ${response.status}: ${response.statusText}`,
      };
    }

    return data as ApiResponse<T>;
  } catch (error) {
    return {
      success: false,
      data: null as T,
      error: error instanceof Error ? error.message : "Network error occurred",
    };
  }
}

/**
 * Manufacturing Orders API
 */

export async function createManufacturingOrder(
  payload: {
    product_id: string;
    quantity: number;
    order_number: string;
    due_date: string;
  }
): Promise<ApiResponse<ManufacturingOrderRead>> {
  return fetchApi<ManufacturingOrderRead>("/manufacturing-orders", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getManufacturingOrders(params?: {
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<ApiResponse<ManufacturingOrderRead[]>> {
  const queryParams = new URLSearchParams();
  if (params?.status) queryParams.append("status", params.status);
  if (params?.limit) queryParams.append("limit", params.limit.toString());
  if (params?.offset) queryParams.append("offset", params.offset.toString());

  const endpoint = queryParams.toString()
    ? `/manufacturing-orders?${queryParams.toString()}`
    : "/manufacturing-orders";

  return fetchApi<ManufacturingOrderRead[]>(endpoint);
}

export async function getManufacturingOrder(
  orderId: string
): Promise<ApiResponse<ManufacturingOrderRead>> {
  return fetchApi<ManufacturingOrderRead>(`/manufacturing-orders/${orderId}`);
}

/**
 * Production Tasks API
 */

export async function getProductionTasks(params?: {
  status?: string;
  work_center_id?: string;
  order_id?: string;
  limit?: number;
  offset?: number;
}): Promise<ApiResponse<ProductionTaskRead[]>> {
  const queryParams = new URLSearchParams();
  if (params?.status) queryParams.append("status", params.status);
  if (params?.work_center_id) queryParams.append("work_center_id", params.work_center_id);
  if (params?.order_id) queryParams.append("order_id", params.order_id);
  if (params?.limit) queryParams.append("limit", params.limit.toString());
  if (params?.offset) queryParams.append("offset", params.offset.toString());

  const endpoint = queryParams.toString()
    ? `/production-tasks?${queryParams.toString()}`
    : "/production-tasks";

  return fetchApi<ProductionTaskRead[]>(endpoint);
}

export async function getProductionTask(
  taskId: string
): Promise<ApiResponse<ProductionTaskRead>> {
  return fetchApi<ProductionTaskRead>(`/production-tasks/${taskId}`);
}
