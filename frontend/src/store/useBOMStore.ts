/**
 * Zustand store для управления спецификациями (BOM)
 */

import { create } from 'zustand';
import { bomAPI } from '../services/api';
import type { BOM, BOMCreate } from '../services/types';
import type { ApiResponse } from '../types/api';

interface BOMStore {
  bomItems: BOM[];
  loading: boolean;
  error: string | null;
  fetchBOMByProduct: (productId: string) => Promise<void>;
  createBOM: (data: BOMCreate) => Promise<ApiResponse<BOM> | null>;
  deleteBOM: (id: string) => Promise<void>;
  explodeBOM: (productId: string, quantity: number) => Promise<ApiResponse<any> | null>;
}

export const useBOMStore = create<BOMStore>((set, get) => ({
  bomItems: [],
  loading: false,
  error: null,

  fetchBOMByProduct: async (productId) => {
    set({ loading: true, error: null });
    try {
      const response = await bomAPI.getByProduct(productId);
      if (response.success) {
        set({ bomItems: response.data, loading: false });
      } else {
        set({ error: response.error || 'Ошибка загрузки спецификации', loading: false });
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка загрузки спецификации', loading: false });
    }
  },

  createBOM: async (data) => {
    set({ error: null });
    try {
      const response = await bomAPI.create(data);
      if (response.success) {
        // Обновляем спецификацию для родительского продукта
        await get().fetchBOMByProduct(data.parent_product_id);
        return response;
      } else {
        set({ error: response.error || 'Ошибка создания строки спецификации' });
        return null;
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка создания строки спецификации' });
      return null;
    }
  },

  deleteBOM: async (id) => {
    set({ error: null });
    try {
      const parentProductId = get().bomItems.find((b) => b.id === id)?.parent_product_id;
      await bomAPI.delete(id);
      if (parentProductId) {
        await get().fetchBOMByProduct(parentProductId);
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка удаления строки спецификации' });
    }
  },

  explodeBOM: async (productId, quantity) => {
    set({ loading: true, error: null });
    try {
      const response = await bomAPI.explode(productId, quantity);
      if (response.success) {
        set({ loading: false });
        return response;
      } else {
        set({ error: response.error || 'Ошибка взрыва спецификации', loading: false });
        return null;
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка взрыва спецификации', loading: false });
      return null;
    }
  },
}));
