/**
 * Страница выявления новых и изменённых заказов.
 * Реализует шаг бизнес-процесса "Блок обновления данных" → "Выявить новые и/или измененные ЗП".
 */

import React from 'react';
import { OrderChangesList } from '../components/orders/OrderChangesList';

export const OrderChangesPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-800">Выявление изменений заказов</h1>
          <p className="text-sm text-gray-600 mt-1">
            Блок обновления данных — выявить новые и/или измененные ЗП
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        <OrderChangesList />
      </main>
    </div>
  );
};
