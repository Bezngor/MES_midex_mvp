/**
 * Компонент дашборда остатков на складе
 */

import React, { useEffect, useMemo, useState } from 'react';
import { useInventoryStore } from '../../store/useInventoryStore';
import { Loading } from '../common/Loading';
import { Error } from '../common/Error';
import { ProductType } from '../../services/types';

/** Подпись статуса остатка: готов к выдаче (сырьё, масса, ГП) — не путать с типом продукта «ГП». */
const INVENTORY_STATUS_FINISHED_LABEL = 'Готово к отпуску';

/** Фильтр по типу продукта: Сырьё, Масса, Упаковка, ГП. */
const PRODUCT_TYPE_FILTER_OPTIONS: { value: ProductType | ''; label: string }[] = [
  { value: '', label: 'Все типы продукта' },
  { value: ProductType.RAW_MATERIAL, label: 'Сырьё' },
  { value: ProductType.BULK, label: 'Масса' },
  { value: ProductType.PACKAGING, label: 'Упаковка' },
  { value: ProductType.FINISHED_GOOD, label: 'Готовая продукция (ГП)' },
];

export const InventoryDashboard: React.FC = () => {
  const { inventory, loading, error, fetchInventory } = useInventoryStore();
  const [filter, setFilter] = useState<'FINISHED' | 'SEMI_FINISHED' | ''>('');
  const [productTypeFilter, setProductTypeFilter] = useState<ProductType | ''>('');

  // Безопасное преобразование значения (string | number | null) в число
  const toNumber = (value: unknown): number => {
    if (typeof value === 'number') return value;
    if (value === null || value === undefined) return 0;
    const parsed = parseFloat(String(value));
    return Number.isNaN(parsed) ? 0 : parsed;
  };

  useEffect(() => {
    fetchInventory(undefined, undefined, filter || undefined);
  }, [filter, fetchInventory]);

  const safeInventory = Array.isArray(inventory) ? inventory : [];
  const filteredInventory = useMemo(() => {
    if (!productTypeFilter) return safeInventory;
    return safeInventory.filter((item) => {
      const pt = item?.product?.product_type;
      return pt != null && String(pt) === String(productTypeFilter);
    });
  }, [safeInventory, productTypeFilter]);

  const totalQuantity = filteredInventory.reduce((sum, item) => sum + toNumber(item.quantity), 0);
  const totalAvailable = filteredInventory.reduce((sum, item) => {
    const rawAvailable =
      item.available_quantity !== undefined && item.available_quantity !== null
        ? item.available_quantity
        : toNumber(item.quantity) - toNumber(item.reserved_quantity);
    const availableQty = toNumber(rawAvailable);
    return sum + availableQty;
  }, 0);
  const totalReserved = filteredInventory.reduce((sum, item) => sum + toNumber(item.reserved_quantity), 0);

  if (loading) return <Loading message="Загрузка остатков..." />;
  if (error) return <Error message={error} onRetry={() => fetchInventory(undefined, undefined, filter || undefined)} />;

  return (
    <div className="p-4">
      <div className="flex flex-wrap justify-between items-center gap-4 mb-4">
        <h2 className="text-2xl font-bold text-gray-800">Остатки на складе</h2>
        <div className="flex flex-wrap gap-2">
          <select
            className="border rounded px-3 py-2"
            value={filter}
            onChange={(e) => setFilter(e.target.value as 'FINISHED' | 'SEMI_FINISHED' | '')}
            title="Фильтр по типу остатка: готово к отпуску или полуфабрикат"
          >
            <option value="">Все типы остатка</option>
            <option value="FINISHED">{INVENTORY_STATUS_FINISHED_LABEL}</option>
            <option value="SEMI_FINISHED">Полуфабрикаты</option>
          </select>
          <select
            className="border rounded px-3 py-2"
            value={productTypeFilter}
            onChange={(e) => setProductTypeFilter(e.target.value as ProductType | '')}
            title="Фильтр по типу продукта: Сырьё, Масса, Упаковка, ГП"
          >
            {PRODUCT_TYPE_FILTER_OPTIONS.map((opt) => (
              <option key={opt.value || 'all'} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Общее количество</p>
          <p className="text-2xl font-bold text-gray-900">
            {totalQuantity.toLocaleString('ru-RU', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Доступно</p>
          <p className="text-2xl font-bold text-gray-900">
            {totalAvailable.toLocaleString('ru-RU', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </p>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Зарезервировано</p>
          <p className="text-2xl font-bold text-gray-900">
            {totalReserved.toLocaleString('ru-RU', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </p>
        </div>
      </div>

      {/* Таблица */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-300">
          <thead className="bg-gray-100">
            <tr>
              <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">Продукт</th>
              <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">Локация</th>
              <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">Количество</th>
              <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">Статус</th>
              <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">Доступно</th>
              <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">Зарезервировано</th>
            </tr>
          </thead>
          <tbody>
            {filteredInventory.length === 0 ? (
              <tr>
                <td colSpan={6} className="border border-gray-300 p-4 text-center text-gray-500">
                  Остатки не найдены
                </td>
              </tr>
            ) : (
              filteredInventory.map((item) => {
                // Вычисляем available_quantity если оно не пришло с сервера
                const quantity = toNumber(item.quantity);
                const reserved = toNumber(item.reserved_quantity);
                const rawAvailable =
                  item.available_quantity !== undefined && item.available_quantity !== null
                    ? item.available_quantity
                    : quantity - reserved;
                const availableQty = toNumber(rawAvailable);
                
                return (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="border border-gray-300 p-2 text-gray-900">
                      {item.product?.product_name || item.product_id}
                    </td>
                    <td className="border border-gray-300 p-2 text-gray-900">{item.location}</td>
                    <td className="border border-gray-300 p-2 text-gray-900">
                      {`${quantity.toLocaleString('ru-RU', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })} ${item.unit}`}
                    </td>
                    <td className="border border-gray-300 p-2">
                      <span className={`px-2 py-1 rounded text-xs ${
                        item.product_status === 'FINISHED' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`} title={item.product_status === 'FINISHED' ? INVENTORY_STATUS_FINISHED_LABEL : 'Полуфабрикат'}>
                        {item.product_status === 'FINISHED' ? INVENTORY_STATUS_FINISHED_LABEL : 'Полуфабрикат'}
                      </span>
                    </td>
                    <td className="border border-gray-300 p-2 text-gray-900">
                      {`${availableQty.toLocaleString('ru-RU', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })} ${item.unit}`}
                    </td>
                    <td className="border border-gray-300 p-2 text-gray-900">
                      {`${reserved.toLocaleString('ru-RU', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })} ${item.unit}`}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
