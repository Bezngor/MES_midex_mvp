/**
 * Zustand store для управления расписанием и диспетчеризацией
 */

import { create } from 'zustand';
import { dispatchingAPI, tasksAPI } from '../services/api';
import type { Task, GanttData, WorkCenterLoad, ManufacturingOrder } from '../services/types';
import type { ApiResponse } from '../types/api';

interface ScheduleStore {
  tasks: Task[];
  ganttData: GanttData | null;
  loading: boolean;
  error: string | null;
  fetchSchedule: (horizonDays?: number, workCenterId?: string) => Promise<void>;
  fetchGanttData: (startDate: string, endDate: string) => Promise<void>;
  fetchWorkCenterLoad: (workCenterId: string, date: string) => Promise<ApiResponse<WorkCenterLoad> | null>;
  releaseOrder: (orderId: string, releaseDate?: string) => Promise<ApiResponse<{ order: ManufacturingOrder; tasks_created: number }> | null>;
  cancelRelease: (orderId: string) => Promise<ApiResponse<{ order: ManufacturingOrder }> | null>;
  dispatchTask: (taskId: string, workCenterId: string, scheduledStart: string) => Promise<ApiResponse<Task> | null>;
  fetchTasks: (params?: { status?: string; work_center_id?: string; order_id?: string }) => Promise<void>;
}

export const useScheduleStore = create<ScheduleStore>((set, get) => ({
  tasks: [],
  ganttData: null,
  loading: false,
  error: null,

  fetchSchedule: async (horizonDays = 7, workCenterId) => {
    set({ loading: true, error: null });
    try {
      const response = await dispatchingAPI.getSchedule(horizonDays, workCenterId);
      if (response.success) {
        set({ tasks: response.data, loading: false });
      } else {
        set({ error: response.error || 'Ошибка загрузки расписания', loading: false });
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка загрузки расписания', loading: false });
    }
  },

  fetchGanttData: async (startDate, endDate) => {
    set({ loading: true, error: null });
    try {
      const response = await dispatchingAPI.getGanttData(startDate, endDate);
      if (response.success) {
        set({ ganttData: response.data, loading: false });
      } else {
        set({ error: response.error || 'Ошибка загрузки данных для Gantt', loading: false });
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка загрузки данных для Gantt', loading: false });
    }
  },

  fetchWorkCenterLoad: async (workCenterId, date) => {
    set({ error: null });
    try {
      const response = await dispatchingAPI.getWorkCenterLoad(workCenterId, date);
      if (response.success) {
        return response;
      } else {
        set({ error: response.error || 'Ошибка загрузки загрузки рабочего центра' });
        return null;
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка загрузки загрузки рабочего центра' });
      return null;
    }
  },

  releaseOrder: async (orderId, releaseDate) => {
    set({ error: null });
    try {
      const response = await dispatchingAPI.releaseOrder(orderId, releaseDate);
      if (response.success) {
        await get().fetchSchedule();
        return response;
      } else {
        set({ error: response.error || 'Ошибка выпуска заказа' });
        return null;
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка выпуска заказа' });
      return null;
    }
  },

  cancelRelease: async (orderId) => {
    set({ error: null });
    try {
      const response = await dispatchingAPI.cancelRelease(orderId);
      if (response.success) {
        await get().fetchSchedule();
        return response;
      } else {
        set({ error: response.error || 'Ошибка отмены выпуска' });
        return null;
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка отмены выпуска' });
      return null;
    }
  },

  dispatchTask: async (taskId, workCenterId, scheduledStart) => {
    set({ error: null });
    try {
      const response = await dispatchingAPI.dispatchTask(taskId, workCenterId, scheduledStart);
      if (response.success) {
        // Обновляем расписание
        await get().fetchSchedule();
        return response;
      } else {
        set({ error: response.error || 'Ошибка диспетчеризации задачи' });
        return null;
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка диспетчеризации задачи' });
      return null;
    }
  },

  fetchTasks: async (params) => {
    set({ loading: true, error: null });
    try {
      const response = await tasksAPI.getAll(params);
      if (response.success) {
        set({ tasks: response.data, loading: false });
      } else {
        set({ error: response.error || 'Ошибка загрузки задач', loading: false });
      }
    } catch (error: any) {
      set({ error: error.message || 'Ошибка загрузки задач', loading: false });
    }
  },
}));
