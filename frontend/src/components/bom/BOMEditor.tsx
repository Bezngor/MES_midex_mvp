/**
 * Компонент редактора спецификации (BOM)
 */

import React, { useState } from 'react';
import { useBOMStore } from '../../store/useBOMStore';
import { useProductStore } from '../../store/useProductStore';
import { BOMCreate } from '../../services/types';
import { Button } from '../common/Button';

interface BOMEditorProps {
  parentProductId: string;
  onSuccess?: () => void;
}

export const BOMEditor: React.FC<BOMEditorProps> = ({ parentProductId, onSuccess }) => {
  const { createBOM } = useBOMStore();
  const { products } = useProductStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<BOMCreate>({
    parent_product_id: parentProductId,
    child_product_id: '',
    quantity: 0,
    unit: 'kg',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await createBOM(formData);
      if (response?.success) {
        onSuccess?.();
        setFormData({
          parent_product_id: parentProductId,
          child_product_id: '',
          quantity: 0,
          unit: 'kg',
        });
      } else {
        setError(response?.error || 'Ошибка создания строки спецификации');
      }
    } catch (err: any) {
      setError(err.message || 'Ошибка создания строки спецификации');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded-md bg-white">
      <h3 className="text-lg font-semibold">Добавить компонент в спецификацию</h3>

      {error && <div className="text-red-600 text-sm bg-red-50 p-2 rounded">{error}</div>}

      <div>
        <label className="block text-sm font-medium mb-1">Компонент *</label>
        <select
          className="w-full border rounded px-2 py-1"
          value={formData.child_product_id}
          onChange={(e) => setFormData({ ...formData, child_product_id: e.target.value })}
          required
        >
          <option value="">Выберите продукт</option>
          {products.map((product) => (
            <option key={product.id} value={product.id}>
              {product.product_code} - {product.product_name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Количество *</label>
        <input
          type="number"
          step="0.01"
          className="w-full border rounded px-2 py-1"
          value={formData.quantity}
          onChange={(e) => setFormData({ ...formData, quantity: Number(e.target.value) })}
          required
          min="0"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Единица измерения *</label>
        <input
          type="text"
          className="w-full border rounded px-2 py-1"
          value={formData.unit}
          onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
          required
        />
      </div>

      <Button type="submit" isLoading={isSubmitting}>
        Добавить компонент
      </Button>
    </form>
  );
};
