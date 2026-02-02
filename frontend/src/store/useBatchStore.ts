/**
 * Zustand store для управления батчами
 */

import { create } from 'zustand';
import { batchesAPI } from '../services/api';
import type { Batch, BatchCreate, BatchUpdate } from '../services/types';
import type { ApiResponse } from '../types/api';

interface BatchStore {
  batches: Batch[];
  loading: boolean;
  error: string | null;
  fetchBatches: (status?: string) => Promise<void>;
  createBatch: (data: BatchCreate) => Promise<ApiResponse<Batch> | null>;
  updateBatch: (id: string, data: BatchUpdate) => Promise<ApiResponse<Batch> | null>;
  postBatchToInventory: (id: string) => Promise<ApiResponse<Batch> | null>;
  undoPostBatchToInventory: (id: string) => Promise<ApiResponse<Batch> | null>;
  startBatch: (id: string) => Promise<void>;
  completeBatch: (id: string) => Promise<void>;
  getBatchById: (id: string) => Batch | undefined;
}

export const useBatchStore = create<BatchStore>((set, get) => ({
  batches: [],
  loading: false,
  error: null,

  fetchBatches: async (status) => {
    set({ loading: true, error: null });
    try {
      const response = await batchesAPI.getAll(status);
      if (response.success) {
        set({ batches: response.data, loading: false });
      } else {
        set({ error: response.error || 'Ошибка загрузки батчей', loading: false });
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка загрузки батчей', loading: false });
    }
  },

  createBatch: async (data) => {
    set({ error: null });
    try {
      const response = await batchesAPI.create(data);
      if (response.success) {
        await get().fetchBatches();
        return response;
      } else {
        set({ error: response.error || 'Ошибка создания батча' });
        return null;
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка создания батча' });
      return null;
    }
  },

  updateBatch: async (id, data) => {
    set({ error: null });
    try {
      const response = await batchesAPI.update(id, data);
      if (response.success) {
        await get().fetchBatches();
        return response;
      } else {
        set({ error: response.error || 'Ошибка корректировки батча' });
        return null;
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка корректировки батча' });
      return null;
    }
  },

  postBatchToInventory: async (id) => {
    set({ error: null });
    try {
      const response = await batchesAPI.postToInventory(id);
      if (response.success) {
        await get().fetchBatches();
        return response;
      } else {
        set({ error: response.error || 'Ошибка учёта в остатках' });
        return null;
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка учёта в остатках' });
      return null;
    }
  },

  undoPostBatchToInventory: async (id) => {
    set({ error: null });
    try {
      const response = await batchesAPI.undoPostToInventory(id);
      if (response.success) {
        await get().fetchBatches();
        return response;
      } else {
        set({ error: response.error || 'Ошибка отмены учёта в остатках' });
        return null;
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка отмены учёта в остатках' });
      return null;
    }
  },

  startBatch: async (id) => {
    set({ error: null });
    try {
      await batchesAPI.start(id);
      await get().fetchBatches();
    } catch (error: any) {
      set({ error: error.message || 'Ошибка запуска батча' });
    }
  },

  completeBatch: async (id) => {
    set({ error: null });
    try {
      await batchesAPI.complete(id);
      await get().fetchBatches();
    } catch (error: any) {
      set({ error: error.message || 'Ошибка завершения батча' });
    }
  },

  getBatchById: (id) => {
    return get().batches.find((b) => b.id === id);
  },
}));
