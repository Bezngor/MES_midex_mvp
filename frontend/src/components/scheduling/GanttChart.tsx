/**
 * Компонент Gantt-диаграммы для визуализации расписания производства
 */

import React, { useEffect, useState } from 'react';
import { useScheduleStore } from '../../store/useScheduleStore';
import { Loading } from '../common/Loading';
import { Error } from '../common/Error';

export const GanttChart: React.FC = () => {
  const { ganttData, loading, error, fetchGanttData } = useScheduleStore();
  const [days, setDays] = useState(7);

  useEffect(() => {
    const startDate = new Date().toISOString();
    const endDate = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toISOString();
    fetchGanttData(startDate, endDate);
  }, [days, fetchGanttData]);

  if (loading) return <Loading message="Загрузка расписания..." />;
  if (error) return <Error message={error} onRetry={() => {
    const startDate = new Date().toISOString();
    const endDate = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toISOString();
    fetchGanttData(startDate, endDate);
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

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-gray-800">Расписание производства (Gantt)</h3>
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
            <div className="flex-1 grid grid-cols-7 gap-1">
              {dates.map((date, idx) => (
                <div key={idx} className="text-xs text-center p-1 border-r text-gray-800 font-medium">
                  {date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })}
                </div>
              ))}
            </div>
          </div>

          {/* Рабочие центры и задачи */}
          {ganttData.work_centers.map((wc) => (
            <div key={wc.id} className="mb-4 border-b pb-4">
              <div className="font-semibold mb-2 text-gray-800">{wc.name}</div>
              <div className="relative h-20 bg-gray-50 rounded">
                {wc.tasks.map((task) => {
                  const position = getTaskPosition(task.start, task.end);
                  return (
                    <div
                      key={task.id}
                      className={`absolute ${getPriorityColor(task.priority)} text-white text-xs p-1 rounded cursor-pointer hover:opacity-80`}
                      style={{ left: position.left, width: position.width, top: '10px', height: '30px' }}
                      title={`${task.name} (${task.start} - ${task.end})`}
                    >
                      <div className="truncate">{task.name}</div>
                    </div>
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
