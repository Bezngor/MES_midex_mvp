/**
 * Компонент редактора спецификации (BOM)
 * Компонент: сначала категория (ГП / Масса / Сырьё), затем список. Количество — пустое по умолчанию. Единица — из справочника продукта.
 */

import React, { useState, useEffect, useMemo } from 'react';
import { useBOMStore } from '../../store/useBOMStore';
import { useProductStore } from '../../store/useProductStore';
import { BOMCreate, ProductType } from '../../services/types';
import { Button } from '../common/Button';

/** Допустимые категории компонентов в зависимости от категории родительского продукта:
 *  Родитель Масса → только Сырьё.
 *  Родитель ГП → Масса и Упаковка. */
const COMPONENT_CATEGORIES_BY_PARENT: Record<ProductType, { value: ProductType; label: string }[]> = {
  [ProductType.RAW_MATERIAL]: [], // сырьё не бывает родителем BOM
  [ProductType.BULK]: [{ value: ProductType.RAW_MATERIAL, label: 'Сырьё' }],
  [ProductType.PACKAGING]: [], // упаковка как родитель — не в сценарии
  [ProductType.FINISHED_GOOD]: [
    { value: ProductType.BULK, label: 'Масса' },
    { value: ProductType.PACKAGING, label: 'Упаковка' },
  ],
};

/** Парсинг числа: допускается запятая или точка как десятичный разделитель, до 6 знаков после запятой. */
function parseQuantity(value: string): number | null {
  const normalized = value.trim().replace(',', '.');
  if (normalized === '') return null;
  const num = Number(normalized);
  if (Number.isNaN(num) || num < 0) return null;
  const parts = normalized.split('.');
  if (parts.length === 2 && parts[1].length > 6) return null;
  return num;
}

interface BOMEditorProps {
  parentProductId: string;
  onSuccess?: () => void;
}

export const BOMEditor: React.FC<BOMEditorProps> = ({ parentProductId, onSuccess }) => {
  const { createBOM } = useBOMStore();
  const { products, getProductById } = useProductStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [componentCategory, setComponentCategory] = useState<ProductType | ''>('');
  const [childProductId, setChildProductId] = useState('');
  const [quantityInput, setQuantityInput] = useState('');
  const [unit, setUnit] = useState('');

  const parentProduct = parentProductId ? getProductById(parentProductId) : null;
  const allowedComponentCategories = useMemo(() => {
    if (!parentProduct?.product_type) return [];
    return COMPONENT_CATEGORIES_BY_PARENT[parentProduct.product_type] ?? [];
  }, [parentProduct?.product_type]);

  const productsInCategory = componentCategory
    ? products.filter((p) => p.product_type === componentCategory)
    : [];

  const selectedProduct = childProductId ? getProductById(childProductId) : null;

  useEffect(() => {
    if (selectedProduct?.unit_of_measure) {
      setUnit(selectedProduct.unit_of_measure);
    } else if (!childProductId) {
      setUnit('');
    }
  }, [childProductId, selectedProduct?.unit_of_measure]);

  useEffect(() => {
    const allowed = allowedComponentCategories.map((c) => c.value);
    if (componentCategory && !allowed.includes(componentCategory)) {
      setComponentCategory('');
      setChildProductId('');
      setUnit('');
    }
  }, [parentProductId, allowedComponentCategories, componentCategory]);

  const resetForm = () => {
    setChildProductId('');
    setQuantityInput('');
    setUnit('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const qty = parseQuantity(quantityInput);
    if (qty === null || qty === 0) {
      setError('Введите корректное количество (положительное число, до 6 знаков после запятой).');
      return;
    }
    if (!childProductId) {
      setError('Выберите компонент.');
      return;
    }
    setIsSubmitting(true);
    setError(null);

    const payload: BOMCreate = {
      parent_product_id: parentProductId,
      child_product_id: childProductId,
      quantity: qty,
      unit: unit || 'кг',
    };

    try {
      const response = await createBOM(payload);
      if (response?.success) {
        onSuccess?.();
        resetForm();
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
        <label className="block text-sm font-medium mb-1">Категория компонента *</label>
        <select
          className="w-full border rounded px-2 py-1"
          value={componentCategory}
          onChange={(e) => {
            setComponentCategory(e.target.value as ProductType | '');
            setChildProductId('');
            setUnit('');
          }}
          required
          disabled={allowedComponentCategories.length === 0}
        >
          <option value="">
            {allowedComponentCategories.length === 0
              ? 'Нет допустимых категорий для выбранного продукта'
              : 'Выберите категорию'}
          </option>
          {allowedComponentCategories.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>
      </div>

      {componentCategory && (
        <div>
          <label className="block text-sm font-medium mb-1">Компонент *</label>
          <select
            className="w-full border rounded px-2 py-1"
            value={childProductId}
            onChange={(e) => setChildProductId(e.target.value)}
            required
          >
            <option value="">Выберите продукт</option>
            {productsInCategory.map((product) => (
              <option key={product.id} value={product.id}>
                {product.product_code} - {product.product_name}
              </option>
            ))}
          </select>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium mb-1">Количество *</label>
        <input
          type="text"
          inputMode="decimal"
          className="w-full border rounded px-2 py-1"
          value={quantityInput}
          onChange={(e) => setQuantityInput(e.target.value)}
          placeholder="0"
          title="Допускается запятая или точка как десятичный разделитель, до 6 знаков после запятой."
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Единица измерения *</label>
        <input
          type="text"
          className="w-full border rounded px-2 py-1 bg-gray-50"
          value={unit}
          onChange={(e) => setUnit(e.target.value)}
          placeholder="Подтягивается из справочника продукта"
          required
        />
      </div>

      <Button type="submit" isLoading={isSubmitting}>
        Добавить компонент
      </Button>
    </form>
  );
};
