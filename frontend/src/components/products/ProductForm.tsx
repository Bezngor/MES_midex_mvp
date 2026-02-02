/**
 * Компонент формы создания/редактирования продукта
 */

import React, { useState, useEffect } from 'react';
import { useProductStore } from '../../store/useProductStore';
import { ProductType, ProductCreate } from '../../services/types';
import { Button } from '../common/Button';

interface ProductFormProps {
  onSuccess?: () => void;
  /** Режим редактирования: id продукта и начальные данные (из getProductById). */
  productId?: string;
  initialData?: Partial<ProductCreate & { product_code?: string }>;
}

export const ProductForm: React.FC<ProductFormProps> = ({ onSuccess, productId, initialData }) => {
  const { createProduct, updateProduct } = useProductStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const isEdit = Boolean(productId);

  const [formData, setFormData] = useState<ProductCreate>({
    product_name: initialData?.product_name || '',
    product_type: initialData?.product_type || ProductType.RAW_MATERIAL,
    unit_of_measure: initialData?.unit_of_measure || 'кг',
    min_batch_size_kg: initialData?.min_batch_size_kg,
    batch_size_step_kg: initialData?.batch_size_step_kg,
    shelf_life_days: initialData?.shelf_life_days,
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        product_name: initialData.product_name || '',
        product_type: initialData.product_type || ProductType.RAW_MATERIAL,
        unit_of_measure: initialData.unit_of_measure || 'кг',
        min_batch_size_kg: initialData.min_batch_size_kg,
        batch_size_step_kg: initialData.batch_size_step_kg,
        shelf_life_days: initialData.shelf_life_days,
      });
    }
  }, [productId, initialData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      if (isEdit && productId) {
        const response = await updateProduct(productId, formData);
        if (response?.success) {
          onSuccess?.();
        } else {
          setError(response?.error || 'Ошибка обновления продукта');
        }
      } else {
        const response = await createProduct(formData);
        if (response?.success) {
          onSuccess?.();
          setFormData({
            product_name: '',
            product_type: ProductType.RAW_MATERIAL,
            unit_of_measure: 'кг',
          });
        } else {
          setError(response?.error || 'Ошибка создания продукта');
        }
      }
    } catch (err: any) {
      setError(err?.message || (isEdit ? 'Ошибка обновления продукта' : 'Ошибка создания продукта'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded-md bg-white">
      <h2 className="text-lg font-semibold">{isEdit ? 'Редактировать продукт' : 'Создать продукт'}</h2>

      {error && <div className="text-red-600 text-sm bg-red-50 p-2 rounded">{error}</div>}

      {isEdit && initialData?.product_code ? (
        <div>
          <label className="block text-sm font-medium mb-1">Код продукта</label>
          <div className="w-full border rounded px-2 py-1 bg-gray-100 text-gray-700">{initialData.product_code}</div>
        </div>
      ) : (
        <div className="text-sm text-gray-600">Код продукта создаётся автоматически при сохранении.</div>
      )}

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
        {isEdit ? 'Сохранить' : 'Создать продукт'}
      </Button>
    </form>
  );
};
