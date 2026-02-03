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

const priorityLabels: Record<Priority, string> = {
  URGENT: 'Срочно',
  HIGH: 'Высокий',
  NORMAL: 'Обычный',
  LOW: 'Низкий',
};

const priorityColors: Record<Priority, string> = {
  URGENT: 'bg-red-500 hover:bg-red-600',
  HIGH: 'bg-orange-500 hover:bg-orange-600',
  NORMAL: 'bg-blue-500 hover:bg-blue-600',
  LOW: 'bg-gray-500 hover:bg-gray-600',
};

const priorityColorsActive: Record<Priority, string> = {
  URGENT: 'bg-red-700 ring-2 ring-red-300',
  HIGH: 'bg-orange-700 ring-2 ring-orange-300',
  NORMAL: 'bg-blue-700 ring-2 ring-blue-300',
  LOW: 'bg-gray-700 ring-2 ring-gray-300',
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
    <div className="flex flex-wrap gap-2">
      {(Object.keys(priorityLabels) as Priority[]).map((priority) => {
        const isSelected = selectedPriorities.includes(priority);
        return (
          <button
            key={priority}
            onClick={() => togglePriority(priority)}
            className={`px-4 py-2 rounded-md text-white font-medium transition-all ${
              isSelected
                ? priorityColorsActive[priority]
                : priorityColors[priority]
            }`}
            title={`${isSelected ? 'Снять' : 'Выбрать'} фильтр по приоритету "${priorityLabels[priority]}"`}
          >
            {priorityLabels[priority]}
          </button>
        );
      })}
    </div>
  );
};
