/**
 * Компонент списка батчей
 */

import React, { useEffect, useState } from 'react';
import { useBatchStore } from '../../store/useBatchStore';
import { BatchStatus } from '../../services/types';
import { Loading } from '../common/Loading';
import { Error } from '../common/Error';
import { BatchCard } from './BatchCard';

export const BatchList: React.FC = () => {
  const { batches, loading, error, fetchBatches } = useBatchStore();
  const [statusFilter, setStatusFilter] = useState<BatchStatus | ''>('');

  useEffect(() => {
    fetchBatches(statusFilter || undefined);
  }, [statusFilter, fetchBatches]);

  if (loading) return <Loading message="Загрузка батчей..." />;
  if (error) return <Error message={error} onRetry={() => fetchBatches(statusFilter || undefined)} />;

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Производственные партии</h2>
        <select
          className="border rounded px-3 py-2"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as BatchStatus)}
        >
          <option value="">Все статусы</option>
          {Object.values(BatchStatus).map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {batches.length === 0 ? (
          <div className="col-span-full text-center text-gray-500 py-8">
            Батчи не найдены
          </div>
        ) : (
          batches.map((batch) => (
            <BatchCard key={batch.id} batch={batch} />
          ))
        )}
      </div>
    </div>
  );
};
