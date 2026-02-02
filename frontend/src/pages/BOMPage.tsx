/**
 * Страница управления спецификациями (BOM)
 * Выбор продукта: сначала категория (ГП или Масса), затем список без сырья.
 */

import React, { useState, useEffect } from 'react';
import { useProductStore } from '../store/useProductStore';
import { BOMTree } from '../components/bom/BOMTree';
import { BOMEditor } from '../components/bom/BOMEditor';
import { Loading } from '../components/common/Loading';
import { ProductType } from '../services/types';

/** Категория продукта для редактирования BOM: только ГП или Масса (сырьё не участвует). */
const BOM_PARENT_CATEGORIES = [
  { value: ProductType.FINISHED_GOOD, label: 'Готовая продукция (ГП)' },
  { value: ProductType.BULK, label: 'Масса' },
] as const;

export const BOMPage: React.FC = () => {
  const { products, loading, fetchProducts } = useProductStore();
  const [category, setCategory] = useState<ProductType.FINISHED_GOOD | ProductType.BULK | ''>('');
  const [selectedProductId, setSelectedProductId] = useState<string>('');

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const productsInCategory = category
    ? products.filter((p) => p.product_type === category)
    : [];

  const onCategoryChange = (newCategory: string) => {
    setCategory(newCategory as ProductType.FINISHED_GOOD | ProductType.BULK | '');
    setSelectedProductId('');
  };

  if (loading) return <Loading message="Загрузка продуктов..." />;

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-800">Управление спецификациями (BOM)</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="mb-4 space-y-2">
          <label className="block text-sm font-medium">Выберите категорию продукта для редактирования спецификации:</label>
          <select
            className="w-full max-w-md border rounded px-3 py-2"
            value={category}
            onChange={(e) => onCategoryChange(e.target.value)}
          >
            <option value="">Выберите категорию</option>
            {BOM_PARENT_CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
          {category && (
            <>
              <label className="block text-sm font-medium">Продукт:</label>
              <select
                className="w-full max-w-md border rounded px-3 py-2"
                value={selectedProductId}
                onChange={(e) => setSelectedProductId(e.target.value)}
              >
                <option value="">Выберите продукт</option>
                {productsInCategory.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.product_code} - {product.product_name}
                  </option>
                ))}
              </select>
            </>
          )}
        </div>

        {selectedProductId && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <BOMTree productId={selectedProductId} />
            </div>
            <div>
              <BOMEditor
                parentProductId={selectedProductId}
                onSuccess={() => {
                  // Обновление произойдёт автоматически через store
                }}
              />
            </div>
          </div>
        )}

        {!selectedProductId && (
          <div className="text-center text-gray-500 py-8">
            Выберите продукт для просмотра и редактирования спецификации
          </div>
        )}
      </main>
    </div>
  );
};
