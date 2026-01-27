/**
 * Компонент выбора слота реактора (1-12)
 */

import React from 'react';

interface ReactorSlotSelectorProps {
  selectedSlots: number[];
  onSlotsChange: (slots: number[]) => void;
  maxSlots?: number;
  disabled?: boolean;
}

export const ReactorSlotSelector: React.FC<ReactorSlotSelectorProps> = ({
  selectedSlots,
  onSlotsChange,
  maxSlots = 12,
  disabled = false,
}) => {
  const handleSlotToggle = (slot: number) => {
    if (disabled) return;
    
    if (selectedSlots.includes(slot)) {
      onSlotsChange(selectedSlots.filter((s) => s !== slot));
    } else {
      if (selectedSlots.length < maxSlots) {
        onSlotsChange([...selectedSlots, slot]);
      }
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Слоты реакторов (выбрано: {selectedSlots.length}/{maxSlots})
      </label>
      <div className="grid grid-cols-6 gap-2">
        {Array.from({ length: maxSlots }, (_, i) => i + 1).map((slot) => {
          const isSelected = selectedSlots.includes(slot);
          return (
            <button
              key={slot}
              type="button"
              onClick={() => handleSlotToggle(slot)}
              disabled={disabled}
              className={`
                px-3 py-2 rounded-md text-sm font-medium transition-colors
                ${isSelected
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              Реактор {slot}
            </button>
          );
        })}
      </div>
    </div>
  );
};
