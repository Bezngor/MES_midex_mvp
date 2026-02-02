/**
 * Страница расписания производства
 * Этап 1: заказы из 1С (SHIP) → выпуск в производство → задачи в Ганте.
 * Перед выпуском проверяется полнота маршрутов и правил выбора РЦ для всех ГП.
 */

import React, { useState } from 'react';
import { GanttChart } from '../components/scheduling/GanttChart';
import { ReleasedOrdersBlock } from '../components/scheduling/ReleasedOrdersBlock';
import { ReleaseOrdersBlock } from '../components/scheduling/ReleaseOrdersBlock';
import { RoutesAndRulesValidationBlock } from '../components/scheduling/RoutesAndRulesValidationBlock';
import { devAPI } from '../services/api';

export const SchedulePage: React.FC = () => {
  const [systemReady, setSystemReady] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [resetMessage, setResetMessage] = useState<string | null>(null);

  const handleResetAll = async () => {
    if (!window.confirm('Очистить все таблицы БД? После сброса нужно заново выполнить prepare_test_env (или миграции + seed + загрузку данных).')) return;
    setResetting(true);
    setResetMessage(null);
    try {
      const res = await devAPI.resetAllTables();
      if (res.success && res.data?.message) {
        setResetMessage(res.data.message);
        window.location.reload();
      } else {
        setResetMessage(res.error ?? 'Ошибка сброса');
      }
    } catch (e) {
      setResetMessage('Ошибка запроса: ' + (e instanceof Error ? e.message : String(e)));
    } finally {
      setResetting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex flex-wrap items-center justify-between gap-2">
          <h1 className="text-2xl font-bold text-gray-800">Расписание производства</h1>
          {import.meta.env.DEV && (
            <button
              type="button"
              disabled={resetting}
              onClick={handleResetAll}
              className="px-3 py-1.5 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
              title="Только для тестовой версии. В production эта кнопка не отображается."
            >
              {resetting ? 'Сброс…' : 'Сбросить все данные (только для теста)'}
            </button>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {resetMessage && (
          <div className="mb-4 p-3 rounded bg-green-100 text-green-800 text-sm">
            {resetMessage}
          </div>
        )}
        <RoutesAndRulesValidationBlock onValidationChange={(ok) => setSystemReady(ok)} />
        <ReleaseOrdersBlock systemReady={systemReady} />
        <ReleasedOrdersBlock />
        <GanttChart />
      </main>
    </div>
  );
};
