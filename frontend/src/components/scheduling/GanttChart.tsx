/**
 * Компонент Gantt-диаграммы для визуализации расписания производства
 */

import React, { useEffect, useState } from 'react';
import { useScheduleStore } from '../../store/useScheduleStore';
import { getWorkCenterDisplayName, sortWorkCentersByOrder } from '../../utils/workCenterDisplayNames';
import { Loading } from '../common/Loading';
import { Error } from '../common/Error';

interface GanttChartProps {
  /** При изменении значения данные Гант-диаграммы перезапрашиваются (например, после пересчёта плана). */
  refreshTrigger?: number;
  /** Количество дней по умолчанию (на вкладке «Стратегия» лучше 14+, т.к. план привязан к срокам заказов). */
  defaultDays?: number;
}

export const GanttChart: React.FC<GanttChartProps> = ({ refreshTrigger = 0, defaultDays = 7 }) => {
  const { ganttData, loading, error, fetchGanttData } = useScheduleStore();
  const [days, setDays] = useState(defaultDays);

  useEffect(() => {
    const start = new Date();
    start.setHours(0, 0, 0, 0);
    const end = new Date(start.getTime() + (days - 1) * 24 * 60 * 60 * 1000);
    end.setHours(23, 59, 59, 999);
    fetchGanttData(start.toISOString(), end.toISOString());
  }, [days, fetchGanttData, refreshTrigger]);

  if (loading) return <Loading message="Загрузка расписания..." />;
  if (error) return <Error message={error} onRetry={() => {
    const start = new Date();
    start.setHours(0, 0, 0, 0);
    const end = new Date(start.getTime() + (days - 1) * 24 * 60 * 60 * 1000);
    end.setHours(23, 59, 59, 999);
    fetchGanttData(start.toISOString(), end.toISOString());
  }} />;

  if (!ganttData) return <div className="p-4">Нет данных для отображения</div>;

  // Генерируем даты для оси X
  const dates: Date[] = [];
  const start = new Date(ganttData.start_date);
  const end = new Date(ganttData.end_date);
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    dates.push(new Date(d));
  }

  const getTaskPosition = (taskStart: string, taskEnd: string) => {
    const start = new Date(ganttData.start_date);
    const taskStartDate = new Date(taskStart);
    const taskEndDate = new Date(taskEnd);
    const totalDays = (new Date(ganttData.end_date).getTime() - start.getTime()) / (1000 * 60 * 60 * 24);
    const left = ((taskStartDate.getTime() - start.getTime()) / (1000 * 60 * 60 * 24) / totalDays) * 100;
    const width = ((taskEndDate.getTime() - taskStartDate.getTime()) / (1000 * 60 * 60 * 24) / totalDays) * 100;
    return { left: `${left}%`, width: `${width}%` };
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'URGENT':
        return 'bg-red-500';
      case 'HIGH':
        return 'bg-orange-500';
      case 'NORMAL':
        return 'bg-blue-500';
      case 'LOW':
        return 'bg-gray-500';
      default:
        return 'bg-gray-400';
    }
  };

  /** Границы смен в UTC: Смена1 08:00–20:00, Смена2 20:00–08:00. Дата в подсказке — всегда дата начала смены. */
  const getShiftDisplayDate = (taskStart: Date): Date => {
    const h = taskStart.getUTCHours();
    const m = taskStart.getUTCMinutes();
    const dayStart = new Date(Date.UTC(
      taskStart.getUTCFullYear(),
      taskStart.getUTCMonth(),
      taskStart.getUTCDate(),
    ));
    if (h < 8) {
      dayStart.setUTCDate(dayStart.getUTCDate() - 1);
    }
    return dayStart;
  };

  const pad2 = (n: number) => String(n).padStart(2, '0');

  const formatGanttTooltip = (
    productName: string,
    quantityDisplay: string | null | undefined,
    taskStart: string,
    taskEnd: string,
  ): string => {
    const start = new Date(taskStart);
    const end = new Date(taskEnd);
    const shiftDate = getShiftDisplayDate(start);
    const dateStr = `${pad2(shiftDate.getUTCDate())}-${pad2(shiftDate.getUTCMonth() + 1)}-${shiftDate.getUTCFullYear()}`;
    const timeStart = `${pad2(start.getUTCHours())}:${pad2(start.getUTCMinutes())}`;
    const timeEnd = `${pad2(end.getUTCHours())}:${pad2(end.getUTCMinutes())}`;
    const quantityPart = quantityDisplay ? ` - ${quantityDisplay}` : '';
    return `${productName}${quantityPart} (${dateStr} ${timeStart}-${timeEnd})`;
  };

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-800">Расписание производства (Gantt)</h3>
          <p className="text-xs text-gray-500 mt-1">
            Цвета задач: <span className="inline-block w-3 h-3 bg-red-500 rounded mr-1"></span> Срочно —{' '}
            <span className="inline-block w-3 h-3 bg-orange-500 rounded mr-1"></span> Высокий —{' '}
            <span className="inline-block w-3 h-3 bg-blue-500 rounded mr-1"></span> Обычный —{' '}
            <span className="inline-block w-3 h-3 bg-gray-500 rounded mr-1"></span> Низкий
          </p>
        </div>
        <select
          className="border rounded px-3 py-2"
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
        >
          <option value={7}>7 дней</option>
          <option value={14}>14 дней</option>
          <option value={30}>30 дней</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <div className="min-w-full">
          {/* Заголовок с датами */}
          <div className="flex border-b mb-2 bg-gray-50">
            <div className="w-48 flex-shrink-0 p-2 font-semibold text-gray-800">Рабочий центр</div>
            <div
              className="flex-1 grid gap-1"
              style={{ gridTemplateColumns: `repeat(${dates.length}, minmax(0, 1fr))` }}
            >
              {dates.map((date, idx) => (
                <div key={idx} className="text-xs text-center p-1 border-r text-gray-800 font-medium">
                  {date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })}
                </div>
              ))}
            </div>
          </div>

          {/* Рабочие центры и задачи (порядок фиксирован: Реактор → Миксер → Тубировка 1/2 → полуавтоматы → розлив → ЧЗ → Линия тубы) */}
          {sortWorkCentersByOrder(ganttData.work_centers).map((wc) => (
            <div key={wc.id} className="mb-4 border-b pb-4">
              <div className="font-semibold mb-2 text-gray-800">{getWorkCenterDisplayName(wc.name, wc.id)}</div>
              <div className="relative h-20 bg-gray-50 rounded">
                {wc.tasks.map((task) => {
                  const position = getTaskPosition(task.start, task.end);
                  const tooltipProductName = task.product_name || task.name;
                  const tooltip = formatGanttTooltip(
                    tooltipProductName,
                    task.quantity_display ?? null,
                    task.start,
                    task.end,
                  );
                  return (
                    <div
                      key={task.id}
                      className={`absolute ${getPriorityColor(task.priority)} text-white text-xs p-1 rounded cursor-pointer hover:opacity-80`}
                      style={{ left: position.left, width: position.width, top: '10px', height: '30px' }}
                      title={tooltip}
                    />
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
