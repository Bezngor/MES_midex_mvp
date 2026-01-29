/**
 * Компонент карточки батча
 */

import React from 'react';
import { useBatchStore } from '../../store/useBatchStore';
import { useProductStore } from '../../store/useProductStore';
import { Batch, BatchStatus } from '../../services/types';
import { Button } from '../common/Button';

interface BatchCardProps {
  batch: Batch;
}

export const BatchCard: React.FC<BatchCardProps> = ({ batch }) => {
  const { startBatch, completeBatch } = useBatchStore();
  const { getProductById } = useProductStore();
  const product = getProductById(batch.product_id);

  const getStatusColor = (status: BatchStatus) => {
    switch (status) {
      case BatchStatus.PLANNED:
        return 'bg-gray-100 text-gray-800';
      case BatchStatus.IN_PROGRESS:
        return 'bg-blue-100 text-blue-800';
      case BatchStatus.COMPLETED:
        return 'bg-green-100 text-green-800';
      case BatchStatus.FAILED:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="border rounded-lg p-4 bg-white shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-semibold text-lg">{batch.batch_number}</h3>
          <p className="text-sm text-gray-600">{batch.product_name ?? product?.product_name ?? batch.product_id}</p>
        </div>
        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(batch.status)}`}>
          {batch.status}
        </span>
      </div>

      <div className="space-y-1 text-sm">
        <p><span className="font-medium">Количество:</span> {batch.quantity_kg} кг</p>
        {batch.started_at && (
          <p><span className="font-medium">Начало:</span> {new Date(batch.started_at).toLocaleString('ru-RU')}</p>
        )}
        {batch.completed_at && (
          <p><span className="font-medium">Завершение:</span> {new Date(batch.completed_at).toLocaleString('ru-RU')}</p>
        )}
      </div>

      <div className="mt-4 flex gap-2">
        {batch.status === BatchStatus.PLANNED && (
          <Button
            variant="primary"
            size="sm"
            onClick={() => startBatch(batch.id)}
          >
            Запустить
          </Button>
        )}
        {batch.status === BatchStatus.IN_PROGRESS && (
          <Button
            variant="success"
            size="sm"
            onClick={() => completeBatch(batch.id)}
          >
            Завершить
          </Button>
        )}
      </div>
    </div>
  );
};
