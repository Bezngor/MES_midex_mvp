/**
 * Блок «Выпущенные заказы»: список заказов в статусе RELEASED с кнопкой «Отменить выпуск».
 */

import React, { useEffect, useState } from 'react';
import { ordersAPI } from '../../services/api';
import { useScheduleStore } from '../../store/useScheduleStore';
import type { ManufacturingOrder } from '../../services/types';

const LIST_LIMIT = 20;

export const ReleasedOrdersBlock: React.FC<{
  onCancelled?: () => void;
}> = ({ onCancelled }) => {
  const [orders, setOrders] = useState<ManufacturingOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [cancellingId, setCancellingId] = useState<string | null>(null);
  const { cancelRelease, fetchGanttData } = useScheduleStore();

  const loadOrders = async () => {
    setLoading(true);
    try {
      const res = await ordersAPI.getAll({ status: 'RELEASED', limit: LIST_LIMIT });
      if (res.success && Array.isArray(res.data)) {
        setOrders(res.data);
      } else {
        setOrders([]);
      }
    } catch {
      setOrders([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
  }, []);

  const handleCancelRelease = async (orderId: string) => {
    setCancellingId(orderId);
    try {
      const result = await cancelRelease(orderId);
      if (result?.success) {
        setOrders((prev) => prev.filter((o) => o.id !== orderId));
        const start = new Date();
        start.setHours(0, 0, 0, 0);
        const end = new Date(start.getTime() + 6 * 24 * 60 * 60 * 1000);
        end.setHours(23, 59, 59, 999);
        await fetchGanttData(start.toISOString(), end.toISOString());
        onCancelled?.();
      }
    } finally {
      setCancellingId(null);
    }
  };

  if (loading) return <div className="text-sm text-gray-500">Загрузка выпущенных заказов…</div>;
  if (orders.length === 0) return null;

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-2">Выпущенные заказы</h3>
      <p className="text-xs text-gray-500 mb-3">
        Заказы в статусе RELEASED. «Отменить выпуск» вернёт заказ в статус SHIP и отменит созданные задачи.
      </p>
      <ul className="space-y-2 max-h-40 overflow-y-auto">
        {orders.map((order) => (
          <li key={order.id} className="flex items-center justify-between gap-2 py-1 border-b border-gray-100 last:border-0">
            <span className="text-sm truncate" title={order.product_name ?? order.product_id}>
              {order.product_name ? `${order.product_name} · ` : ''}{order.order_number} — кол-во {order.quantity}, срок{' '}
              {order.due_date ? new Date(order.due_date).toLocaleDateString('ru-RU') : '—'}
            </span>
            <button
              type="button"
              disabled={!!cancellingId}
              onClick={() => handleCancelRelease(order.id)}
              className="shrink-0 px-3 py-1 text-sm bg-amber-600 text-white rounded hover:bg-amber-700 disabled:opacity-50"
            >
              {cancellingId === order.id ? '…' : 'Отменить выпуск'}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};
