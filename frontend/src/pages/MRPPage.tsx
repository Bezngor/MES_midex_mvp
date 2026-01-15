/**
 * Страница MRP (Material Requirements Planning)
 */

import React from 'react';
import { MRPDashboard } from '../components/mrp/MRPDashboard';

export const MRPPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-800">MRP - Планирование потребности в материалах</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        <MRPDashboard />
      </main>
    </div>
  );
};
