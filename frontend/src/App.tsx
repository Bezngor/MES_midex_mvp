/**
 * Главный компонент приложения с роутингом
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { ProductsPage } from './pages/ProductsPage';
import { BOMPage } from './pages/BOMPage';
import { BatchesPage } from './pages/BatchesPage';
import { InventoryPage } from './pages/InventoryPage';
import { SchedulePage } from './pages/SchedulePage';
import { MRPPage } from './pages/MRPPage';

const Navigation: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Главная' },
    { path: '/products', label: 'Продукты' },
    { path: '/bom', label: 'BOM' },
    { path: '/batches', label: 'Партии' },
    { path: '/inventory', label: 'Остатки' },
    { path: '/schedule', label: 'Расписание' },
    { path: '/mrp', label: 'MRP' },
  ];

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex space-x-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`px-4 py-3 text-sm font-medium transition-colors ${
                location.pathname === item.path
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100">
        <Navigation />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/bom" element={<BOMPage />} />
          <Route path="/batches" element={<BatchesPage />} />
          <Route path="/inventory" element={<InventoryPage />} />
          <Route path="/schedule" element={<SchedulePage />} />
          <Route path="/mrp" element={<MRPPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
