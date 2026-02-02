/**
 * Компонент детального просмотра изменений заказа (drill-down).
 */

import React, { useState, useEffect } from 'react';
import { ordersAPI } from '../../services/api';
import type { OrderChangeInfo } from '../../types/api';
import { Loading } from '../common/Loading';
import { Error } from '../common/Error';
import { Modal } from '../common/Modal';

interface OrderChangesDetailProps {
  orderId: string;
  onClose: () => void;
}

export const OrderChangesDetail: React.FC<OrderChangesDetailProps> = ({ orderId, onClose }) => {
  const [data, setData] = useState<OrderChangeInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDetails = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await ordersAPI.getChangeDetails(orderId);
        if (response.success && response.data) {
          setData(response.data);
        } else {
          setError('Детали изменений не найдены');
        }
      } catch (e: unknown) {
        const msg =
          e != null &&
          typeof e === 'object' &&
          'message' in e &&
          typeof (e as { message: unknown }).message === 'string'
            ? (e as { message: string }).message
            : typeof e === 'string'
              ? e
              : 'Ошибка при загрузке деталей изменений';
        setError(msg);
      } finally {
        setLoading(false);
      }
    };

    loadDetails();
  }, [orderId]);

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('ru-RU');
  };

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'boolean') return value ? 'Да' : 'Нет';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  };

  const getFieldLabel = (field: string): string => {
    const labels: Record<string, string> = {
      product_id: 'Продукт',
      quantity: 'Количество',
      status: 'Статус',
      due_date: 'Дата выполнения',
      order_type: 'Тип заказа',
      priority: 'Приоритет',
      source_status: 'Статус источника',
      parent_order_id: 'Родительский заказ',
      is_consolidated: 'Консолидированный',
    };
    return labels[field] || field;
  };

  return (
    <Modal isOpen={true} onClose={onClose} title="Детали изменений заказа">
      {loading && <Loading />}
      {error && <Error message={error} />}
      {data && !loading && !error && (
        <div className="space-y-4">
          {/* Основная информация */}
          <div className="bg-gray-50 rounded-lg p-4 space-y-2">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-sm text-gray-600">Номер заказа:</span>
                <div className="font-medium">{data.order_number}</div>
              </div>
              <div>
                <span className="text-sm text-gray-600">Продукт:</span>
                <div className="font-medium">{data.product_name || data.product_id}</div>
              </div>
              {data.is_new && (
                <div className="col-span-2">
                  <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm font-medium">
                    Новый заказ
                  </span>
                </div>
              )}
              {data.is_changed && (
                <div className="col-span-2">
                  <span className="inline-block px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-sm font-medium">
                    Изменённый заказ
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Детали изменений */}
          {data.changes && Object.keys(data.changes).length > 0 && (
            <div>
              <h4 className="text-md font-semibold text-gray-800 mb-3">Изменённые поля:</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Поле</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Старое значение</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Новое значение</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {Object.entries(data.changes).map(([field, [oldValue, newValue]]) => (
                      <tr key={field}>
                        <td className="px-4 py-2 text-sm font-medium text-gray-900">
                          {getFieldLabel(field)}
                        </td>
                        <td className="px-4 py-2 text-sm text-gray-600">
                          <span className="bg-red-50 text-red-800 px-2 py-1 rounded">
                            {formatValue(oldValue)}
                          </span>
                        </td>
                        <td className="px-4 py-2 text-sm text-gray-600">
                          <span className="bg-green-50 text-green-800 px-2 py-1 rounded">
                            {formatValue(newValue)}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Метаданные */}
          <div className="text-sm text-gray-600 space-y-1">
            {data.last_snapshot_date && (
              <div>Последний снимок: {formatDate(data.last_snapshot_date)}</div>
            )}
            {data.current_updated_at && (
              <div>Обновлён: {formatDate(data.current_updated_at)}</div>
            )}
          </div>

          {/* Кнопка закрытия */}
          <div className="flex justify-end pt-4 border-t">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 font-medium"
            >
              Закрыть
            </button>
          </div>
        </div>
      )}
    </Modal>
  );
};
