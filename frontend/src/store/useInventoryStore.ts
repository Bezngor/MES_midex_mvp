/**
 * Zustand store для управления остатками на складе
 */

import { create } from 'zustand';
import { inventoryAPI } from '../services/api';
import type { InventoryBalance, InventoryAdjustment } from '../services/types';
import type { ApiResponse } from '../types/api';

interface InventoryStore {
  inventory: InventoryBalance[];
  loading: boolean;
  error: string | null;
  fetchInventory: (productId?: string, location?: string, productStatus?: 'FINISHED' | 'SEMI_FINISHED') => Promise<void>;
  adjustInventory: (productId: string, adjustment: InventoryAdjustment) => Promise<ApiResponse<InventoryBalance> | null>;
  getInventoryByProduct: (productId: string) => InventoryBalance[];
}

export const useInventoryStore = create<InventoryStore>((set, get) => ({
  inventory: [],
  loading: false,
  error: null,

  fetchInventory: async (productId, location, productStatus) => {
    set({ loading: true, error: null });
    try {
      const response = await inventoryAPI.getAll(productId, location, productStatus);
      if (response.success) {
        set({ inventory: response.data, loading: false });
      } else {
        set({ error: response.error || 'Ошибка загрузки остатков', loading: false });
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка загрузки остатков', loading: false });
    }
  },

  adjustInventory: async (productId, adjustment) => {
    set({ error: null });
    try {
      const response = await inventoryAPI.adjust(productId, adjustment);
      if (response.success) {
        await get().fetchInventory();
        return response;
      } else {
        set({ error: response.error || 'Ошибка корректировки остатков' });
        return null;
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка корректировки остатков' });
      return null;
    }
  },

  getInventoryByProduct: (productId) => {
    return get().inventory.filter((item) => item.product_id === productId);
  },
}));
