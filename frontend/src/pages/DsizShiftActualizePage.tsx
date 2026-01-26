/**
 * Страница фактизации смен DSIZ
 */

import React, { useState } from 'react';
import { useShiftActualize } from '../hooks/useShiftActualize';
import { Loading } from '../components/common/Loading';
import { Error } from '../components/common/Error';

export const DsizShiftActualizePage: React.FC = () => {
  const { dispatchData, loading, error, runDispatching, clearError } = useShiftActualize();
  
  const [shiftDate, setShiftDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [shiftNum, setShiftNum] = useState<1 | 2>(1);
  const [orderIds, setOrderIds] = useState<string[]>([]);

  const handleRunDispatching = async () => {
    if (orderIds.length === 0) {
      alert('Выберите хотя бы один заказ');
      return;
    }
    
    clearError();
    const result = await runDispatching({
      manufacturing_order_ids: orderIds,
    });
    
    if (result) {
      console.log('Диспетчеризация выполнена:', result);
    }
  };

  const handleSaveFact = () => {
    // TODO: Реализовать сохранение фактических данных
    alert('Сохранение фактических данных будет реализовано в следующей версии');
  };

  const handlePrintShiftTask = () => {
    // TODO: Реализовать печать задания смены
    alert('Печать задания смены будет реализована в следующей версии');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-800">Фактизация смены</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Панель выбора смены */}
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">Параметры смены</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Дата смены
              </label>
              <input
                type="date"
                value={shiftDate}
                onChange={(e) => setShiftDate(e.target.value)}
                className="w-full border rounded px-3 py-2"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Номер смены
              </label>
              <select
                value={shiftNum}
                onChange={(e) => setShiftNum(parseInt(e.target.value) as 1 | 2)}
                className="w-full border rounded px-3 py-2"
              >
                <option value={1}>Смена 1</option>
                <option value={2}>Смена 2</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              ID заказов (через запятую)
            </label>
            <input
              type="text"
              value={orderIds.join(', ')}
              onChange={(e) => setOrderIds(e.target.value.split(',').map(id => id.trim()).filter(Boolean))}
              placeholder="uuid1, uuid2, uuid3"
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div className="flex gap-4 pt-4">
            <button
              onClick={handleRunDispatching}
              disabled={loading || orderIds.length === 0}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              {loading ? 'Запуск диспетчеризации...' : 'Запустить диспетчеризацию'}
            </button>
            
            <button
              onClick={handleSaveFact}
              disabled={!dispatchData || loading}
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              Сохранить факт
            </button>
            
            <button
              onClick={handlePrintShiftTask}
              disabled={!dispatchData || loading}
              className="px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              Напечатать задание смены
            </button>
          </div>
        </div>

        {/* Ошибки */}
        {error && (
          <Error
            message={error}
            onRetry={clearError}
          />
        )}

        {/* Загрузка */}
        {loading && <Loading message="Выполнение диспетчеризации..." />}

        {/* Результаты диспетчеризации */}
        {dispatchData && dispatchData.data && (
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-800">Результаты диспетчеризации</h2>
            
            {dispatchData.data.gantt_preview && dispatchData.data.gantt_preview.length > 0 && (
              <div>
                <h3 className="text-md font-medium text-gray-700 mb-2">Preview Gantt</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full border-collapse border border-gray-300">
                    <thead>
                      <tr>
                        <th className="border border-gray-300 p-2 bg-gray-50 text-left text-xs font-medium">Задача</th>
                        <th className="border border-gray-300 p-2 bg-gray-50 text-left text-xs font-medium">Рабочий центр</th>
                        <th className="border border-gray-300 p-2 bg-gray-50 text-left text-xs font-medium">Начало</th>
                        <th className="border border-gray-300 p-2 bg-gray-50 text-left text-xs font-medium">Окончание</th>
                        <th className="border border-gray-300 p-2 bg-gray-50 text-left text-xs font-medium">Длительность</th>
                        <th className="border border-gray-300 p-2 bg-gray-50 text-left text-xs font-medium">Переналадка</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dispatchData.data.gantt_preview.map((task) => (
                        <tr key={task.task_id}>
                          <td className="border border-gray-300 p-2 text-xs">{task.task_id}</td>
                          <td className="border border-gray-300 p-2 text-xs">{task.work_center_name}</td>
                          <td className="border border-gray-300 p-2 text-xs">
                            {new Date(task.task_start).toLocaleString('ru-RU')}
                          </td>
                          <td className="border border-gray-300 p-2 text-xs">
                            {new Date(task.task_end).toLocaleString('ru-RU')}
                          </td>
                          <td className="border border-gray-300 p-2 text-xs">{task.duration_hours.toFixed(2)} ч</td>
                          <td className="border border-gray-300 p-2 text-xs">{task.changeover_minutes} мин</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {dispatchData.data.conflicts && dispatchData.data.conflicts.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="text-md font-medium text-yellow-800 mb-2">Конфликты в расписании</h3>
                <ul className="space-y-1">
                  {dispatchData.data.conflicts.map((conflict, idx) => (
                    <li key={idx} className="text-sm text-yellow-700">
                      Задача {conflict.task_id} конфликтует с {conflict.conflict_with} на рабочем центре {conflict.work_center_id}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};
