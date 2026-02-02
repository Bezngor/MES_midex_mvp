/**
 * Страница управления продуктами
 */

import React, { useState, useCallback } from 'react';
import { ProductList } from '../components/products/ProductList';
import { ProductForm } from '../components/products/ProductForm';
import { Modal } from '../components/common/Modal';
import { Button } from '../components/common/Button';
import { useProductStore } from '../store/useProductStore';
import type { Product } from '../services/types';

type ModalMode = null | 'create' | { productId: string };

export const ProductsPage: React.FC = () => {
  const [modalMode, setModalMode] = useState<ModalMode>(null);
  const { getProductById } = useProductStore();

  const handleEdit = useCallback((product: Product) => {
    setModalMode({ productId: product.id });
  }, []);

  const isOpen = modalMode !== null;

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-800">Управление продуктами</h1>
            <Button onClick={() => setModalMode('create')}>Создать продукт</Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        <ProductList onEdit={handleEdit} />
      </main>

      {isOpen && (
        <Modal
          isOpen
          onClose={() => setModalMode(null)}
          title={modalMode === 'create' ? 'Создать продукт' : 'Редактировать продукт'}
          size="md"
        >
          <ProductForm
            productId={typeof modalMode === 'object' ? modalMode.productId : undefined}
            initialData={
              typeof modalMode === 'object'
                ? (() => {
                    const product = getProductById(modalMode.productId);
                    return product
                      ? {
                          product_name: product.product_name,
                          product_type: product.product_type,
                          unit_of_measure: product.unit_of_measure,
                          min_batch_size_kg: product.min_batch_size_kg,
                          batch_size_step_kg: product.batch_size_step_kg,
                          shelf_life_days: product.shelf_life_days,
                          product_code: product.product_code,
                        }
                      : undefined;
                  })()
                : undefined
            }
            onSuccess={() => setModalMode(null)}
          />
        </Modal>
      )}
    </div>
  );
};
