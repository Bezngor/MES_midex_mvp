/**
 * Компонент фильтров по приоритетам для вкладки "Стратегия".
 * Позволяет выбрать один или несколько приоритетов для фильтрации списков заказов.
 */

import React from 'react';

export type Priority = 'URGENT' | 'HIGH' | 'NORMAL' | 'LOW';

interface PriorityFiltersProps {
  selectedPriorities: Priority[];
  onChange: (priorities: Priority[]) => void;
}

export const priorityLabels: Record<Priority, string> = {
  URGENT: 'Срочно',
  HIGH: 'Высокий',
  NORMAL: 'Обычный',
  LOW: 'Низкий',
};

/** Цвета кнопок как во вкладке MRP: выбран — цветной фон, не выбран — серый. */
const priorityButtonClasses: Record<Priority, string> = {
  URGENT: 'bg-red-600 text-white',
  HIGH: 'bg-orange-500 text-white',
  NORMAL: 'bg-blue-600 text-white',
  LOW: 'bg-gray-600 text-white',
};

export const PriorityFilters: React.FC<PriorityFiltersProps> = ({
  selectedPriorities,
  onChange,
}) => {
  const togglePriority = (priority: Priority) => {
    if (selectedPriorities.includes(priority)) {
      onChange(selectedPriorities.filter((p) => p !== priority));
    } else {
      onChange([...selectedPriorities, priority]);
    }
  };

  return (
    <div className="flex flex-wrap gap-2 items-center">
      {(Object.keys(priorityLabels) as Priority[]).map((priority) => {
        const isSelected = selectedPriorities.includes(priority);
        return (
          <button
            key={priority}
            type="button"
            onClick={() => togglePriority(priority)}
            className={`px-3 py-1.5 rounded text-sm font-medium ${
              isSelected ? priorityButtonClasses[priority] : 'bg-gray-200 text-gray-500'
            }`}
            title={`${isSelected ? 'Снять' : 'Выбрать'} фильтр по приоритету "${priorityLabels[priority]}"`}
          >
            {priorityLabels[priority]}
            {isSelected ? ' ✓' : ''}
          </button>
        );
      })}
    </div>
  );
};
