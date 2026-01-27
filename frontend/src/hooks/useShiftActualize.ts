/**
 * Hook для работы с фактизацией смен DSIZ
 */

import { useState, useCallback } from 'react';
import { dsizDispatchingAPI } from '../services/api';
import type { ApiResponse, DispatchRunRequest, DispatchPreviewResponse } from '../types/api';

interface UseShiftActualizeReturn {
  dispatchData: DispatchPreviewResponse | null;
  loading: boolean;
  error: string | null;
  runDispatching: (request: DispatchRunRequest) => Promise<DispatchPreviewResponse | null>;
  clearError: () => void;
}

export const useShiftActualize = (): UseShiftActualizeReturn => {
  const [dispatchData, setDispatchData] = useState<DispatchPreviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runDispatching = useCallback(async (request: DispatchRunRequest): Promise<DispatchPreviewResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      const response: ApiResponse<DispatchPreviewResponse> = await dsizDispatchingAPI.runDispatching(request);
      if (response.success) {
        setDispatchData(response.data);
        return response.data;
      } else {
        const errorMsg = response.error || 'Ошибка выполнения диспетчеризации';
        setError(errorMsg);
        return null;
      }
    } catch (err: any) {
      const errorMsg = err.message || 'Неожиданная ошибка при выполнении диспетчеризации';
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
    dispatchData,
    loading,
    error,
    runDispatching,
    clearError,
  };
};
