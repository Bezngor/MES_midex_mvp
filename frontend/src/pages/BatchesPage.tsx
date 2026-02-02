/**
 * Страница управления батчами
 */

import React, { useState } from 'react';
import { BatchList } from '../components/batches/BatchList';
import { useBatchStore } from '../store/useBatchStore';
import { BatchCreate, BatchStatus } from '../services/types';
import { Modal } from '../components/common/Modal';
import { Button } from '../components/common/Button';
import { useProductStore } from '../store/useProductStore';

export const BatchesPage: React.FC = () => {
  const { createBatch } = useBatchStore();
  const { products, fetchProducts } = useProductStore();

  React.useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const initialFormData: BatchCreate = {
    product_id: '',
    quantity_kg: 0,
    status: BatchStatus.PLANNED,
    operator_id: '',
    planned_start: '',
  };
  const [formData, setFormData] = useState<BatchCreate>(initialFormData);

  const bulkProducts = products.filter((p) => p.product_type === 'BULK');
  const selectedProduct = formData.product_id
    ? bulkProducts.find((p) => p.id === formData.product_id)
    : null;
  const minBatchKg = selectedProduct?.min_batch_size_kg;
  const quantityError =
    minBatchKg != null && formData.quantity_kg < minBatchKg
      ? `Количество не может быть меньше минимального размера партии (${minBatchKg} кг)`
      : null;

  const handleProductChange = (productId: string) => {
    const product = bulkProducts.find((p) => p.id === productId);
    const defaultQty = product?.min_batch_size_kg ?? 1;
    setFormData((prev) => ({
      ...prev,
      product_id: productId,
      quantity_kg: defaultQty,
    }));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (quantityError) return;
    setIsSubmitting(true);
    setError(null);

    const payload: BatchCreate = {
      product_id: formData.product_id,
      quantity_kg: formData.quantity_kg,
      status: formData.status,
      operator_id: formData.operator_id?.trim() || undefined,
      planned_start: formData.planned_start ? new Date(formData.planned_start).toISOString() : undefined,
    };
    try {
      const response = await createBatch(payload);
      if (response?.success) {
        setIsFormOpen(false);
        setFormData(initialFormData);
        setSuccessMessage('Партия успешно создана');
        setTimeout(() => setSuccessMessage(null), 3000);
      } else {
        setError(response?.error || 'Ошибка создания батча');
      }
    } catch (err: any) {
      setError(err.message || 'Ошибка создания батча');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-800">Управление производственными партиями</h1>
            <Button onClick={() => setIsFormOpen(true)}>Создать батч</Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {successMessage && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-800 rounded-md" role="status">
            {successMessage}
          </div>
        )}
        <BatchList />
      </main>

      <Modal
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        title="Создать производственную партию"
        size="md"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="text-red-600 text-sm bg-red-50 p-2 rounded">{error}</div>}

          <div>
            <label className="block text-sm font-medium mb-1">Продукт (масса) *</label>
            <select
              className="w-full border rounded px-2 py-1"
              value={formData.product_id}
              onChange={(e) => handleProductChange(e.target.value)}
              required
            >
              <option value="">Выберите продукт</option>
              {bulkProducts.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.product_code} - {product.product_name}
                </option>
              ))}
            </select>
          </div>

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
              className={`w-full border rounded px-2 py-1 ${quantityError ? 'border-red-500' : ''}`}
              value={formData.quantity_kg}
              onChange={(e) => setFormData({ ...formData, quantity_kg: Number(e.target.value) })}
              required
              min={minBatchKg ?? 0}
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
              value={formData.status ?? BatchStatus.PLANNED}
              onChange={(e) => setFormData({ ...formData, status: e.target.value as BatchStatus })}
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
              value={formData.operator_id ?? ''}
              onChange={(e) => setFormData({ ...formData, operator_id: e.target.value })}
              placeholder="Идентификатор оператора"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Плановое время старта</label>
            <input
              type="datetime-local"
              className="w-full border rounded px-2 py-1"
              value={formData.planned_start ?? ''}
              onChange={(e) => setFormData({ ...formData, planned_start: e.target.value })}
            />
          </div>

          <Button type="submit" isLoading={isSubmitting} disabled={!!quantityError}>
            Создать батч
          </Button>
        </form>
      </Modal>
    </div>
  );
};
