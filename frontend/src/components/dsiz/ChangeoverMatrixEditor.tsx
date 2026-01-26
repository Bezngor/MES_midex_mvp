/**
 * Компонент редактора матрицы совместимости (changeover matrix)
 */

import React, { useState } from 'react';

interface ChangeoverMatrixEditorProps {
  matrix: Record<string, Record<string, number>>;
  onMatrixChange: (matrix: Record<string, Record<string, number>>) => void;
  products: string[];
  disabled?: boolean;
}

export const ChangeoverMatrixEditor: React.FC<ChangeoverMatrixEditorProps> = ({
  matrix,
  onMatrixChange,
  products,
  disabled = false,
}) => {
  const [localMatrix, setLocalMatrix] = useState(matrix);

  const handleChange = (fromProduct: string, toProduct: string, value: number) => {
    if (disabled) return;
    
    const newMatrix = {
      ...localMatrix,
      [fromProduct]: {
        ...localMatrix[fromProduct],
        [toProduct]: value,
      },
    };
    setLocalMatrix(newMatrix);
    onMatrixChange(newMatrix);
  };

  const getColor = (minutes: number) => {
    if (minutes === 0) return 'bg-green-100';
    if (minutes < 30) return 'bg-yellow-100';
    if (minutes < 60) return 'bg-orange-100';
    return 'bg-red-100';
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Матрица совместимости (время переналадки в минутах)
      </label>
      <div className="overflow-x-auto">
        <table className="min-w-full border-collapse border border-gray-300">
          <thead>
            <tr>
              <th className="border border-gray-300 p-2 bg-gray-50 text-left text-xs font-medium text-gray-700">
                От \ К
              </th>
              {products.map((product) => (
                <th
                  key={product}
                  className="border border-gray-300 p-2 bg-gray-50 text-xs font-medium text-gray-700"
                >
                  {product}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {products.map((fromProduct) => (
              <tr key={fromProduct}>
                <td className="border border-gray-300 p-2 bg-gray-50 text-xs font-medium text-gray-700">
                  {fromProduct}
                </td>
                {products.map((toProduct) => {
                  const value = localMatrix[fromProduct]?.[toProduct] ?? 0;
                  return (
                    <td key={toProduct} className="border border-gray-300 p-1">
                      <input
                        type="number"
                        min="0"
                        value={value}
                        onChange={(e) =>
                          handleChange(fromProduct, toProduct, parseInt(e.target.value) || 0)
                        }
                        disabled={disabled || fromProduct === toProduct}
                        className={`
                          w-full px-2 py-1 text-xs text-center border rounded
                          ${getColor(value)}
                          ${fromProduct === toProduct ? 'opacity-50 cursor-not-allowed' : ''}
                          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
                        `}
                      />
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex gap-4 text-xs text-gray-600">
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-green-100 border border-gray-300"></div>
          <span>0 мин</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-yellow-100 border border-gray-300"></div>
          <span>&lt; 30 мин</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-orange-100 border border-gray-300"></div>
          <span>30-60 мин</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-red-100 border border-gray-300"></div>
          <span>&gt; 60 мин</span>
        </div>
      </div>
    </div>
  );
};
