/**
 * Страница справочников DSIZ (Master Data)
 */

import React, { useState } from 'react';

export const DsizMasterDataPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'modes' | 'matrix' | 'rates' | 'workforce' | 'labeling'>('modes');

  const tabs = [
    { id: 'modes' as const, label: 'Режимы реактора' },
    { id: 'matrix' as const, label: 'Матрица совместимости' },
    { id: 'rates' as const, label: 'Базовые скорости' },
    { id: 'workforce' as const, label: 'Workforce правила' },
    { id: 'labeling' as const, label: 'Правила маркировки' },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-800">Справочники DSIZ</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="bg-white rounded-lg shadow">
          {/* Вкладки */}
          <div className="border-b">
            <nav className="flex space-x-1 px-4">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    px-4 py-3 text-sm font-medium transition-colors border-b-2
                    ${activeTab === tab.id
                      ? 'text-blue-600 border-blue-600'
                      : 'text-gray-600 border-transparent hover:text-gray-900 hover:border-gray-300'
                    }
                  `}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Содержимое вкладок */}
          <div className="p-6">
            {activeTab === 'modes' && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-800">Режимы реактора</h2>
                <p className="text-sm text-gray-600">
                  Управление режимами работы реакторов (CREAM_MODE, PASTE_MODE и т.д.)
                </p>
                <div className="bg-gray-50 border rounded-lg p-4">
                  <p className="text-sm text-gray-500">Функционал будет реализован в следующей версии</p>
                </div>
              </div>
            )}

            {activeTab === 'matrix' && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-800">Матрица совместимости</h2>
                <p className="text-sm text-gray-600">
                  Настройка времени переналадки между продуктами
                </p>
                <div className="bg-gray-50 border rounded-lg p-4">
                  <p className="text-sm text-gray-500">Функционал будет реализован в следующей версии</p>
                </div>
              </div>
            )}

            {activeTab === 'rates' && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-800">Базовые скорости</h2>
                <p className="text-sm text-gray-600">
                  Настройка базовых производственных скоростей по операциям
                </p>
                <div className="bg-gray-50 border rounded-lg p-4">
                  <p className="text-sm text-gray-500">Функционал будет реализован в следующей версии</p>
                </div>
              </div>
            )}

            {activeTab === 'workforce' && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-800">Workforce правила</h2>
                <p className="text-sm text-gray-600">
                  Настройка норм по персоналу и коэффициентов
                </p>
                <div className="bg-gray-50 border rounded-lg p-4">
                  <p className="text-sm text-gray-500">Функционал будет реализован в следующей версии</p>
                </div>
              </div>
            )}

            {activeTab === 'labeling' && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-800">Правила маркировки</h2>
                <p className="text-sm text-gray-600">
                  Настройка дефолтного режима ЧЗ и политики при отсутствии QR
                </p>
                <div className="bg-gray-50 border rounded-lg p-4">
                  <p className="text-sm text-gray-500">Функционал будет реализован в следующей версии</p>
                </div>
              </div>
            )}

            {/* Кнопки действий */}
            <div className="mt-6 flex gap-4">
              <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium">
                Сохранить
              </button>
              <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 font-medium">
                Экспорт CSV
              </button>
              <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 font-medium">
                Импорт CSV
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
