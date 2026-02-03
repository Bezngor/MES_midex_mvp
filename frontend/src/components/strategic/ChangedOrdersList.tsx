/**
 * Компонент списка изменённых заказов с отображением старого и нового значения.
 * Для вкладки "Стратегия".
 */

import React from 'react';
import type { OrderChangeInfo } from '../../types/api';
import type { Priority } from './PriorityFilters';

interface ChangedOrdersListProps {
  orders: OrderChangeInfo[];
  acceptedOrderIds: Set<string>;
  onAccept: (orderId: string) => void;
  onCancel: (orderId: string) => void;
  getPriority?: (order: OrderChangeInfo) => Priority | undefined;
}

export const ChangedOrdersList: React.FC<ChangedOrdersListProps> = ({
  orders,
  acceptedOrderIds,
  onAccept,
  onCancel,
  getPriority,
}) => {
  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '-';
    try {
      return new Date(dateString).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      });
    } catch {
      return dateString;
    }
  };

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'boolean') return value ? 'Да' : 'Нет';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  };

  const getPriorityColor = (priority: Priority | undefined) => {
    if (!priority) return 'bg-gray-100 text-gray-800';
    switch (priority) {
      case 'URGENT':
        return 'bg-red-100 text-red-800';
      case 'HIGH':
        return 'bg-orange-100 text-orange-800';
      case 'NORMAL':
        return 'bg-blue-100 text-blue-800';
      case 'LOW':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityLabel = (priority: Priority | undefined) => {
    if (!priority) return '-';
    switch (priority) {
      case 'URGENT':
        return 'Срочно';
      case 'HIGH':
        return 'Высокий';
      case 'NORMAL':
        return 'Обычный';
      case 'LOW':
        return 'Низкий';
      default:
        return '-';
    }
  };

  const getFieldLabel = (field: string): string => {
    const labels: Record<string, string> = {
      quantity: 'Количество',
      due_date: 'Дата выполнения',
      priority: 'Приоритет',
      product_id: 'Продукт',
      status: 'Статус',
    };
    return labels[field] || field;
  };

  if (orders.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <h3 className="text-lg font-semibold text-gray-800">Изменённые заказы</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                ГП (Продукт)
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Изменения
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Текущий приоритет
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {orders.map((order) => {
              const orderId = order.order_id || order.order_number;
              const isAccepted = acceptedOrderIds.has(orderId);
              const priority = getPriority ? getPriority(order) : undefined;
              const changes = order.changes || {};

              return (
                <tr
                  key={orderId}
                  className={`hover:bg-gray-50 ${
                    isAccepted ? 'bg-green-50' : ''
                  }`}
                >
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {order.product_name || order.product_id}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {Object.keys(changes).length > 0 ? (
                      <div className="space-y-1">
                        {Object.entries(changes).map(([field, [oldValue, newValue]]) => (
                          <div key={field} className="text-xs">
                            <span className="font-medium text-gray-700">
                              {getFieldLabel(field)}:
                            </span>{' '}
                            <span className="bg-red-50 text-red-800 px-1 py-0.5 rounded">
                              {formatValue(oldValue)}
                            </span>{' '}
                            <span className="text-gray-500">→</span>{' '}
                            <span className="bg-green-50 text-green-800 px-1 py-0.5 rounded">
                              {formatValue(newValue)}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <span className="text-gray-500">Нет изменений</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span
                      className={`inline-block px-2 py-1 rounded text-xs font-medium ${getPriorityColor(
                        priority
                      )}`}
                    >
                      {getPriorityLabel(priority)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {isAccepted ? (
                      <button
                        onClick={() => onCancel(orderId)}
                        className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 font-medium"
                      >
                        Отменить
                      </button>
                    ) : (
                      <button
                        onClick={() => onAccept(orderId)}
                        className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 font-medium"
                      >
                        Принять
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
