/**
 * Компонент списка заказов с кнопками "Принять"/"Отменить" для вкладки "Стратегия".
 * Отображает заказы с информацией о ГП, количестве, дате и приоритете.
 */

import React from 'react';
import type { OrderChangeInfo } from '../../types/api';
import type { Priority } from './PriorityFilters';

/** Нормализует UUID к 32 символам hex для сравнения (то же правило, что на странице Стратегия). */
function normalizeOrderIdForMatch(id: string | null | undefined): string {
  if (id == null || typeof id !== 'string') return '';
  const s = String(id).trim().toLowerCase().replace(/-/g, '');
  return /^[0-9a-f]{32}$/.test(s) ? s : String(id).trim().toLowerCase();
}

interface OrdersListWithAcceptProps {
  orders: OrderChangeInfo[];
  acceptedOrderIds: Set<string>;
  onAccept: (orderId: string) => void;
  onCancel: (orderId: string) => void;
  title: string;
  getOrderNumber?: (order: OrderChangeInfo) => string;
  getPriority?: (order: OrderChangeInfo) => Priority;
  getQuantity?: (order: OrderChangeInfo) => number | string;
  getDueDate?: (order: OrderChangeInfo) => string | null;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

export const OrdersListWithAccept: React.FC<OrdersListWithAcceptProps> = ({
  orders,
  acceptedOrderIds,
  onAccept,
  onCancel,
  title,
  getOrderNumber,
  getPriority,
  getQuantity,
  getDueDate,
  collapsed = false,
  onToggleCollapse,
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

  if (orders.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        {onToggleCollapse && (
          <button
            type="button"
            onClick={onToggleCollapse}
            className="text-gray-500 hover:text-gray-700 text-sm"
            title={collapsed ? 'Развернуть' : 'Свернуть'}
          >
            {collapsed ? '▶' : '▼'}
          </button>
        )}
      </div>
      {!collapsed && (
        <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Номер заказа
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                ГП (Продукт)
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Количество
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Дата выполнения
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Приоритет
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {orders.map((order) => {
              const orderId = order.order_id || order.order_number;
              const normalizedId = normalizeOrderIdForMatch(order.order_id);
              const isAccepted =
                acceptedOrderIds.has(orderId) ||
                (normalizedId.length > 0 && acceptedOrderIds.has(normalizedId));
              const priority = getPriority ? getPriority(order) : undefined;
              const quantity = getQuantity ? getQuantity(order) : '-';
              const dueDate = getDueDate ? getDueDate(order) : null;

              return (
                <tr
                  key={orderId}
                  className={`hover:bg-gray-50 ${
                    isAccepted ? 'bg-green-50' : ''
                  }`}
                >
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {getOrderNumber ? getOrderNumber(order) : order.order_number ?? '-'}
                  </td>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {order.product_name || order.product_id}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{quantity}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {formatDate(dueDate)}
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
      )}
    </div>
  );
};
