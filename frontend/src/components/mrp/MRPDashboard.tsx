/**
 * Компонент дашборда MRP (Material Requirements Planning)
 */

import React, { useEffect, useState } from 'react';
import { useMRPStore } from '../../store/useMRPStore';
import { Loading } from '../common/Loading';
import { Error } from '../common/Error';
import { Button } from '../common/Button';

export const MRPDashboard: React.FC = () => {
  const { consolidatedOrders, loading, error, consolidateOrders } = useMRPStore();
  const [horizonDays, setHorizonDays] = useState(30);

  useEffect(() => {
    consolidateOrders(horizonDays);
  }, [horizonDays, consolidateOrders]);

  if (loading) return <Loading message="Консолидация заказов..." />;
  if (error) return <Error message={error} onRetry={() => consolidateOrders(horizonDays)} />;

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">MRP - Консолидация заказов</h2>
        <div className="flex gap-2 items-center">
          <label className="text-sm">Горизонт планирования (дней):</label>
          <input
            type="number"
            className="border rounded px-2 py-1 w-20"
            value={horizonDays}
            onChange={(e) => setHorizonDays(Number(e.target.value))}
            min="1"
            max="365"
          />
          <Button onClick={() => consolidateOrders(horizonDays)} size="sm">
            Обновить
          </Button>
        </div>
      </div>

      <div className="mb-4 p-4 bg-blue-50 rounded-lg">
        <p className="text-sm text-gray-700">
          Найдено <strong>{consolidatedOrders.length}</strong> продуктов для производства
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-300">
          <thead className="bg-gray-100">
            <tr>
              <th className="border border-gray-300 p-2 text-left">Продукт</th>
              <th className="border border-gray-300 p-2 text-left">Общее количество</th>
              <th className="border border-gray-300 p-2 text-left">Приоритет</th>
              <th className="border border-gray-300 p-2 text-left">Крайний срок</th>
              <th className="border border-gray-300 p-2 text-left">Источник заказов</th>
            </tr>
          </thead>
          <tbody>
            {consolidatedOrders.length === 0 ? (
              <tr>
                <td colSpan={5} className="border border-gray-300 p-4 text-center text-gray-500">
                  Нет заказов для консолидации
                </td>
              </tr>
            ) : (
              consolidatedOrders.map((order, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="border border-gray-300 p-2">{order.product_id}</td>
                  <td className="border border-gray-300 p-2">{order.total_quantity.toLocaleString('ru-RU')}</td>
                  <td className="border border-gray-300 p-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      order.priority === 'URGENT' ? 'bg-red-100 text-red-800' :
                      order.priority === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                      order.priority === 'NORMAL' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {order.priority}
                    </span>
                  </td>
                  <td className="border border-gray-300 p-2">
                    {new Date(order.earliest_due_date).toLocaleDateString('ru-RU')}
                  </td>
                  <td className="border border-gray-300 p-2">
                    <span className="text-sm text-gray-600">
                      {order.source_orders.length} заказ(ов)
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
