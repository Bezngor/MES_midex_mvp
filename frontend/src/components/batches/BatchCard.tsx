/**
 * Компонент карточки батча
 */

import React, { useState } from 'react';
import { useBatchStore } from '../../store/useBatchStore';
import { useProductStore } from '../../store/useProductStore';
import { Batch, BatchStatus } from '../../services/types';
import { Button } from '../common/Button';
import { Modal } from '../common/Modal';

function toDateTimeLocal(iso: string | undefined): string {
  if (!iso) return '';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  return d.toISOString().slice(0, 16);
}

interface BatchCardProps {
  batch: Batch;
}

export const BatchCard: React.FC<BatchCardProps> = ({ batch }) => {
  const { startBatch, completeBatch, updateBatch, postBatchToInventory, undoPostBatchToInventory } = useBatchStore();
  const [isPostingToInventory, setIsPostingToInventory] = useState(false);
  const [isUndoingToInventory, setIsUndoingToInventory] = useState(false);
  const isPostedToInventory = batch.posted_to_inventory_at != null;
  const { getProductById } = useProductStore();
  const product = getProductById(batch.product_id);

  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editQuantityKg, setEditQuantityKg] = useState<string>(String(batch.quantity_kg));
  const [editStatus, setEditStatus] = useState<BatchStatus>(batch.status as BatchStatus);
  const [editOperatorId, setEditOperatorId] = useState(batch.operator_id ?? '');
  const [editPlannedStart, setEditPlannedStart] = useState(toDateTimeLocal(batch.planned_start));
  const [editStartedAt, setEditStartedAt] = useState(toDateTimeLocal(batch.started_at));
  const [editCompletedAt, setEditCompletedAt] = useState(toDateTimeLocal(batch.completed_at));
  const [editError, setEditError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const minBatchKg = product?.min_batch_size_kg;
  const quantityNum = parseFloat(editQuantityKg);
  const quantityValid = !Number.isNaN(quantityNum) && quantityNum > 0;
  const quantityBelowMin = minBatchKg != null && quantityValid && quantityNum < minBatchKg;
  const quantityError = quantityBelowMin
    ? `Количество не может быть меньше минимального размера партии (${minBatchKg} кг)`
    : null;

  const openEdit = () => {
    setEditQuantityKg(String(batch.quantity_kg));
    setEditStatus(batch.status as BatchStatus);
    setEditOperatorId(batch.operator_id ?? '');
    setEditPlannedStart(toDateTimeLocal(batch.planned_start));
    setEditStartedAt(toDateTimeLocal(batch.started_at));
    setEditCompletedAt(toDateTimeLocal(batch.completed_at));
    setEditError(null);
    setIsEditOpen(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (quantityError || !quantityValid) return;
    setIsSubmitting(true);
    setEditError(null);
    const payload = {
      quantity_kg: quantityNum,
      status: editStatus,
      operator_id: editOperatorId.trim() || undefined,
      planned_start: editPlannedStart ? new Date(editPlannedStart).toISOString() : undefined,
      started_at: editStartedAt ? new Date(editStartedAt).toISOString() : undefined,
      completed_at: editCompletedAt ? new Date(editCompletedAt).toISOString() : undefined,
    };
    try {
      const response = await updateBatch(batch.id, payload);
      if (response?.success) {
        setIsEditOpen(false);
      } else {
        setEditError(response?.error ?? 'Ошибка сохранения');
      }
    } catch (err: any) {
      setEditError(err.message ?? 'Ошибка сохранения');
    } finally {
      setIsSubmitting(false);
    }
  };

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
    <>
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

      <div className="mt-4 flex flex-wrap gap-2">
        <Button variant="secondary" size="sm" onClick={openEdit}>
          Корректировать
        </Button>
        {batch.status === BatchStatus.PLANNED && (
          <Button variant="primary" size="sm" onClick={() => startBatch(batch.id)}>
            Запустить
          </Button>
        )}
        {batch.status === BatchStatus.IN_PROGRESS && (
          <Button variant="success" size="sm" onClick={() => completeBatch(batch.id)}>
            Завершить
          </Button>
        )}
        {batch.status === BatchStatus.COMPLETED && !isPostedToInventory && (
          <Button
            variant="secondary"
            size="sm"
            isLoading={isPostingToInventory}
            disabled={isPostingToInventory}
            onClick={async () => {
              setIsPostingToInventory(true);
              await postBatchToInventory(batch.id);
              setIsPostingToInventory(false);
            }}
            title="Добавить количество партии в остатки"
          >
            Учесть в остатках
          </Button>
        )}
        {batch.status === BatchStatus.COMPLETED && isPostedToInventory && (
          <Button
            variant="danger"
            size="sm"
            isLoading={isUndoingToInventory}
            disabled={isUndoingToInventory}
            onClick={async () => {
              setIsUndoingToInventory(true);
              await undoPostBatchToInventory(batch.id);
              setIsUndoingToInventory(false);
            }}
            title="Вычесть количество партии из остатков"
          >
            Отменить учёт в остатках
          </Button>
        )}
      </div>
    </div>

    <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Корректировка партии" size="md">
      <form onSubmit={handleEditSubmit} className="space-y-4">
        {editError && (
          <div className="text-red-600 text-sm bg-red-50 p-2 rounded" role="alert">
            {editError}
          </div>
        )}
        <div>
          <label className="block text-sm font-medium mb-1">
            Количество (кг) *
            {minBatchKg != null && (
              <span className="text-gray-500 font-normal ml-1">мин. {minBatchKg} кг</span>
            )}
          </label>
          <input
            type="number"
            step="0.01"
            min={minBatchKg ?? 0}
            className={`w-full border rounded px-2 py-1 ${quantityError ? 'border-red-500' : ''}`}
            value={editQuantityKg}
            onChange={(e) => setEditQuantityKg(e.target.value)}
            required
          />
          {quantityError && (
            <p className="text-red-600 text-sm mt-1" role="alert">
              {quantityError}
            </p>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Статус</label>
          <select
            className="w-full border rounded px-2 py-1"
            value={editStatus}
            onChange={(e) => setEditStatus(e.target.value as BatchStatus)}
          >
            {Object.values(BatchStatus).map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Оператор</label>
          <input
            type="text"
            className="w-full border rounded px-2 py-1"
            value={editOperatorId}
            onChange={(e) => setEditOperatorId(e.target.value)}
            placeholder="Идентификатор оператора"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Плановое время старта</label>
          <input
            type="datetime-local"
            className="w-full border rounded px-2 py-1"
            value={editPlannedStart}
            onChange={(e) => setEditPlannedStart(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Фактическое время начала</label>
          <input
            type="datetime-local"
            className="w-full border rounded px-2 py-1"
            value={editStartedAt}
            onChange={(e) => setEditStartedAt(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Фактическое время завершения</label>
          <input
            type="datetime-local"
            className="w-full border rounded px-2 py-1"
            value={editCompletedAt}
            onChange={(e) => setEditCompletedAt(e.target.value)}
          />
        </div>
        <div className="flex gap-2 justify-end">
          <Button type="button" variant="secondary" onClick={() => setIsEditOpen(false)}>
            Отмена
          </Button>
          <Button type="submit" isLoading={isSubmitting} disabled={!!quantityError || !quantityValid}>
            Сохранить
          </Button>
        </div>
      </form>
    </Modal>
  </>
  );
};
