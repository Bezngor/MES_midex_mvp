/**
 * Компонент выбора режима маркировки (AUTO/MANUAL) и статуса принтера
 */

import React from 'react';

export type LabelingMode = 'AUTO' | 'MANUAL';

interface LabelingModeSelectorProps {
  mode: LabelingMode;
  onModeChange: (mode: LabelingMode) => void;
  printerStatus?: 'READY' | 'BUSY' | 'ERROR' | 'OFFLINE';
  disabled?: boolean;
}

export const LabelingModeSelector: React.FC<LabelingModeSelectorProps> = ({
  mode,
  onModeChange,
  printerStatus = 'READY',
  disabled = false,
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'READY':
        return 'bg-green-100 text-green-800';
      case 'BUSY':
        return 'bg-yellow-100 text-yellow-800';
      case 'ERROR':
        return 'bg-red-100 text-red-800';
      case 'OFFLINE':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'READY':
        return 'Готов';
      case 'BUSY':
        return 'Занят';
      case 'ERROR':
        return 'Ошибка';
      case 'OFFLINE':
        return 'Офлайн';
      default:
        return 'Неизвестно';
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Режим маркировки
      </label>
      <div className="flex gap-4">
        <div className="flex-1">
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => onModeChange('AUTO')}
              disabled={disabled}
              className={`
                flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors
                ${mode === 'AUTO'
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              AUTO
            </button>
            <button
              type="button"
              onClick={() => onModeChange('MANUAL')}
              disabled={disabled}
              className={`
                flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors
                ${mode === 'MANUAL'
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              MANUAL
            </button>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-600">Принтер:</span>
          <span
            className={`
              px-3 py-1 rounded-full text-xs font-medium
              ${getStatusColor(printerStatus)}
            `}
          >
            {getStatusText(printerStatus)}
          </span>
        </div>
      </div>
      <p className="text-xs text-gray-500">
        {mode === 'AUTO'
          ? 'Автоматическая маркировка через принтер'
          : 'Ручная маркировка оператором'}
      </p>
    </div>
  );
};
