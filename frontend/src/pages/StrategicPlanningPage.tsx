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
import { PriorityFilters, Priority, priorityLabels } from '../components/strategic/PriorityFilters';
import { ordersAPI } from '../services/api';
import type { OrderChangeInfo, ReservationMissingDetail, MassValidationError, MassPlanningInfo } from '../types/api';
import { Loading } from '../components/common/Loading';
import { Error } from '../components/common/Error';
import { useScheduleStore } from '../store/useScheduleStore';

const STORAGE_KEY_ACCEPTED_IDS = 'mes_strategic_accepted_order_ids';

function loadAcceptedOrderIdsFromStorage(): Set<string> {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY_ACCEPTED_IDS);
    if (raw) {
      const arr = JSON.parse(raw) as unknown;
      if (Array.isArray(arr)) {
        return new Set(arr.filter((id): id is string => typeof id === 'string'));
      }
    }
  } catch {
    // ignore
  }
  return new Set();
}

function saveAcceptedOrderIdsToStorage(ids: Set<string>): void {
  try {
    sessionStorage.setItem(STORAGE_KEY_ACCEPTED_IDS, JSON.stringify([...ids]));
  } catch {
    // ignore
  }
}

/** Нормализует UUID к 32 символам hex (без дефисов) для надёжного сравнения независимо от формата API. */
function normalizeOrderIdForMatch(id: string | null | undefined): string {
  if (id == null || typeof id !== 'string') return '';
  const s = String(id).trim().toLowerCase().replace(/-/g, '');
  return /^[0-9a-f]{32}$/.test(s) ? s : String(id).trim().toLowerCase();
}

