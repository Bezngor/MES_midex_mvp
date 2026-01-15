/**
 * Компонент формы создания/редактирования продукта
 */

import React, { useState } from 'react';
import { useProductStore } from '../../store/useProductStore';
import { ProductType, ProductCreate } from '../../services/types';
import { Button } from '../common/Button';

interface ProductFormProps {
  onSuccess?: () => void;
  initialData?: Partial<ProductCreate>;
}

export const ProductForm: React.FC<ProductFormProps> = ({ onSuccess, initialData }) => {
  const { createProduct, updateProduct } = useProductStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<ProductCreate>({
    product_code: initialData?.product_code || '',
    product_name: initialData?.product_name || '',
    product_type: initialData?.product_type || ProductType.RAW_MATERIAL,
    unit_of_measure: initialData?.unit_of_measure || 'kg',
    min_batch_size_kg: initialData?.min_batch_size_kg,
    batch_size_step_kg: initialData?.batch_size_step_kg,
    shelf_life_days: initialData?.shelf_life_days,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await createProduct(formData);
      if (response?.success) {
        onSuccess?.();
        // Сброс формы
        setFormData({
          product_code: '',
          product_name: '',
          product_type: ProductType.RAW_MATERIAL,
          unit_of_measure: 'kg',
        });
      } else {
        setError(response?.error || 'Ошибка создания продукта');
      }
    } catch (err: any) {
      setError(err.message || 'Ошибка создания продукта');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded-md bg-white">
      <h2 className="text-lg font-semibold">Создать продукт</h2>

      {error && <div className="text-red-600 text-sm bg-red-50 p-2 rounded">{error}</div>}

      <div>
        <label className="block text-sm font-medium mb-1">Код продукта *</label>
        <input
          type="text"
          className="w-full border rounded px-2 py-1"
          value={formData.product_code}
          onChange={(e) => setFormData({ ...formData, product_code: e.target.value })}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Название продукта *</label>
        <input
          type="text"
          className="w-full border rounded px-2 py-1"
          value={formData.product_name}
          onChange={(e) => setFormData({ ...formData, product_name: e.target.value })}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Тип продукта *</label>
        <select
          className="w-full border rounded px-2 py-1"
          value={formData.product_type}
          onChange={(e) => setFormData({ ...formData, product_type: e.target.value as ProductType })}
          required
        >
          {Object.values(ProductType).map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Единица измерения *</label>
        <input
          type="text"
          className="w-full border rounded px-2 py-1"
          value={formData.unit_of_measure}
          onChange={(e) => setFormData({ ...formData, unit_of_measure: e.target.value })}
          required
        />
      </div>

      {formData.product_type === ProductType.BULK && (
        <>
          <div>
            <label className="block text-sm font-medium mb-1">Мин. размер партии (кг)</label>
            <input
              type="number"
              className="w-full border rounded px-2 py-1"
              value={formData.min_batch_size_kg || ''}
              onChange={(e) => setFormData({ ...formData, min_batch_size_kg: e.target.value ? Number(e.target.value) : undefined })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Шаг размера партии (кг)</label>
            <input
              type="number"
              className="w-full border rounded px-2 py-1"
              value={formData.batch_size_step_kg || ''}
              onChange={(e) => setFormData({ ...formData, batch_size_step_kg: e.target.value ? Number(e.target.value) : undefined })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Срок хранения (дней)</label>
            <input
              type="number"
              className="w-full border rounded px-2 py-1"
              value={formData.shelf_life_days || ''}
              onChange={(e) => setFormData({ ...formData, shelf_life_days: e.target.value ? Number(e.target.value) : undefined })}
            />
          </div>
        </>
      )}

      <Button type="submit" isLoading={isSubmitting}>
        Создать продукт
      </Button>
    </form>
  );
};
