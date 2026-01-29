/**
 * Страница управления батчами
 */

import React, { useState } from 'react';
import { BatchList } from '../components/batches/BatchList';
import { useBatchStore } from '../store/useBatchStore';
import { BatchCreate } from '../services/types';
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
  const [formData, setFormData] = useState<BatchCreate>({
    product_id: '',
    quantity_kg: 0,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await createBatch(formData);
      if (response?.success) {
        setIsFormOpen(false);
        setFormData({ product_id: '', quantity_kg: 0 });
      } else {
        setError(response?.error || 'Ошибка создания батча');
      }
    } catch (err: any) {
      setError(err.message || 'Ошибка создания батча');
    } finally {
      setIsSubmitting(false);
    }
  };

  const bulkProducts = products.filter((p) => p.product_type === 'BULK');

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
              onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
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
            <label className="block text-sm font-medium mb-1">Количество (кг) *</label>
            <input
              type="number"
              step="0.01"
              className="w-full border rounded px-2 py-1"
              value={formData.quantity_kg}
              onChange={(e) => setFormData({ ...formData, quantity_kg: Number(e.target.value) })}
              required
              min="0"
            />
          </div>

          <Button type="submit" isLoading={isSubmitting}>
            Создать батч
          </Button>
        </form>
      </Modal>
    </div>
  );
};
