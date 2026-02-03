/**
 * Страница стратегического планирования производства.
 * Реализует вкладку "Стратегия" из бизнес-процесса производства.
 * 
 * Основные элементы:
 * - Гант-диаграмма с утверждёнными заданиями
 * - Кнопка "Обновить заказы покупателей"
 * - Списки "Новые заказы" и "Изменённые заказы" с кнопками "Принять"/"Отменить"
 * - Фильтры по приоритетам (URGENT/HIGH/NORMAL/LOW)
 * - Кнопка "Пересчитать план"
 */

import React, { useState, useEffect } from 'react';
import { GanttChart } from '../components/scheduling/GanttChart';
import { OrdersListWithAccept } from '../components/strategic/OrdersListWithAccept';
import { ChangedOrdersList } from '../components/strategic/ChangedOrdersList';
import { PriorityFilters, Priority } from '../components/strategic/PriorityFilters';
import { ordersAPI } from '../services/api';
import type { OrderChangeInfo } from '../types/api';
import { Loading } from '../components/common/Loading';
import { Error } from '../components/common/Error';

export const StrategicPlanningPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newOrders, setNewOrders] = useState<OrderChangeInfo[]>([]);
  const [changedOrders, setChangedOrders] = useState<OrderChangeInfo[]>([]);
  const [acceptedOrderIds, setAcceptedOrderIds] = useState<Set<string>>(new Set());
  const [selectedPriorities, setSelectedPriorities] = useState<Priority[]>([]);

  // Загрузка изменений заказов
  const loadOrderChanges = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await ordersAPI.getChanges({
        order_type: 'CUSTOMER',
      });

      setNewOrders(response.new_orders || []);
      setChangedOrders(response.changed_orders || []);
    } catch (e) {
      const msg =
        e != null &&
        typeof e === 'object' &&
        'message' in e &&
        typeof (e as { message: unknown }).message === 'string'
          ? (e as { message: string }).message
          : typeof e === 'string'
            ? e
            : 'Ошибка при загрузке изменений заказов';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  // Загрузка при монтировании компонента
  useEffect(() => {
    loadOrderChanges();
  }, []);

  // Обработка принятия/отмены заказа
  const handleAccept = (orderId: string) => {
    setAcceptedOrderIds(new Set([...acceptedOrderIds, orderId]));
  };

  const handleCancel = (orderId: string) => {
    const newSet = new Set(acceptedOrderIds);
    newSet.delete(orderId);
    setAcceptedOrderIds(newSet);
  };

  // Фильтрация заказов по приоритетам
  const filterOrdersByPriority = (orders: OrderChangeInfo[]): OrderChangeInfo[] => {
    if (selectedPriorities.length === 0) {
      return orders;
    }
    return orders.filter((order) => {
      const priority = order.priority as Priority | undefined;
      return priority && selectedPriorities.includes(priority);
    });
  };

  // Получение приоритета заказа
  const getOrderPriority = (order: OrderChangeInfo): Priority | undefined => {
    return (order.priority as Priority | undefined) || undefined;
  };

  // Получение количества
  const getOrderQuantity = (order: OrderChangeInfo): number | string => {
    return order.quantity ?? '-';
  };

  // Получение даты выполнения
  const getOrderDueDate = (order: OrderChangeInfo): string | null => {
    return order.due_date || null;
  };

  // Фильтрованные списки
  const filteredNewOrders = filterOrdersByPriority(newOrders);
  const filteredChangedOrders = filterOrdersByPriority(changedOrders);

  // Обработка пересчёта плана
  const handleRecalculatePlan = async () => {
    const acceptedOrders = [...newOrders, ...changedOrders].filter((order) => {
      const orderId = order.order_id || order.order_number;
      return acceptedOrderIds.has(orderId);
    });

    if (acceptedOrders.length === 0) {
      alert('Выберите хотя бы один заказ для пересчёта плана');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const orderIds = acceptedOrders
        .map((order) => order.order_id)
        .filter((id): id is string => id != null && id.length === 36);

      if (orderIds.length === 0) {
        setError('Не удалось получить ID заказов для планирования');
        return;
      }

      const response = await ordersAPI.recalculatePlan(orderIds);

      if (response.success && response.data) {
        const result = response.data;

        // Показываем результаты
        if (result.failed_orders && result.failed_orders.length > 0) {
          alert(
            `Пересчёт завершён.\nУспешно зарезервировано: ${result.reserved_orders.length} заказов.\nОшибки резервирования: ${result.failed_orders.length} заказов.`
          );
          // TODO: Обновить UI для показа ошибок резервирования с drill-down
        } else {
          alert(`Пересчёт завершён успешно. Зарезервировано: ${result.reserved_orders.length} заказов.`);
        }

        // TODO: Обновить Гант-диаграмму с новыми операциями
        // TODO: Удалить принятые заказы из списков
      } else {
        setError(response.error || 'Ошибка при пересчёте плана');
      }
    } catch (e) {
      const msg =
        e != null &&
        typeof e === 'object' &&
        'message' in e &&
        typeof (e as { message: unknown }).message === 'string'
          ? (e as { message: string }).message
          : typeof e === 'string'
            ? e
            : 'Ошибка при пересчёте плана';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-800">Стратегическое планирование</h1>
          <p className="text-sm text-gray-600 mt-1">
            Вкладка "Стратегия" — оценка потребности в ГП и пересчёт плана производства
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Кнопка "Обновить заказы покупателей" */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-800">
                Обновление заказов покупателей
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Загрузить данные о заказах и выявить новые и изменённые заказы
              </p>
            </div>
            <button
              onClick={loadOrderChanges}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 font-medium"
            >
              {loading ? 'Загрузка...' : 'Обновить заказы покупателей'}
            </button>
          </div>
        </div>

        {/* Ошибка */}
        {error && (
          <Error
            message={error}
            onRetry={loadOrderChanges}
          />
        )}

        {/* Фильтры по приоритетам */}
        {(newOrders.length > 0 || changedOrders.length > 0) && (
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">
              Фильтры по приоритетам
            </h3>
            <PriorityFilters
              selectedPriorities={selectedPriorities}
              onChange={setSelectedPriorities}
            />
            {selectedPriorities.length > 0 && (
              <p className="text-sm text-gray-600 mt-2">
                Показаны заказы с приоритетами: {selectedPriorities.join(', ')}
              </p>
            )}
          </div>
        )}

        {/* Списки заказов */}
        {loading ? (
          <Loading />
        ) : (
          <>
            {/* Список новых заказов */}
            <OrdersListWithAccept
              orders={filteredNewOrders}
              acceptedOrderIds={acceptedOrderIds}
              onAccept={handleAccept}
              onCancel={handleCancel}
              title="Новые заказы"
              getPriority={getOrderPriority}
              getQuantity={getOrderQuantity}
              getDueDate={getOrderDueDate}
            />

            {/* Список изменённых заказов */}
            <ChangedOrdersList
              orders={filteredChangedOrders}
              acceptedOrderIds={acceptedOrderIds}
              onAccept={handleAccept}
              onCancel={handleCancel}
              getPriority={getOrderPriority}
            />

            {/* Сообщение, если нет заказов */}
            {filteredNewOrders.length === 0 &&
              filteredChangedOrders.length === 0 &&
              (newOrders.length > 0 || changedOrders.length > 0) && (
                <div className="bg-white rounded-lg shadow p-6 text-center">
                  <p className="text-gray-600">
                    Нет заказов с выбранными приоритетами. Измените фильтры или выберите все
                    приоритеты.
                  </p>
                </div>
              )}

            {newOrders.length === 0 && changedOrders.length === 0 && !loading && (
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <p className="text-gray-600">
                  Нет новых или изменённых заказов. Нажмите "Обновить заказы покупателей" для
                  загрузки данных.
                </p>
              </div>
            )}
          </>
        )}

        {/* Кнопка "Пересчитать план" */}
        {acceptedOrderIds.size > 0 && (
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-800">
                  Пересчёт плана производства
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  Принято заказов к планированию: {acceptedOrderIds.size}
                </p>
              </div>
              <button
                onClick={handleRecalculatePlan}
                className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium"
              >
                Пересчитать план
              </button>
            </div>
          </div>
        )}

        {/* Гант-диаграмма с утверждёнными заданиями */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Утверждённый план производства
          </h2>
          <GanttChart />
        </div>
      </main>
    </div>
  );
};
