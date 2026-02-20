/**
 * Компонент дашборда MRP (Material Requirements Planning).
 *
 * Консолидация заказов: таблица с колонками URGENT / HIGH / NORMAL / LOW (количество по приоритетам)
 * и ИТОГО. Кнопки URGENT/HIGH/NORMAL/LOW включают/выключают соответствующие столбцы (множественный выбор).
 */

import React, { useEffect, useMemo, useState } from 'react';
import { useMRPStore } from '../../store/useMRPStore';
import { Loading } from '../common/Loading';
import { Error } from '../common/Error';
import { Button } from '../common/Button';
import { BOMExplosionModal } from './BOMExplosionModal';
import type { MRPConsolidation } from '../../services/types';

const PRIORITIES = ['URGENT', 'HIGH', 'NORMAL', 'LOW'] as const;
type PriorityKey = (typeof PRIORITIES)[number];

const PRIORITY_LABELS: Record<PriorityKey, string> = {
  URGENT: 'Срочно',
  HIGH: 'Высокий',
  NORMAL: 'Обычный',
  LOW: 'Низкий',
};

const PAGE_SIZE_OPTIONS = [10, 20, 50] as const;
const DEFAULT_PAGE_SIZE = 20;

const defaultVisibleColumns: Record<PriorityKey, boolean> = {
  URGENT: true,
  HIGH: true,
  NORMAL: true,
  LOW: true,
};

function formatQty(value: number): string {
  return value.toLocaleString('ru-RU', { maximumFractionDigits: 0 });
}

/** ИТОГО, Крайний срок и кол-во заказов только по выбранным колонкам приоритета */
function aggregateByVisibleColumns(
  order: MRPConsolidation,
  visible: Record<PriorityKey, boolean>
): { totalQty: number; earliestDue: string | null; orderCount: number } {
  let totalQty = 0;
  let earliestDue: string | null = null;
  let orderCount = 0;
  const qtyKey: Record<PriorityKey, keyof MRPConsolidation> = {
    URGENT: 'qty_urgent',
    HIGH: 'qty_high',
    NORMAL: 'qty_normal',
    LOW: 'qty_low',
  };
  const dateKey: Record<PriorityKey, keyof MRPConsolidation> = {
    URGENT: 'earliest_due_date_urgent',
    HIGH: 'earliest_due_date_high',
    NORMAL: 'earliest_due_date_normal',
    LOW: 'earliest_due_date_low',
  };
  const countKey: Record<PriorityKey, keyof MRPConsolidation> = {
    URGENT: 'order_count_urgent',
    HIGH: 'order_count_high',
    NORMAL: 'order_count_normal',
    LOW: 'order_count_low',
  };
  for (const p of PRIORITIES) {
    if (!visible[p]) continue;
    const q = (order[qtyKey[p]] as number) ?? 0;
    totalQty += q;
    const d = order[dateKey[p]] as string | null | undefined;
    if (q > 0 && d) {
      if (!earliestDue || new Date(d).getTime() < new Date(earliestDue).getTime()) {
        earliestDue = d;
      }
    }
    orderCount += (order[countKey[p]] as number) ?? 0;
  }
  return { totalQty, earliestDue, orderCount };
}

