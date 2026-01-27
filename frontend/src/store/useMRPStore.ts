/**
 * Zustand store для управления MRP (Material Requirements Planning)
 */

import { create } from 'zustand';
import { mrpAPI } from '../services/api';
import type { MRPConsolidation, MRPExplosion, NetRequirement, ManufacturingOrder } from '../services/types';
import type { ApiResponse } from '../types/api';

interface MRPStore {
  consolidatedOrders: MRPConsolidation[];
  explosionResult: MRPExplosion | null;
  netRequirement: NetRequirement | null;
  loading: boolean;
  error: string | null;
  consolidateOrders: (horizonDays?: number) => Promise<void>;
  explodeBOM: (productId: string, quantity: number) => Promise<void>;
  calculateNetRequirement: (productId: string, grossRequirement: number) => Promise<void>;
  createBulkOrder: (parentOrderId: string, bulkProductId: string, quantityKg: number, dueDate: string) => Promise<ApiResponse<ManufacturingOrder> | null>;
}

export const useMRPStore = create<MRPStore>((set) => ({
  consolidatedOrders: [],
  explosionResult: null,
  netRequirement: null,
  loading: false,
  error: null,

  consolidateOrders: async (horizonDays = 30) => {
    set({ loading: true, error: null });
    try {
      const response = await mrpAPI.consolidateOrders(horizonDays);
      if (response.success) {
        set({ consolidatedOrders: response.data.consolidated_orders, loading: false });
      } else {
        set({ error: response.error || 'Ошибка консолидации заказов', loading: false });
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка консолидации заказов', loading: false });
    }
  },

  explodeBOM: async (productId, quantity) => {
    set({ loading: true, error: null });
    try {
      const response = await mrpAPI.explodeBOM(productId, quantity);
      if (response.success) {
        set({ explosionResult: response.data, loading: false });
      } else {
        set({ error: response.error || 'Ошибка взрыва спецификации', loading: false });
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка взрыва спецификации', loading: false });
    }
  },

  calculateNetRequirement: async (productId, grossRequirement) => {
    set({ loading: true, error: null });
    try {
      const response = await mrpAPI.calculateNetRequirement(productId, grossRequirement);
      if (response.success) {
        set({ netRequirement: response.data, loading: false });
      } else {
        set({ error: response.error || 'Ошибка расчёта нетто-потребности', loading: false });
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка расчёта нетто-потребности', loading: false });
    }
  },

  createBulkOrder: async (parentOrderId, bulkProductId, quantityKg, dueDate) => {
    set({ error: null });
    try {
      const response = await mrpAPI.createBulkOrder(parentOrderId, bulkProductId, quantityKg, dueDate);
      if (response.success) {
        return response;
      } else {
        set({ error: response.error || 'Ошибка создания заказа на варку' });
        return null;
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка создания заказа на варку' });
      return null;
    }
  },
}));
