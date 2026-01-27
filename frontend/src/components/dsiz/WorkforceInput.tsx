/**
 * Компонент ввода состава смены и резерва персонала
 */

import React, { useState } from 'react';

interface WorkforceInputProps {
  workforce: Record<string, Record<string, number>>;
  onWorkforceChange: (workforce: Record<string, Record<string, number>>) => void;
  roles?: string[];
  disabled?: boolean;
}

export const WorkforceInput: React.FC<WorkforceInputProps> = ({
  workforce,
  onWorkforceChange,
  roles = ['OPERATOR', 'PACKER', 'AUTO'],
  disabled = false,
}) => {
  const [localWorkforce, setLocalWorkforce] = useState<Record<string, Record<string, number>>>(workforce);

  const handleChange = (shiftKey: string, role: string, value: number) => {
    if (disabled) return;
    
    const newWorkforce = {
      ...localWorkforce,
      [shiftKey]: {
        ...localWorkforce[shiftKey],
        [role]: Math.max(0, value),
      },
    };
    setLocalWorkforce(newWorkforce);
    onWorkforceChange(newWorkforce);
  };

  const shifts = Object.keys(localWorkforce).length > 0 
    ? Object.keys(localWorkforce) 
    : ['shift_1', 'shift_2'];

  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium text-gray-700">
        Состав персонала по сменам
      </label>
      <div className="overflow-x-auto">
        <table className="min-w-full border-collapse border border-gray-300">
          <thead>
            <tr>
              <th className="border border-gray-300 p-2 bg-gray-50 text-left text-xs font-medium text-gray-700">
                Смена
              </th>
              {roles.map((role) => (
                <th
                  key={role}
                  className="border border-gray-300 p-2 bg-gray-50 text-xs font-medium text-gray-700"
                >
                  {role}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {shifts.map((shiftKey) => (
              <tr key={shiftKey}>
                <td className="border border-gray-300 p-2 bg-gray-50 text-xs font-medium text-gray-700">
                  {shiftKey === 'shift_1' ? 'Смена 1' : shiftKey === 'shift_2' ? 'Смена 2' : shiftKey}
                </td>
                {roles.map((role) => {
                  const value = localWorkforce[shiftKey]?.[role] ?? 0;
                  return (
                    <td key={role} className="border border-gray-300 p-1">
                      <input
                        type="number"
                        min="0"
                        value={value}
                        onChange={(e) => handleChange(shiftKey, role, parseInt(e.target.value) || 0)}
                        disabled={disabled}
                        className={`
                          w-full px-2 py-1 text-xs text-center border rounded
                          ${disabled ? 'opacity-50 cursor-not-allowed bg-gray-100' : 'bg-white'}
                        `}
                        placeholder="0"
                      />
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
