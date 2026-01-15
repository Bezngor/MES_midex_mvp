/**
 * Страница управления остатками на складе
 */

import React from 'react';
import { InventoryDashboard } from '../components/inventory/InventoryDashboard';

export const InventoryPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-800">Остатки на складе</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        <InventoryDashboard />
      </main>
    </div>
  );
};
