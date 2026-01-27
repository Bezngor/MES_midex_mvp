/**
 * Страница управления продуктами
 */

import React, { useState } from 'react';
import { ProductList } from '../components/products/ProductList';
import { ProductForm } from '../components/products/ProductForm';
import { Modal } from '../components/common/Modal';
import { Button } from '../components/common/Button';

export const ProductsPage: React.FC = () => {
  const [isFormOpen, setIsFormOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-800">Управление продуктами</h1>
            <Button onClick={() => setIsFormOpen(true)}>Создать продукт</Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        <ProductList />
      </main>

      <Modal
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        title="Создать продукт"
        size="md"
      >
        <ProductForm
          onSuccess={() => {
            setIsFormOpen(false);
          }}
        />
      </Modal>
    </div>
  );
};
