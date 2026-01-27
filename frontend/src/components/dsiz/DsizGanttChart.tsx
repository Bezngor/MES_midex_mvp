/**
 * Компонент Gantt-диаграммы для DSIZ планирования реакторов
 * Показывает 12 реакторов с операциями и временем переналадки
 */

import React from 'react';
import type { PlanningOperation } from '../../types/api';

interface DsizGanttChartProps {
  operations: PlanningOperation[];
  startDate: string;
  endDate: string;
  reactorCount?: number;
}

export const DsizGanttChart: React.FC<DsizGanttChartProps> = ({
  operations,
  startDate,
  endDate,
  reactorCount = 12,
}) => {
  // Генерируем даты для оси X
  const dates: Date[] = [];
  const start = new Date(startDate);
  const end = new Date(endDate);
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    dates.push(new Date(d));
  }

  // Группируем операции по реакторам и слотам
  const reactorSlots: Record<number, Record<number, PlanningOperation[]>> = {};
  for (let reactor = 1; reactor <= reactorCount; reactor++) {
    reactorSlots[reactor] = { 1: [], 2: [] };
  }

  operations.forEach((op) => {
    // Определяем номер реактора из shift_num и reactor_slot
    // Для упрощения: используем shift_num как номер реактора (1-2), а reactor_slot как слот (1-2)
    // В реальности нужно маппинг из конфигурации
    const reactorNum = op.shift_num; // Упрощение: используем shift_num
    if (reactorNum >= 1 && reactorNum <= reactorCount) {
      const slot = op.reactor_slot;
      if (slot === 1 || slot === 2) {
        if (!reactorSlots[reactorNum][slot]) {
          reactorSlots[reactorNum][slot] = [];
        }
        reactorSlots[reactorNum][slot].push(op);
      }
    }
  });

  const getTaskPosition = (shiftDate: string) => {
    const taskDate = new Date(shiftDate);
    const totalDays = (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24);
    const left = ((taskDate.getTime() - start.getTime()) / (1000 * 60 * 60 * 24) / totalDays) * 100;
    return { left: `${Math.max(0, left)}%`, width: '8%' }; // Фиксированная ширина для операций
  };

  const getModeColor = (mode: string) => {
    if (mode.includes('CREAM')) return 'bg-blue-500';
    if (mode.includes('PASTE')) return 'bg-purple-500';
    return 'bg-gray-500';
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <div className="overflow-x-auto">
        <div className="min-w-full">
          {/* Заголовок с датами */}
          <div className="flex border-b mb-2 sticky top-0 bg-gray-50 z-10">
            <div className="w-48 flex-shrink-0 p-2 font-semibold text-sm text-gray-800">Реактор / Слот</div>
            <div className="flex-1 grid gap-1" style={{ gridTemplateColumns: `repeat(${dates.length}, minmax(100px, 1fr))` }}>
              {dates.map((date, idx) => (
                <div key={idx} className="text-xs text-center p-1 border-r">
                  <div className="font-medium text-gray-800">
                    {date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })}
                  </div>
                  <div className="text-gray-600 text-xs">
                    {date.toLocaleDateString('ru-RU', { weekday: 'short' })}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Реакторы и операции */}
          {Array.from({ length: reactorCount }, (_, i) => i + 1).map((reactorNum) => (
            <div key={reactorNum} className="mb-2 border-b pb-2">
              <div className="font-semibold text-sm mb-1 text-gray-800">Реактор {reactorNum}</div>
              {/* Слот 1 */}
              <div className="relative h-12 bg-gray-50 rounded mb-1">
                <div className="absolute left-0 top-0 bottom-0 w-24 bg-gray-100 flex items-center px-2 text-xs text-gray-800 font-medium">
                  Слот 1
                </div>
                <div className="ml-24 relative h-full">
                  {reactorSlots[reactorNum]?.[1]?.map((op, idx) => {
                    const position = getTaskPosition(op.shift_date);
                    return (
                      <div
                        key={idx}
                        className={`absolute ${getModeColor(op.mode)} text-white text-xs p-1 rounded cursor-pointer hover:opacity-80`}
                        style={{
                          left: position.left,
                          width: position.width,
                          top: '2px',
                          height: 'calc(100% - 4px)',
                        }}
                        title={`${op.bulk_product_sku} - ${op.quantity_kg}кг - ${op.mode} - Смена ${op.shift_num}`}
                      >
                        <div className="truncate font-medium">{op.bulk_product_sku}</div>
                        <div className="truncate text-xs opacity-90">{op.quantity_kg}кг</div>
                      </div>
                    );
                  })}
                </div>
              </div>
              {/* Слот 2 */}
              <div className="relative h-12 bg-gray-50 rounded">
                <div className="absolute left-0 top-0 bottom-0 w-24 bg-gray-100 flex items-center px-2 text-xs text-gray-800 font-medium">
                  Слот 2
                </div>
                <div className="ml-24 relative h-full">
                  {reactorSlots[reactorNum]?.[2]?.map((op, idx) => {
                    const position = getTaskPosition(op.shift_date);
                    return (
                      <div
                        key={idx}
                        className={`absolute ${getModeColor(op.mode)} text-white text-xs p-1 rounded cursor-pointer hover:opacity-80`}
                        style={{
                          left: position.left,
                          width: position.width,
                          top: '2px',
                          height: 'calc(100% - 4px)',
                        }}
                        title={`${op.bulk_product_sku} - ${op.quantity_kg}кг - ${op.mode} - Смена ${op.shift_num}`}
                      >
                        <div className="truncate font-medium">{op.bulk_product_sku}</div>
                        <div className="truncate text-xs opacity-90">{op.quantity_kg}кг</div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Легенда */}
      <div className="mt-4 flex gap-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-500 rounded"></div>
          <span>CREAM_MODE</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-purple-500 rounded"></div>
          <span>PASTE_MODE</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-gray-500 rounded"></div>
          <span>Другое</span>
        </div>
      </div>
    </div>
  );
};
