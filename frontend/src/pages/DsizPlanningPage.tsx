/**
 * Страница планирования реакторов DSIZ
 */

import React, { useState } from 'react';
import { useDsizPlanning } from '../hooks/useDsizPlanning';
import { DsizGanttChart } from '../components/dsiz/DsizGanttChart';
import { ReactorSlotSelector } from '../components/dsiz/ReactorSlotSelector';
import { WorkforceInput } from '../components/dsiz/WorkforceInput';
import { LabelingModeSelector, LabelingMode } from '../components/dsiz/LabelingModeSelector';
import { Loading } from '../components/common/Loading';
import { Error } from '../components/common/Error';

export const DsizPlanningPage: React.FC = () => {
  const { planningData, loading, error, runPlanning, clearError } = useDsizPlanning();
  
  const [planningDate, setPlanningDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [horizonDays, setHorizonDays] = useState(7);
  const [selectedSlots, setSelectedSlots] = useState<number[]>([]);
  const [workforce, setWorkforce] = useState<Record<string, Record<string, number>>>({
    shift_1: { OPERATOR: 1, PACKER: 2, AUTO: 4 },
    shift_2: { OPERATOR: 1, PACKER: 1, AUTO: 3 },
  });
  const [labelingMode, setLabelingMode] = useState<LabelingMode>('AUTO');

  const handleRunPlanning = async () => {
    clearError();
    const result = await runPlanning({
      planning_date: planningDate,
      horizon_days: horizonDays,
      workforce_state: workforce,
    });
    
    if (result) {
      // Планирование успешно выполнено
      console.log('Планирование выполнено:', result);
    }
  };

  const handleExportPDF = () => {
    // TODO: Реализовать экспорт в PDF
    alert('Экспорт в PDF будет реализован в следующей версии');
  };

  const endDate = planningData
    ? new Date(
        new Date(planningData.planning_date).getTime() +
          planningData.horizon_days * 24 * 60 * 60 * 1000
      ).toISOString().split('T')[0]
    : new Date(
        new Date(planningDate).getTime() + horizonDays * 24 * 60 * 60 * 1000
      ).toISOString().split('T')[0];

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-800">Планирование реакторов</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Панель параметров планирования */}
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">Параметры планирования</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="planning-date" className="block text-sm font-medium text-gray-700 mb-1">
                Дата начала планирования
              </label>
              <input
                id="planning-date"
                type="date"
                value={planningDate}
                onChange={(e) => setPlanningDate(e.target.value)}
                className="w-full border rounded px-3 py-2"
              />
            </div>
            
            <div>
              <label htmlFor="horizon-days" className="block text-sm font-medium text-gray-700 mb-1">
                Горизонт планирования (дней)
              </label>
              <input
                id="horizon-days"
                type="number"
                min="1"
                max="30"
                value={horizonDays}
                onChange={(e) => setHorizonDays(parseInt(e.target.value) || 7)}
                className="w-full border rounded px-3 py-2"
              />
            </div>
          </div>

          <ReactorSlotSelector
            selectedSlots={selectedSlots}
            onSlotsChange={setSelectedSlots}
            maxSlots={12}
          />

          <WorkforceInput
            workforce={workforce}
            onWorkforceChange={setWorkforce}
            roles={['OPERATOR', 'PACKER', 'AUTO']}
          />

          <LabelingModeSelector
            mode={labelingMode}
            onModeChange={setLabelingMode}
            printerStatus="READY"
          />

          <div className="flex gap-4 pt-4">
            <button
              onClick={handleRunPlanning}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              {loading ? 'Запуск планирования...' : 'Запустить планирование'}
            </button>
            
            <button
              onClick={handleExportPDF}
              disabled={!planningData || loading}
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              PDF Export
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
        {loading && <Loading message="Выполнение планирования..." />}

        {/* Gantt Chart */}
        {planningData && planningData.operations.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              План производства
            </h2>
            <DsizGanttChart
              operations={planningData.operations}
              startDate={planningData.planning_date}
              endDate={endDate}
              reactorCount={12}
            />
          </div>
        )}

        {/* Предупреждения */}
        {planningData && planningData.warnings.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-yellow-800 mb-2">Предупреждения</h3>
            <ul className="space-y-1">
              {planningData.warnings.map((warning, idx) => (
                <li key={idx} className="text-sm text-yellow-700">
                  <span className="font-medium">{warning.level}:</span> {warning.message}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Сводка */}
        {planningData && planningData.summary && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-blue-800 mb-2">Сводка планирования</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Всего операций:</span>
                <span className="ml-2 font-medium">{planningData.summary.total_operations || 0}</span>
              </div>
              <div>
                <span className="text-gray-600">ГП продуктов:</span>
                <span className="ml-2 font-medium">{planningData.summary.total_fg_products || 0}</span>
              </div>
              <div>
                <span className="text-gray-600">Предупреждений:</span>
                <span className="ml-2 font-medium">{planningData.warnings.length}</span>
              </div>
              <div>
                <span className="text-gray-600">ID плана:</span>
                <span className="ml-2 font-medium text-xs">{planningData.plan_id}</span>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