export const StrategicPlanningPage: React.FC = () => {
  const { ganttData } = useScheduleStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newOrders, setNewOrders] = useState<OrderChangeInfo[]>([]);
  const [changedOrders, setChangedOrders] = useState<OrderChangeInfo[]>([]);
  const [acceptedOrderIds, setAcceptedOrderIds] = useState<Set<string>>(loadAcceptedOrderIdsFromStorage);
  const [selectedPriorities, setSelectedPriorities] = useState<Priority[]>([]);
  const [selectedOrderNumbers, setSelectedOrderNumbers] = useState<string[]>([]);
  const [ganttRefreshTrigger, setGanttRefreshTrigger] = useState(0);
  /** Ошибки резервирования после последнего пересчёта (для drill-down). */
  const [lastFailedOrders, setLastFailedOrders] = useState<Array<{
    order_id: string;
    order_number?: string;
    order_product_name?: string;
    missing_components: Record<string, number>;
    missing_details?: ReservationMissingDetail[];
  }>>([]);
  const [resetLoading, setResetLoading] = useState(false);
  const [newOrdersCollapsed, setNewOrdersCollapsed] = useState(false);
  const [changedOrdersCollapsed, setChangedOrdersCollapsed] = useState(false);
  /** Ошибки валидации маршрутов масс после последнего пересчёта. */
  const [massValidationErrors, setMassValidationErrors] = useState<MassValidationError[]>([]);
  /** Информация о массах для анализа отсутствия задач на Реакторе. */
  const [massPlanningInfo, setMassPlanningInfo] = useState<MassPlanningInfo[]>([]);

  /**
   * Номер заказа без суффикса: убирается только короткий суффикс вида -1, -2 (добавляемый
   * загрузчиком при дубликатах номера). Основной номер типа НФ00-003531 не обрезается.
   */
  const orderNumberWithoutSuffix = (orderNumber: string | undefined): string => {
    if (!orderNumber) return '';
    const m = orderNumber.match(/^(.+)-(\d{1,3})$/);
    return m ? m[1] : orderNumber;
  };

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

  // Сохраняем принятые ID в sessionStorage, чтобы при возврате на вкладку отметки «Принять» сохранялись
  useEffect(() => {
    saveAcceptedOrderIdsToStorage(acceptedOrderIds);
  }, [acceptedOrderIds]);

  // Обработка принятия/отмены заказа
  const handleAccept = (orderId: string) => {
    const normalized = normalizeOrderIdForMatch(orderId);
    const next = new Set(acceptedOrderIds);
    next.add(orderId);
    if (normalized.length > 0) next.add(normalized);
    setAcceptedOrderIds(next);
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

  // Фильтр по номерам заказов (без суффикса)
  const filterOrdersByOrderNumbers = (orders: OrderChangeInfo[]): OrderChangeInfo[] => {
    if (selectedOrderNumbers.length === 0) return orders;
    const set = new Set(selectedOrderNumbers);
    return orders.filter((o) => set.has(orderNumberWithoutSuffix(o.order_number)));
  };

  // Фильтрованные списки: сначала по приоритетам, затем по номерам заказов
  const afterPriorityNew = filterOrdersByPriority(newOrders);
  const afterPriorityChanged = filterOrdersByPriority(changedOrders);
  const filteredNewOrders = filterOrdersByOrderNumbers(afterPriorityNew);
  const filteredChangedOrders = filterOrdersByOrderNumbers(afterPriorityChanged);

  // Уникальные номера заказов (без суффикса) для выпадающего списка
  const allOrderNumbersBase = Array.from(
    new Set([
      ...afterPriorityNew.map((o) => orderNumberWithoutSuffix(o.order_number)),
      ...afterPriorityChanged.map((o) => orderNumberWithoutSuffix(o.order_number)),
    ].filter(Boolean))
  ).sort();

  const getOrderNumberDisplay = (order: OrderChangeInfo): string =>
    orderNumberWithoutSuffix(order.order_number) || '-';

  // Принять все отфильтрованные / Отменить все отфильтрованные
  const handleAcceptAll = () => {
    const ids = new Set<string>();
    filteredNewOrders.forEach((o) => ids.add(o.order_id ?? o.order_number ?? ''));
    filteredChangedOrders.forEach((o) => ids.add(o.order_id ?? o.order_number ?? ''));
    ids.delete('');
    setAcceptedOrderIds((prev) => new Set([...prev, ...ids]));
  };

  const handleCancelAll = () => {
    const toRemove = new Set<string>();
    filteredNewOrders.forEach((o) => toRemove.add(o.order_id ?? o.order_number ?? ''));
    filteredChangedOrders.forEach((o) => toRemove.add(o.order_id ?? o.order_number ?? ''));
    toRemove.delete('');
    setAcceptedOrderIds((prev) => {
      const next = new Set(prev);
      toRemove.forEach((id) => next.delete(id));
      return next;
    });
  };

  const hasAcceptedInFiltered =
    filteredNewOrders.some((o) => acceptedOrderIds.has(o.order_id ?? o.order_number ?? '')) ||
    filteredChangedOrders.some((o) => acceptedOrderIds.has(o.order_id ?? o.order_number ?? ''));

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
        .map((order) => order.order_id != null ? String(order.order_id).trim() : null)
        .filter((id): id is string => id != null && (id.length === 36 || id.length === 32) && /^[0-9a-fA-F-]+$/.test(id));

      if (orderIds.length === 0) {
        setError('Не удалось получить ID заказов для планирования');
        return;
      }

      const response = await ordersAPI.recalculatePlan(orderIds);

      if (response.success && response.data) {
        const result = response.data;
        const reservedOrderIds = (result.reserved_orders || []).map((id) =>
          normalizeOrderIdForMatch(String(id))
        );
        const reservedSet = new Set(reservedOrderIds.filter((s) => s.length > 0));
        const failed = result.failed_orders || [];
        const massValidationErrs = result.mass_validation_errors || [];
        const massPlanningInf = result.mass_planning_info || [];

        // Сохраняем информацию о массах для анализа отсутствия задач на Реакторе
        setMassValidationErrors(massValidationErrs);
        setMassPlanningInfo(massPlanningInf);

        const isReserved = (o: OrderChangeInfo) => {
          const normalized = normalizeOrderIdForMatch(o.order_id ?? '');
          return normalized.length > 0 && reservedSet.has(normalized);
        };

        const newNewOrders = newOrders.filter((o) => !isReserved(o));
        const newChangedOrders = changedOrders.filter((o) => !isReserved(o));
        const removedOrders = [
          ...newOrders.filter((o) => isReserved(o)),
          ...changedOrders.filter((o) => isReserved(o)),
        ];

        // Формируем сообщение об ошибках
        let alertMessage = '';
        if (massValidationErrs.length > 0) {
          alertMessage += `КРИТИЧЕСКАЯ ОШИБКА: Ошибки валидации маршрутов масс (${massValidationErrs.length}):\n`;
          massValidationErrs.forEach((err) => {
            alertMessage += `- Для массы "${err.mass_product_name}" в заказе ${err.order_number}: ${err.reason}\n`;
          });
          alertMessage += '\n';
        }

        if (failed.length > 0) {
          setLastFailedOrders(failed);
          alertMessage += `Пересчёт завершён.\nУспешно зарезервировано: ${(result.reserved_orders || []).length} заказов.\nОшибки резервирования: ${failed.length} заказов.\n\nПодробности — в блоке «Ошибки резервирования» ниже.`;
        } else {
          setLastFailedOrders([]);
          alertMessage = alertMessage || `Пересчёт завершён успешно. Зарезервировано: ${(result.reserved_orders || []).length} заказов.`;
        }

        if (alertMessage) {
          alert(alertMessage);
        }

        setNewOrders(newNewOrders);
        setChangedOrders(newChangedOrders);
        setAcceptedOrderIds((prev) => {
          const next = new Set(prev);
          removedOrders.forEach((o) => {
            if (o.order_id != null) {
              const idStr = String(o.order_id);
              next.delete(idStr);
              next.delete(idStr.toLowerCase());
              next.delete(normalizeOrderIdForMatch(o.order_id));
            }
            if (o.order_number) next.delete(o.order_number);
          });
          reservedOrderIds.forEach((id) => next.delete(id));
          return next;
        });
        setGanttRefreshTrigger((t) => t + 1);
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

  const handleResetPlan = async () => {
    if (!window.confirm('Сбросить все резервы и запланированные задачи (Гант)? Заказы останутся в списках, отметки «Принять» будут сброшены.')) {
      return;
    }
    setResetLoading(true);
    setError(null);
    try {
      const response = await ordersAPI.resetPlan();
      if (response.success && response.data) {
        setAcceptedOrderIds(new Set());
        saveAcceptedOrderIdsToStorage(new Set());
        setLastFailedOrders([]);
        setMassValidationErrors([]);
        setMassPlanningInfo([]);
        setGanttRefreshTrigger((t) => t + 1);
        alert(`Сброс выполнен: удалено задач — ${response.data.tasks_deleted}, обнулено резервов — ${response.data.reserves_cleared}.`);
      } else {
        setError(response.error || 'Ошибка при сбросе плана');
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
            : 'Ошибка при сбросе плана';
      setError(msg);
    } finally {
      setResetLoading(false);
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

        {/* Ошибки резервирования (drill-down) */}
        {lastFailedOrders.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-amber-900 mb-2">
              Ошибки резервирования ({lastFailedOrders.length} заказов)
            </h3>
            <p className="text-sm text-amber-800 mb-3">
              Резервирование компонентов BOM не выполнено. Возможные причины: для продукта нет BOM в системе;
              недостаточно остатков на складе (сырьё, масса, тара). Загрузите остатки (см. DATA_LOAD_CSV.md)
              и проверьте наличие BOM для ГП.
            </p>
            <ul className="list-none space-y-4 text-sm text-amber-900">
              {lastFailedOrders.map((fo) => {
                const details = fo.missing_details || [];
                const orderLabel = fo.order_product_name || fo.order_number || fo.order_id;
                return (
                  <li key={fo.order_id} className="border-b border-amber-200 pb-3 last:border-0 last:pb-0">
                    <div className="font-medium text-amber-900 mb-1">
                      {fo.order_number && <span className="text-amber-800">{fo.order_number}</span>}
                      {fo.order_number && fo.order_product_name && ' — '}
                      {fo.order_product_name && <span>{fo.order_product_name}</span>}
                      {!fo.order_product_name && !fo.order_number && (
                        <code className="bg-amber-100 px-1 rounded">{fo.order_id}</code>
                      )}
                    </div>
                    {details.length > 0 ? (
                      <table className="w-full max-w-2xl border border-amber-200 rounded overflow-hidden text-left">
                        <thead>
                          <tr className="bg-amber-100/80">
                            <th className="px-2 py-1.5 font-medium">Компонент</th>
                            <th className="px-2 py-1.5 font-medium text-right">На остатке</th>
                            <th className="px-2 py-1.5 font-medium text-right">Потребность</th>
                            <th className="px-2 py-1.5 font-medium text-right">Дефицит</th>
                          </tr>
                        </thead>
                        <tbody>
                          {details.map((d) => (
                            <tr key={d.component_id} className="border-t border-amber-200">
                              <td className="px-2 py-1.5">{d.component_name}</td>
                              <td className="px-2 py-1.5 text-right">{d.available_qty}</td>
                              <td className="px-2 py-1.5 text-right">{d.required_qty}</td>
                              <td className="px-2 py-1.5 text-right font-medium text-amber-900">{d.deficit_qty}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <p className="text-amber-800">Нет BOM или некорректный продукт.</p>
                    )}
                  </li>
                );
              })}
            </ul>
            <button
              type="button"
              onClick={() => setLastFailedOrders([])}
              className="mt-3 text-sm text-amber-700 hover:text-amber-900 underline"
            >
              Скрыть блок
            </button>
          </div>
        )}

        {/* Ошибки валидации маршрутов масс */}
        {massValidationErrors.length > 0 && (
          <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-red-900 mb-3">
              ⚠️ Критические ошибки валидации маршрутов масс
            </h3>
            <p className="text-sm text-red-800 mb-3">
              Планирование заблокировано из-за отсутствия маршрутов или операций для масс. Необходимо исправить данные в БД перед повторным планированием.
            </p>
            <ul className="space-y-3">
              {massValidationErrors.map((err) => (
                <li key={`${err.mass_product_id}-${err.order_id}`} className="border-b border-red-200 pb-3 last:border-0 last:pb-0">
                  <div className="font-medium text-red-900 mb-1">
                    Масса: <span className="font-semibold">{err.mass_product_name}</span> (ID: <code className="bg-red-100 px-1 rounded">{err.mass_product_id}</code>)
                  </div>
                  <div className="text-sm text-red-800 mb-1">
                    Заказ: <span className="font-medium">{err.order_number}</span> (ID: <code className="bg-red-100 px-1 rounded">{err.order_id}</code>)
                  </div>
                  <div className="text-sm text-red-900 font-medium">
                    Причина: {err.reason}
                  </div>
                </li>
              ))}
            </ul>
            <button
              type="button"
              onClick={() => setMassValidationErrors([])}
              className="mt-3 text-sm text-red-700 hover:text-red-900 underline"
            >
              Скрыть блок
            </button>
          </div>
        )}

        {/* Проверка отсутствия задач на Реакторе */}
        {ganttData && massPlanningInfo.length > 0 && (() => {
          // Проверяем, есть ли задачи на Реакторе (WC_REACTOR_MAIN)
          const reactorWC = ganttData.work_centers.find(
            (wc) => wc.name === 'WC_REACTOR_MAIN' || wc.id === '00000000-0000-0000-0000-000000000001'
          );
          const hasReactorTasks = reactorWC && reactorWC.tasks.length > 0;
          
          // Если задач нет, но есть массы, которые требовались для производства
          const massesNeedingProduction = massPlanningInfo.filter((info) => info.needs_production);
          
          if (!hasReactorTasks && massesNeedingProduction.length > 0) {
            return (
              <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-blue-900 mb-3">
                  ℹ️ На Ганте нет задач на Реакторе
                </h3>
                <p className="text-sm text-blue-800 mb-3">
                  Возможные причины отсутствия задач на Реакторе:
                </p>
                <ul className="space-y-2 mb-3">
                  {massesNeedingProduction.map((info) => (
                    <li key={`${info.mass_product_id}-${info.order_id}`} className="border-b border-blue-200 pb-2 last:border-0 last:pb-0">
                      <div className="text-sm text-blue-900">
                        <span className="font-medium">Масса:</span> {info.mass_product_name} (заказ {info.order_number})
                      </div>
                      <div className="text-xs text-blue-700 mt-1 ml-4">
                        {!info.has_route && (
                          <div className="text-red-700">❌ Отсутствует маршрут производства</div>
                        )}
                        {info.has_route && !info.has_operations && (
                          <div className="text-red-700">❌ В маршруте отсутствуют операции</div>
                        )}
                        {info.has_route && info.has_operations && (
                          <div className="text-green-700">✓ Маршрут и операции есть ({info.operations_count} операций)</div>
                        )}
                        <div className="mt-1">
                          Потребность: {info.required_qty} кг, На остатке: {info.available_qty} кг
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
                <button
                  type="button"
                  onClick={() => setMassPlanningInfo([])}
                  className="text-sm text-blue-700 hover:text-blue-900 underline"
                >
                  Скрыть блок
                </button>
              </div>
            );
          }
          return null;
        })()}

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
                Показаны заказы с приоритетами: {selectedPriorities.map((p) => priorityLabels[p]).join(', ')}
              </p>
            )}
          </div>
        )}

        {/* Фильтр по номерам заказов и кнопки Принять все / Отменить все */}
        {(newOrders.length > 0 || changedOrders.length > 0) && (
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">
              Номера заказов и действия
            </h3>
            <div className="flex flex-wrap items-start gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Фильтр по номерам заказов (множественный выбор)
                </label>
                <div className="flex items-center gap-2">
                  <select
                    multiple
                    size={Math.min(8, Math.max(3, allOrderNumbersBase.length))}
                    className="border rounded px-2 py-1 min-w-[180px] text-sm"
                    value={selectedOrderNumbers}
                    onChange={(e) => {
                      const opts = Array.from(e.target.selectedOptions, (o) => o.value);
                      setSelectedOrderNumbers(opts);
                    }}
                  >
                    {allOrderNumbersBase.map((num) => (
                      <option key={num} value={num}>
                        {num}
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={() => setSelectedOrderNumbers([])}
                    className="px-3 py-1.5 text-sm font-medium rounded border border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
                  >
                    Сбросить фильтр
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Ctrl+клик — несколько номеров. Пусто = показаны все. Кнопка «Сбросить фильтр» возвращает к отображению всех заказов.
                </p>
              </div>
              <div className="flex items-end gap-2">
                <button
                  onClick={handleAcceptAll}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium"
                >
                  Принять все
                </button>
                <button
                  onClick={handleCancelAll}
                  disabled={!hasAcceptedInFiltered}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
                >
                  Отменить все
                </button>
              </div>
            </div>
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
              getOrderNumber={getOrderNumberDisplay}
              getPriority={getOrderPriority}
              getQuantity={getOrderQuantity}
              getDueDate={getOrderDueDate}
              collapsed={newOrdersCollapsed}
              onToggleCollapse={() => setNewOrdersCollapsed(!newOrdersCollapsed)}
            />

            {/* Список изменённых заказов */}
            <ChangedOrdersList
              orders={filteredChangedOrders}
              acceptedOrderIds={acceptedOrderIds}
              onAccept={handleAccept}
              onCancel={handleCancel}
              getOrderNumber={getOrderNumberDisplay}
              getPriority={getOrderPriority}
              collapsed={changedOrdersCollapsed}
              onToggleCollapse={() => setChangedOrdersCollapsed(!changedOrdersCollapsed)}
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

        {/* Сброс плана и резервов */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-800">
                Сброс к начальному состоянию
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Обнулить все резервы остатков и удалить запланированные задачи с Ганта. Отметки «Принять» в списках заказов будут сброшены.
              </p>
            </div>
            <button
              type="button"
              onClick={handleResetPlan}
              disabled={resetLoading}
              className="px-6 py-2 bg-amber-600 text-white rounded-md hover:bg-amber-700 disabled:bg-gray-400 font-medium"
            >
              {resetLoading ? 'Выполняется...' : 'Сбросить план и резервы'}
            </button>
          </div>
        </div>

        {/* Гант-диаграмма с утверждёнными заданиями */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Утверждённый план производства
          </h2>
          <GanttChart refreshTrigger={ganttRefreshTrigger} defaultDays={14} />
          <p className="mt-2 text-xs text-gray-500">
            План привязан к срокам заказов; по умолчанию показано 14 дней. Если задачи не видны — выберите 30 дней в выпадающем списке.
          </p>
        </div>
      </main>
    </div>
  );
};
