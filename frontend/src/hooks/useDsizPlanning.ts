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
      const response: ApiResponse<DsizPlanningResponse> = await dsizPlanningAPI.runPlanning(request);
      if (response.success) {
        setPlanningData(response.data);
        return response.data;
      } else {
        const errorMsg = response.error || 'Ошибка выполнения планирования';
        setError(errorMsg);
        return null;
      }
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
