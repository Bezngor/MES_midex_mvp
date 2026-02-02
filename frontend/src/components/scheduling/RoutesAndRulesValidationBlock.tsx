/**
 * Блок проверки готовности системы: у всех ГП есть маршруты и правила выбора РЦ.
 * Если есть пропуски — показываем список ГП и в каких «файлах» нет записей; блокируем выпуск заказов.
 * Кнопка «Проверить снова» после довнесения данных.
 */

import React, { useEffect, useState } from 'react';
import { validationAPI, type RoutesAndRulesValidationData } from '../../services/api';

export const RoutesAndRulesValidationBlock: React.FC<{
  onValidationChange?: (ok: boolean, data: RoutesAndRulesValidationData | null) => void;
}> = ({ onValidationChange }) => {
  const [data, setData] = useState<RoutesAndRulesValidationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchValidation = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await validationAPI.getRoutesAndRules();
      if (res.success && res.data) {
        setData(res.data);
        onValidationChange?.(res.data.ok, res.data);
      } else {
        setData(null);
        onValidationChange?.(false, null);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка проверки');
      setData(null);
      onValidationChange?.(false, null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchValidation();
  }, []);

  if (loading && !data) {
    return (
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <p className="text-sm text-gray-500">Проверка маршрутов и правил выбора РЦ…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-lg shadow p-4 mb-6">
        <p className="text-sm text-amber-800">{error}</p>
        <button
          type="button"
          onClick={fetchValidation}
          className="mt-2 px-3 py-1 text-sm bg-amber-600 text-white rounded hover:bg-amber-700"
        >
          Проверить снова
        </button>
      </div>
    );
  }

  if (data?.ok) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg shadow p-4 mb-6">
        <p className="text-sm text-green-800 font-medium">
          Система готова к запуску: у всех {data.product_count} ГП есть записи в маршрутах и в правилах выбора РЦ.
        </p>
        <button
          type="button"
          onClick={fetchValidation}
          className="mt-2 px-3 py-1 text-sm bg-green-700 text-white rounded hover:bg-green-800"
        >
          Проверить снова
        </button>
      </div>
    );
  }

  const missingDetails = data?.details?.filter((d) => !d.in_routes || !d.in_rules) ?? [];

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg shadow p-4 mb-6">
      <h3 className="text-lg font-semibold text-red-800 mb-2">
        Система не готова к запуску
      </h3>
      <p className="text-sm text-red-700 mb-3">
        Для следующих ГП отсутствуют записи в маршрутах и/или в правилах выбора РЦ. Довнесите данные и нажмите «Проверить снова». Выпуск заказов в производство заблокирован.
      </p>
      <p className="text-sm text-red-700 mb-2">
        Диагностика: ГП всего — {data.product_count}, с маршрутами — {data.routes_ok_count}, с правилами — {data.rules_ok_count}. Маршрутов с операциями в БД — {data.routes_with_ops_count ?? '—'}.
      </p>
      {data.routes_with_ops_count === 0 && (
        <p className="text-sm text-red-600 mb-3 bg-amber-100/80 rounded px-2 py-1.5">
          Маршрутов с операциями в БД нет (0). Убедитесь, что <strong>backend подключён к той же БД</strong>, в которую вы загружали данные: скрипты с хоста пишут в localhost; backend в Docker читает из контейнера postgres. Либо перезапустите backend после загрузки маршрутов.
        </p>
      )}
      <p className="text-sm text-red-600 mb-3 bg-red-100/50 rounded px-2 py-1.5">
        Если вы только что загрузили датасет из CSV (<code className="bg-red-200/70 px-0.5 rounded">load_dataset_from_csv</code>), маршруты и правила при этом очищаются. Выполните: 1) <code className="bg-red-200/70 px-0.5 rounded">seed_work_centers_and_routes</code>, 2) <code className="bg-red-200/70 px-0.5 rounded">load_routes_from_csv</code> (см. DATA_LOAD_CSV.md).
      </p>
      <div className="overflow-x-auto max-h-64 overflow-y-auto mb-3">
        <table className="min-w-full text-sm border border-red-200 rounded">
          <thead>
            <tr className="bg-red-100 text-red-900">
              <th className="px-3 py-2 text-left">Код ГП</th>
              <th className="px-3 py-2 text-left">Наименование</th>
              <th className="px-3 py-2 text-center">Нет в маршрутах</th>
              <th className="px-3 py-2 text-center">Нет в правилах</th>
            </tr>
          </thead>
          <tbody>
            {missingDetails.map((d) => (
              <tr key={d.product_code} className="border-t border-red-200 bg-white">
                <td className="px-3 py-2 font-mono">{d.product_code}</td>
                <td className="px-3 py-2 truncate max-w-xs" title={d.product_name ?? undefined}>
                  {d.product_name ?? '—'}
                </td>
                <td className="px-3 py-2 text-center">{d.in_routes ? '—' : 'да'}</td>
                <td className="px-3 py-2 text-center">{d.in_rules ? '—' : 'да'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <button
        type="button"
        onClick={fetchValidation}
        className="px-3 py-1.5 text-sm bg-red-600 text-white rounded hover:bg-red-700"
      >
        Проверить снова
      </button>
    </div>
  );
};
