/**
 * Компонент индикатора загрузки
 */

import React from 'react';

export const Loading: React.FC<{ message?: string }> = ({ message = 'Загрузка...' }) => {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="mt-2 text-gray-600">{message}</p>
      </div>
    </div>
  );
};
