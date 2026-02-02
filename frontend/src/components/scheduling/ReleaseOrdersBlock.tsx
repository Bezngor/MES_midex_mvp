/**
 * Блок «Выпуск заказов в производство»: список заказов SHIP/PLANNED с кнопкой «Выпустить».
 * После выпуска создаются производственные задачи и они отображаются в Ганте.
 */

import React, { useEffect, useState } from 'react';
import { ordersAPI } from '../../services/api';
import { useScheduleStore } from '../../store/useScheduleStore';
import type { ManufacturingOrder } from '../../services/types';

const LIST_LIMIT = 30;

export const ReleaseOrdersBlock: React.FC<{
  onReleased?: () => void;
  /** false = блокировать выпуск (есть ГП без маршрутов/правил) */
  systemReady?: boolean;
}> = ({ onReleased, systemReady = true }) => {
  const [orders, setOrders] = useState<ManufacturingOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [releasingId, setReleasingId] = useState<string | null>(null);
  const { releaseOrder, fetchGanttData } = useScheduleStore();

  const loadOrders = async () => {
    setLoading(true);
    try {
      const [resShip, resPlanned, resInWork] = await Promise.all([
        ordersAPI.getAll({ status: 'SHIP', limit: LIST_LIMIT }),
        ordersAPI.getAll({ status: 'PLANNED', limit: LIST_LIMIT }),
        ordersAPI.getAll({ status: 'IN_WORK', limit: LIST_LIMIT }),
      ]);
      const byId = new Map<string, ManufacturingOrder>();
      [resShip, resPlanned, resInWork].forEach((res) => {
        if (res.success && Array.isArray(res.data)) res.data.forEach((o) => byId.set(o.id, o));
      });
      setOrders(Array.from(byId.values()).slice(0, LIST_LIMIT));
    } catch {
      setOrders([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
  }, []);

  const handleRelease = async (orderId: string) => {
    setReleasingId(orderId);
    try {
      const result = await releaseOrder(orderId);
      if (result?.success) {
        setOrders((prev) => prev.filter((o) => o.id !== orderId));
        const start = new Date();
        start.setHours(0, 0, 0, 0);
        const end = new Date(start.getTime() + 6 * 24 * 60 * 60 * 1000);
        end.setHours(23, 59, 59, 999);
        await fetchGanttData(start.toISOString(), end.toISOString());
        onReleased?.();
      }
    } finally {
      setReleasingId(null);
    }
  };

  if (loading) return <div className="text-sm text-gray-500">Загрузка заказов...</div>;
  if (orders.length === 0) return null;

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-2">Выпуск заказов в производство</h3>
      {!systemReady && (
        <p className="text-sm text-amber-700 mb-2">
          Выпуск заблокирован: довнесите маршруты и правила выбора РЦ для всех ГП (см. блок выше) и нажмите «Проверить снова».
        </p>
      )}
      <p className="text-sm text-gray-600 mb-1">
        Заказы со статусом SHIP, IN_WORK или PLANNED. Нажмите «Выпустить» — появятся задачи в Ганте.
      </p>
      <p className="text-xs text-gray-500 mb-1">
        <strong>Статусы:</strong> SHIP и IN_WORK — заказы из 1С (в 1С: «Отгрузить» и «В работе»; в MES различие идёт в приоритет, а не в статусе заказа). PLANNED — заказы, созданные в MES вручную.
      </p>
      <p className="text-xs text-gray-500 mb-3">
        В каждой строке — один заказ на один продукт (ГП). «Кол-во» — количество этого продукта в заказе, в ед. продукта. Показаны первые {LIST_LIMIT} заказов; состав списка зависит от датасета и порядка выборки.
      </p>
      <ul className="space-y-2 max-h-48 overflow-y-auto">
        {orders.slice(0, LIST_LIMIT).map((order) => (
          <li key={order.id} className="flex items-center justify-between gap-2 py-1 border-b border-gray-100 last:border-0">
            <span className="text-sm truncate" title={order.product_name ?? order.product_id}>
              {order.product_name ? `${order.product_name} · ` : ''}{order.order_number} — кол-во {order.quantity}, срок {order.due_date ? new Date(order.due_date).toLocaleDateString('ru-RU') : '—'}
            </span>
            <button
              type="button"
              disabled={!!releasingId || !systemReady}
              onClick={() => handleRelease(order.id)}
              className="shrink-0 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              title={!systemReady ? 'Сначала довнесите маршруты и правила для всех ГП' : undefined}
            >
              {releasingId === order.id ? '…' : 'Выпустить'}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};
