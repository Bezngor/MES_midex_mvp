/**
 * Компонент списка продуктов
 */

import React, { useEffect, useState } from 'react';
import { useProductStore } from '../../store/useProductStore';
import { ProductType, Product } from '../../services/types';
import { Loading } from '../common/Loading';
import { Error } from '../common/Error';
import { Button } from '../common/Button';
import { ConfirmDialog } from '../common/ConfirmDialog';

interface ProductListProps {
  onEdit?: (product: Product) => void;
}

export const ProductList: React.FC<ProductListProps> = ({ onEdit }) => {
  const { products, loading, error, fetchProducts, deleteProduct } = useProductStore();
  const [filter, setFilter] = useState<ProductType | ''>('');
  const [deleteConfirm, setDeleteConfirm] = useState<{ id: string; name: string } | null>(null);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const filteredProducts = filter
    ? products.filter((p) => p.product_type === filter)
    : products;

  if (loading) return <Loading message="Загрузка продуктов..." />;
  if (error) return <Error message={error} onRetry={fetchProducts} />;

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-gray-800">Продукты</h2>
        <select
          className="border rounded px-3 py-2"
          value={filter}
          onChange={(e) => setFilter(e.target.value as ProductType)}
        >
          <option value="">Все типы</option>
          {Object.values(ProductType).map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-300">
          <thead className="bg-gray-100">
            <tr>
              <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">Код</th>
              <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">Название</th>
              <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">Тип</th>
              <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">Ед. изм.</th>
              <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">Действия</th>
            </tr>
          </thead>
          <tbody>
            {filteredProducts.length === 0 ? (
              <tr>
                <td colSpan={5} className="border border-gray-300 p-4 text-center text-gray-500">
                  Продукты не найдены
                </td>
              </tr>
            ) : (
              filteredProducts.map((product) => (
                <tr key={product.id} className="hover:bg-gray-50">
                  <td className="border border-gray-300 p-2 text-gray-900">{product.product_code}</td>
                  <td className="border border-gray-300 p-2 text-gray-900">{product.product_name}</td>
                  <td className="border border-gray-300 p-2 text-gray-900">{product.product_type}</td>
                  <td className="border border-gray-300 p-2 text-gray-900">{product.unit_of_measure}</td>
                  <td className="border border-gray-300 p-2">
                    <div className="flex flex-wrap gap-2">
                      {onEdit && (
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => onEdit(product)}
                        >
                          Редактировать
                        </Button>
                      )}
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => setDeleteConfirm({ id: product.id, name: product.product_name })}
                      >
                        Удалить
                      </Button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <ConfirmDialog
        isOpen={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        onConfirm={async () => {
          const id = deleteConfirm?.id;
          setDeleteConfirm(null);
          if (id) await deleteProduct(id);
        }}
        title="Подтверждение удаления"
        message={deleteConfirm ? `Удалить продукт «${deleteConfirm.name}»? Это действие нельзя отменить.` : ''}
        confirmLabel="Удалить"
      />
    </div>
  );
};
