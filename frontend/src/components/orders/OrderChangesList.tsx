/**
 * Компонент списка новых и изменённых заказов.
 * Реализует шаг бизнес-процесса "Блок обновления данных" → "Выявить новые и/или измененные ЗП".
 */

import React, { useState, useEffect } from 'react';
import { ordersAPI } from '../../services/api';
import type { OrderChangesListResponse, OrderChangeInfo } from '../../types/api';
import { Loading } from '../common/Loading';
import { Error } from '../common/Error';
import { OrderChangesDetail } from './OrderChangesDetail';

interface OrderChangesListProps {
  onOrderSelect?: (orderId: string) => void;
}

export const OrderChangesList: React.FC<OrderChangesListProps> = ({ onOrderSelect }) => {
  const [data, setData] = useState<OrderChangesListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
  const [orderType, setOrderType] = useState<'CUSTOMER' | 'INTERNAL_BULK'>('CUSTOMER');
  const [sinceDate, setSinceDate] = useState<string>('');

  const loadChanges = async () => {
    setLoading(true);
    setError(null);

    try {
      const params: { order_type?: string; since_date?: string } = {};
      if (orderType) {
        params.order_type = orderType;
      }
      if (sinceDate) {
        params.since_date = sinceDate;
      }

      const response = await ordersAPI.getChanges(params);
      setData(response);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка при загрузке изменений заказов');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadChanges();
  }, []);

  const handleOrderClick = (orderId: string) => {
    setSelectedOrderId(orderId);
    if (onOrderSelect) {
      onOrderSelect(orderId);
    }
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('ru-RU');
  };

  if (loading) {
    return <Loading />;
  }

  if (error) {
    return <Error message={error} onRetry={loadChanges} />;
  }

  if (!data) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Фильтры */}
      <div className="bg-white rounded-lg shadow p-4 space-y-4">
        <h3 className="text-lg font-semibold text-gray-800">Фильтры</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Тип заказа
            </label>
            <select
              value={orderType}
              onChange={(e) => setOrderType(e.target.value as 'CUSTOMER' | 'INTERNAL_BULK')}
              className="w-full border rounded px-3 py-2"
            >
              <option value="CUSTOMER">Заказы покупателей</option>
              <option value="INTERNAL_BULK">Внутренние bulk-заказы</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Дата начала поиска (опционально)
            </label>
            <input
              type="date"
              value={sinceDate}
              onChange={(e) => setSinceDate(e.target.value)}
              className="w-full border rounded px-3 py-2"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={loadChanges}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
            >
              Обновить
            </button>
          </div>
        </div>
      </div>

      {/* Сводка */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 border border-blue-200 rounded p-4">
            <div className="text-sm text-gray-600">Новых заказов</div>
            <div className="text-2xl font-bold text-blue-600">{data.total_new}</div>
          </div>
          <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
            <div className="text-sm text-gray-600">Изменённых заказов</div>
            <div className="text-2xl font-bold text-yellow-600">{data.total_changed}</div>
          </div>
          <div className="bg-red-50 border border-red-200 rounded p-4">
            <div className="text-sm text-gray-600">Удалённых заказов</div>
            <div className="text-2xl font-bold text-red-600">{data.total_deleted || 0}</div>
          </div>
        </div>
      </div>

      {/* Список новых заказов */}
      {data.new_orders.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h3 className="text-lg font-semibold text-gray-800">Новые заказы</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Номер заказа</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Продукт</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Количество</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дата создания</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Действия</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.new_orders.map((order) => (
                  <tr
                    key={order.order_id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => handleOrderClick(order.order_id)}
                  >
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{order.order_number}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {order.product_name || order.product_id}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">-</td>
                    <td className="px-4 py-3 text-sm text-gray-600">-</td>
                    <td className="px-4 py-3 text-sm">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOrderClick(order.order_id);
                        }}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        Подробнее
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Список изменённых заказов */}
      {data.changed_orders.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h3 className="text-lg font-semibold text-gray-800">Изменённые заказы</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Номер заказа</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Продукт</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Последний снимок</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Обновлён</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Действия</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.changed_orders.map((order) => (
                  <tr
                    key={order.order_id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => handleOrderClick(order.order_id)}
                  >
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{order.order_number}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {order.product_name || order.product_id}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {formatDate(order.last_snapshot_date)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {formatDate(order.current_updated_at)}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOrderClick(order.order_id);
                        }}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        Подробнее
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Список удалённых заказов */}
      {data.deleted_orders && data.deleted_orders.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h3 className="text-lg font-semibold text-gray-800">Удалённые заказы</h3>
            <p className="text-sm text-gray-600 mt-1">Заказы, которые были в снимках, но отсутствуют в текущей таблице</p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Номер заказа</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Продукт</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Последний снимок</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Действия</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.deleted_orders.map((order) => (
                  <tr
                    key={order.order_number}
                    className="hover:bg-gray-50 cursor-pointer bg-red-50"
                    onClick={() => handleOrderClick(order.order_id || order.order_number)}
                  >
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{order.order_number}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {order.product_name || order.product_id}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {formatDate(order.last_snapshot_date)}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className="inline-block px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-medium">
                        Удалён
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Сообщение, если нет изменений */}
      {data.total_new === 0 && data.total_changed === 0 && (!data.deleted_orders || data.deleted_orders.length === 0) && (
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <p className="text-gray-600">Нет новых, изменённых или удалённых заказов</p>
        </div>
      )}

      {/* Модальное окно с деталями изменений */}
      {selectedOrderId && selectedOrderId.length === 36 && selectedOrderId.includes('-') && (
        <OrderChangesDetail
          orderId={selectedOrderId}
          onClose={() => setSelectedOrderId(null)}
        />
      )}
    </div>
  );
};