export const MRPDashboard: React.FC = () => {
  const { consolidatedOrders, loading, error, consolidateOrders } = useMRPStore();
  const [horizonDays, setHorizonDays] = useState(30);
  const [visibleColumns, setVisibleColumns] = useState<Record<PriorityKey, boolean>>(defaultVisibleColumns);
  const [bomModalOrder, setBomModalOrder] = useState<MRPConsolidation | null>(null);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    consolidateOrders(horizonDays);
  }, [horizonDays, consolidateOrders]);

  const sortedOrders = useMemo(
    () =>
      [...consolidatedOrders].sort(
        (a, b) =>
          new Date(a.earliest_due_date).getTime() - new Date(b.earliest_due_date).getTime()
      ),
    [consolidatedOrders]
  );

  const totalPages = Math.max(1, Math.ceil(sortedOrders.length / pageSize));
  const pageStart = (currentPage - 1) * pageSize;
  const paginatedOrders = useMemo(
    () => sortedOrders.slice(pageStart, pageStart + pageSize),
    [sortedOrders, pageStart, pageSize]
  );

  useEffect(() => {
    setCurrentPage(1);
  }, [pageSize, sortedOrders.length]);

  const toggleColumn = (p: PriorityKey) => {
    setVisibleColumns((prev) => ({ ...prev, [p]: !prev[p] }));
  };

  const visiblePriorityColumns = useMemo(
    () => PRIORITIES.filter((p) => visibleColumns[p]),
    [visibleColumns]
  );
  const totalTableColumns = 1 + visiblePriorityColumns.length + 3;

  if (loading) return <Loading message="Консолидация заказов..." />;
  if (error) return <Error message={error} onRetry={() => consolidateOrders(horizonDays)} />;

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-gray-800">MRP - Консолидация заказов</h2>
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

      <div className="mb-4 p-4 bg-blue-50 rounded-lg flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm text-gray-700">
          Найдено <strong>{consolidatedOrders.length}</strong> продуктов для производства
        </p>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">На странице:</span>
          <select
            value={pageSize}
            onChange={(e) => setPageSize(Number(e.target.value))}
            className="border rounded px-2 py-1 text-sm"
          >
            {PAGE_SIZE_OPTIONS.map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="mb-3 flex flex-wrap gap-2 items-center">
        <span className="text-sm text-gray-600">Колонки в таблице:</span>
        {PRIORITIES.map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => toggleColumn(p)}
            className={`px-3 py-1.5 rounded text-sm font-medium ${
              visibleColumns[p]
                ? p === 'URGENT'
                  ? 'bg-red-600 text-white'
                  : p === 'HIGH'
                    ? 'bg-orange-500 text-white'
                    : p === 'NORMAL'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-600 text-white'
                : 'bg-gray-200 text-gray-500'
            }`}
          >
            {PRIORITY_LABELS[p]} {visibleColumns[p] ? '✓' : ''}
          </button>
        ))}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-300">
          <thead className="bg-gray-100">
            <tr>
              <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">Продукт</th>
              {visibleColumns.URGENT && (
                <th className="border border-gray-300 p-2 text-right text-gray-800 font-semibold">{PRIORITY_LABELS.URGENT}</th>
              )}
              {visibleColumns.HIGH && (
                <th className="border border-gray-300 p-2 text-right text-gray-800 font-semibold">{PRIORITY_LABELS.HIGH}</th>
              )}
              {visibleColumns.NORMAL && (
                <th className="border border-gray-300 p-2 text-right text-gray-800 font-semibold">{PRIORITY_LABELS.NORMAL}</th>
              )}
              {visibleColumns.LOW && (
                <th className="border border-gray-300 p-2 text-right text-gray-800 font-semibold">{PRIORITY_LABELS.LOW}</th>
              )}
              <th className="border border-gray-300 p-2 text-right text-gray-800 font-semibold">ИТОГО</th>
              <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">Крайний срок</th>
              <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">Источник заказов</th>
            </tr>
          </thead>
          <tbody>
            {paginatedOrders.length === 0 ? (
              <tr>
                <td colSpan={totalTableColumns} className="border border-gray-300 p-4 text-center text-gray-500">
                  Нет заказов для консолидации
                </td>
              </tr>
            ) : (
              paginatedOrders.map((order, idx) => {
                const agg = aggregateByVisibleColumns(order, visibleColumns);
                return (
                  <tr key={order.product_id ?? idx} className="hover:bg-gray-50">
                    <td className="border border-gray-300 p-2">
                      <button
                        type="button"
                        onClick={() => setBomModalOrder(order)}
                        className="text-left text-blue-600 hover:text-blue-800 hover:underline font-medium"
                      >
                        {order.product_name ?? order.product_code ?? order.product_id}
                      </button>
                    </td>
                    {visibleColumns.URGENT && (
                      <td className="border border-gray-300 p-2 text-right text-gray-900">
                        {formatQty(order.qty_urgent ?? 0)}
                      </td>
                    )}
                    {visibleColumns.HIGH && (
                      <td className="border border-gray-300 p-2 text-right text-gray-900">
                        {formatQty(order.qty_high ?? 0)}
                      </td>
                    )}
                    {visibleColumns.NORMAL && (
                      <td className="border border-gray-300 p-2 text-right text-gray-900">
                        {formatQty(order.qty_normal ?? 0)}
                      </td>
                    )}
                    {visibleColumns.LOW && (
                      <td className="border border-gray-300 p-2 text-right text-gray-900">
                        {formatQty(order.qty_low ?? 0)}
                      </td>
                    )}
                    <td className="border border-gray-300 p-2 text-right text-gray-900 font-medium">
                      {formatQty(agg.totalQty)}
                    </td>
                    <td className="border border-gray-300 p-2 text-gray-900">
                      {agg.earliestDue ? new Date(agg.earliestDue).toLocaleDateString('ru-RU') : '—'}
                    </td>
                    <td className="border border-gray-300 p-2 text-gray-900">
                      <span className="text-sm text-gray-600">
                        {agg.orderCount} заказ(ов)
                      </span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {sortedOrders.length > 0 && (
        <div className="mt-3 flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Страница <strong>{currentPage}</strong> из <strong>{totalPages}</strong>
            {' '}
            (показано {pageStart + 1}–{Math.min(pageStart + pageSize, sortedOrders.length)} из {sortedOrders.length})
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage <= 1}
              className="px-3 py-1.5 rounded border bg-white text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Назад
            </button>
            <button
              type="button"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage >= totalPages}
              className="px-3 py-1.5 rounded border bg-white text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Вперёд
            </button>
          </div>
        </div>
      )}

      {bomModalOrder && (
        <BOMExplosionModal
          isOpen={!!bomModalOrder}
          onClose={() => setBomModalOrder(null)}
          productId={bomModalOrder.product_id}
          quantity={aggregateByVisibleColumns(bomModalOrder, visibleColumns).totalQty}
          productName={bomModalOrder.product_name ?? bomModalOrder.product_code ?? bomModalOrder.product_id}
        />
      )}
    </div>
  );
};
