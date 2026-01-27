/**
 * Zustand store для управления продуктами
 */

import { create } from 'zustand';
import { productsAPI } from '../services/api';
import type { Product, ProductCreate } from '../services/types';
import type { ApiResponse } from '../types/api';

interface ProductStore {
  products: Product[];
  loading: boolean;
  error: string | null;
  fetchProducts: () => Promise<void>;
  createProduct: (data: ProductCreate) => Promise<ApiResponse<Product> | null>;
  updateProduct: (id: string, data: Partial<ProductCreate>) => Promise<ApiResponse<Product> | null>;
  deleteProduct: (id: string) => Promise<void>;
  getProductById: (id: string) => Product | undefined;
}

export const useProductStore = create<ProductStore>((set, get) => ({
  products: [],
  loading: false,
  error: null,

  fetchProducts: async () => {
    set({ loading: true, error: null });
    try {
      const response = await productsAPI.getAll();
      if (response.success) {
        set({ products: response.data, loading: false });
      } else {
        set({ error: response.error || 'Ошибка загрузки продуктов', loading: false });
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка загрузки продуктов', loading: false });
    }
  },

  createProduct: async (data) => {
    set({ error: null });
    try {
      const response = await productsAPI.create(data);
      if (response.success) {
        // Обновляем список продуктов
        await get().fetchProducts();
        return response;
      } else {
        set({ error: response.error || 'Ошибка создания продукта' });
        return null;
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка создания продукта' });
      return null;
    }
  },

  updateProduct: async (id, data) => {
    set({ error: null });
    try {
      const response = await productsAPI.update(id, data);
      if (response.success) {
        // Обновляем список продуктов
        await get().fetchProducts();
        return response;
      } else {
        set({ error: response.error || 'Ошибка обновления продукта' });
        return null;
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка обновления продукта' });
      return null;
    }
  },

  deleteProduct: async (id) => {
    set({ error: null });
    try {
      await productsAPI.delete(id);
      // Обновляем список продуктов
      set((state) => ({
        products: state.products.filter((p) => p.id !== id),
      }));
    } catch (error: any) {
      set({ error: error.message || 'Ошибка удаления продукта' });
    }
  },

  getProductById: (id) => {
    return get().products.find((p) => p.id === id);
  },
}));
