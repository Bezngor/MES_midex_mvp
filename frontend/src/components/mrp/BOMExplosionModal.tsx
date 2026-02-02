/**
 * Модальное окно «Взрыв BOM» для вкладки MRP.
 * Показывает потребность в компонентах по выбранному ГП и количеству.
 * Верхний уровень — прямые компоненты ГП; компоненты с подуровнем (Масса и т.п.)
 * выделены и раскрываются по клику (группировка как в Excel).
 */

import React, { useCallback, useEffect, useState } from 'react';
import { mrpAPI, productsAPI, bomAPI } from '../../services/api';
import type { BOM, Product } from '../../services/types';

export interface BOMExplosionRow {
  productId: string;
  name: string;
  quantity: number;
  unit: string;
  /** Дочерние компоненты (следующий уровень BOM), если есть */
  children?: BOMExplosionRow[];
}

interface BOMExplosionModalProps {
  isOpen: boolean;
  onClose: () => void;
  productId: string;
  quantity: number;
  productName: string;
}

export const BOMExplosionModal: React.FC<BOMExplosionModalProps> = ({
  isOpen,
  onClose,
  productId,
  quantity,
  productName,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [treeRows, setTreeRows] = useState<BOMExplosionRow[]>([]);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const toggleExpanded = useCallback((id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  useEffect(() => {
    if (!isOpen || !productId) {
      setTreeRows([]);
      setExpandedIds(new Set());
      setError(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    (async () => {
      try {
        const [explosionRes, productsRes, bomFgRes] = await Promise.all([
          mrpAPI.explodeBOM(productId, quantity),
          productsAPI.getAll({ limit: 5000 }),
          bomAPI.getByProduct(productId),
        ]);
        if (cancelled) return;
        if (!explosionRes.success || !explosionRes.data) {
          setError(explosionRes.error ?? 'Ошибка расчёта потребности');
          setLoading(false);
          return;
        }
        const requirements: Record<string, number> = explosionRes.data.requirements ?? {};
        const products: Product[] = productsRes.success && productsRes.data ? productsRes.data : [];
        const byId = Object.fromEntries(products.map((p) => [p.id, p]));
        const bomRows: BOM[] = bomFgRes.success && bomFgRes.data ? bomFgRes.data : [];

        const toRow = (id: string): BOMExplosionRow => {
          const qty = requirements[id] ?? 0;
          const product = byId[id];
          return {
            productId: id,
            name: product?.product_name ?? product?.product_code ?? id,
            quantity: Math.round(qty * 100) / 100,
            unit: product?.unit_of_measure ?? '—',
          };
        };

        const roots: BOMExplosionRow[] = [];
        for (const bom of bomRows) {
          const childId = bom.child_product_id;
          const row = toRow(childId);
          const childBomRes = await bomAPI.getByProduct(childId);
          if (cancelled) return;
          const childBom: BOM[] = childBomRes.success && childBomRes.data ? childBomRes.data : [];
          if (childBom.length > 0) {
            row.children = childBom.map((b) => toRow(b.child_product_id));
          }
          roots.push(row);
        }

        if (roots.length === 0 && Object.keys(requirements).length > 0) {
          const fallback: BOMExplosionRow[] = Object.keys(requirements).map((id) => toRow(id));
          setTreeRows(fallback);
        } else {
          setTreeRows(roots);
        }
      } catch (e: unknown) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Ошибка загрузки');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [isOpen, productId, quantity]);

  if (!isOpen) return null;

  const hasAnyExpandable = treeRows.some((r) => (r.children?.length ?? 0) > 0);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div
        className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-800">
            Взрыв BOM: {productName}
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl leading-none"
            aria-label="Закрыть"
          >
            ×
          </button>
        </div>
        <div className="p-4 text-sm text-gray-600 border-b border-gray-100">
          Количество ГП: <strong>{quantity.toLocaleString('ru-RU')}</strong>
          {hasAnyExpandable && (
            <span className="ml-2 text-gray-500">
              — нажмите на строку с ▼, чтобы раскрыть состав
            </span>
          )}
        </div>
        <div className="p-4 overflow-auto flex-1">
          {loading && (
            <p className="text-gray-500">Расчёт потребности...</p>
          )}
          {error && (
            <p className="text-red-600">{error}</p>
          )}
          {!loading && !error && treeRows.length > 0 && (
            <table className="w-full border-collapse border border-gray-300">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold w-8" />
                  <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">
                    Наименование
                  </th>
                  <th className="border border-gray-300 p-2 text-right text-gray-800 font-semibold">
                    Количество
                  </th>
                  <th className="border border-gray-300 p-2 text-left text-gray-800 font-semibold">
                    Ед. изм.
                  </th>
                </tr>
              </thead>
              <tbody>
                {treeRows.map((row) => (
                  <React.Fragment key={row.productId}>
                    <tr
                      className={
                        (row.children?.length ?? 0) > 0
                          ? 'bg-blue-50/60 hover:bg-blue-100/80 cursor-pointer'
                          : 'hover:bg-gray-50'
                      }
                      onClick={() => (row.children?.length ?? 0) > 0 && toggleExpanded(row.productId)}
                    >
                      <td className="border border-gray-300 p-2 text-center w-8">
                        {(row.children?.length ?? 0) > 0 ? (
                          <span className="text-gray-600" aria-hidden>
                            {expandedIds.has(row.productId) ? '▼' : '▶'}
                          </span>
                        ) : (
                          <span className="text-gray-300">·</span>
                        )}
                      </td>
                      <td className="border border-gray-300 p-2 text-gray-900">
                        <span className={(row.children?.length ?? 0) > 0 ? 'font-medium' : ''}>
                          {row.name}
                        </span>
                      </td>
                      <td className="border border-gray-300 p-2 text-right text-gray-900">
                        {row.quantity.toLocaleString('ru-RU', {
                          minimumFractionDigits: 0,
                          maximumFractionDigits: 2,
                        })}
                      </td>
                      <td className="border border-gray-300 p-2 text-gray-700">{row.unit}</td>
                    </tr>
                    {expandedIds.has(row.productId) &&
                      (row.children ?? []).map((child) => (
                        <tr key={child.productId} className="hover:bg-gray-50 bg-gray-50/50">
                          <td className="border border-gray-300 p-2 w-8" />
                          <td className="border border-gray-300 p-2 pl-8 text-gray-700">
                            {child.name}
                          </td>
                          <td className="border border-gray-300 p-2 text-right text-gray-900">
                            {child.quantity.toLocaleString('ru-RU', {
                              minimumFractionDigits: 0,
                              maximumFractionDigits: 2,
                            })}
                          </td>
                          <td className="border border-gray-300 p-2 text-gray-700">{child.unit}</td>
                        </tr>
                      ))}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          )}
          {!loading && !error && treeRows.length === 0 && (
            <p className="text-gray-500">Нет компонентов в спецификации.</p>
          )}
        </div>
      </div>
    </div>
  );
};
