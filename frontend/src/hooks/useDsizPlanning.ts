/**
 * Hook для работы с DSIZ планированием
 */

import { useState, useCallback } from 'react';
import { dsizPlanningAPI } from '../services/api';
import type { ApiResponse, DsizPlanningRequest, DsizPlanningResponse } from '../types/api';

interface UseDsizPlanningReturn {
  planningData: DsizPlanningResponse | null;
  loading: boolean;
  error: string | null;
  runPlanning: (request: DsizPlanningRequest) => Promise<DsizPlanningResponse | null>;
  clearError: () => void;
}

export const useDsizPlanning = (): UseDsizPlanningReturn => {
  const [planningData, setPlanningData] = useState<DsizPlanningResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runPlanning = useCallback(async (request: DsizPlanningRequest): Promise<DsizPlanningResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await dsizPlanningAPI.runPlanning(request);
      const body = response as ApiResponse<DsizPlanningResponse> & DsizPlanningResponse;
      if (body.success !== true) {
        setError(body.error || 'Ошибка выполнения планирования');
        return null;
      }
      // Бэкенд возвращает план «плоским» объектом { success, plan_id, operations, ... }, без обёртки data
      const plan: DsizPlanningResponse = body.data ?? body;
      setPlanningData(plan);
      return plan;
    } catch (err: any) {
      const errorMsg = err.message || 'Неожиданная ошибка при выполнении планирования';
      setError(errorMsg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    planningData,
    loading,
    error,
    runPlanning,
    clearError,
  };
};
