/**
 * Dashboard page - главная страница MES платформы с навигацией
 */

import React from "react";
import { Link } from "react-router-dom";

export const Dashboard: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-gray-800">MES Platform Dashboard</h1>
          <p className="text-sm text-gray-600 mt-1">
            Система управления производством - Manufacturing Execution System
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link
            to="/products"
            className="bg-blue-500 text-white p-6 rounded-lg shadow-md hover:bg-blue-600 transition-colors"
          >
            <h2 className="text-xl font-semibold mb-2">Продукты</h2>
            <p className="text-blue-100">Управление каталогом продуктов (сырьё, масса, тара, ГП)</p>
          </Link>

          <Link
            to="/bom"
            className="bg-green-500 text-white p-6 rounded-lg shadow-md hover:bg-green-600 transition-colors"
          >
            <h2 className="text-xl font-semibold mb-2">BOM</h2>
            <p className="text-green-100">Редактирование спецификаций состава (Bill of Materials)</p>
          </Link>

          <Link
            to="/batches"
            className="bg-purple-500 text-white p-6 rounded-lg shadow-md hover:bg-purple-600 transition-colors"
          >
            <h2 className="text-xl font-semibold mb-2">Партии</h2>
            <p className="text-purple-100">Отслеживание производственных партий (PLANNED → IN_PROGRESS → COMPLETED)</p>
          </Link>

          <Link
            to="/inventory"
            className="bg-yellow-500 text-white p-6 rounded-lg shadow-md hover:bg-yellow-600 transition-colors"
          >
            <h2 className="text-xl font-semibold mb-2">Остатки</h2>
            <p className="text-yellow-100">Мониторинг остатков на складе (FINISHED/SEMI_FINISHED)</p>
          </Link>

          <Link
            to="/schedule"
            className="bg-red-500 text-white p-6 rounded-lg shadow-md hover:bg-red-600 transition-colors"
          >
            <h2 className="text-xl font-semibold mb-2">Расписание</h2>
            <p className="text-red-100">Просмотр расписания производства (Gantt-диаграмма)</p>
          </Link>

          <Link
            to="/mrp"
            className="bg-indigo-500 text-white p-6 rounded-lg shadow-md hover:bg-indigo-600 transition-colors"
          >
            <h2 className="text-xl font-semibold mb-2">MRP</h2>
            <p className="text-indigo-100">Планирование потребности в материалах</p>
          </Link>
        </div>

        <div className="mt-8 p-6 bg-white rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">Статистика системы</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">29</p>
              <p className="text-sm text-gray-600">API endpoints</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">141</p>
              <p className="text-sm text-gray-600">Тестов</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">93%</p>
              <p className="text-sm text-gray-600">Покрытие тестами</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
