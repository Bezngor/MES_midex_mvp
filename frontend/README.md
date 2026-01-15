# MES Frontend - React Dashboard

React приложение для управления производством (MES Platform).

## Технологии

- **React 18+** с TypeScript
- **Zustand** для управления состоянием
- **React Router v6** для роутинга
- **Axios** для HTTP запросов
- **Tailwind CSS** для стилизации
- **Vite** как сборщик

## Установка

### Предварительные требования

**Node.js должен быть установлен!** Если вы видите ошибку `npm: The term 'npm' is not recognized`, установите Node.js:

1. Скачайте с https://nodejs.org/ (LTS версия)
2. Запустите установщик
3. Перезапустите терминал

Подробная инструкция: см. [INSTALLATION.md](./INSTALLATION.md)

### Быстрая проверка

Запустите скрипт проверки (PowerShell):
```powershell
.\check-node.ps1
```

### Установка зависимостей

```bash
cd frontend
npm install
```

## Настройка

Создайте файл `.env` в корне папки `frontend`:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Запуск

```bash
npm run dev
```

Приложение будет доступно по адресу: http://localhost:5173

## Сборка для production

```bash
npm run build
```

## Структура проекта

```
frontend/
├── src/
│   ├── components/          # React компоненты
│   │   ├── common/          # Общие компоненты (Button, Modal, Loading, Error)
│   │   ├── products/        # Компоненты для продуктов
│   │   ├── bom/             # Компоненты для спецификаций
│   │   ├── batches/         # Компоненты для партий
│   │   ├── inventory/       # Компоненты для остатков
│   │   ├── scheduling/      # Компоненты для расписания
│   │   └── mrp/             # Компоненты для MRP
│   ├── pages/               # Страницы приложения
│   │   ├── Dashboard.tsx    # Главная страница
│   │   ├── ProductsPage.tsx
│   │   ├── BOMPage.tsx
│   │   ├── BatchesPage.tsx
│   │   ├── InventoryPage.tsx
│   │   ├── SchedulePage.tsx
│   │   └── MRPPage.tsx
│   ├── services/            # API клиент и типы
│   │   ├── api.ts           # Axios instance и endpoints
│   │   └── types.ts         # TypeScript интерфейсы
│   ├── store/               # Zustand stores
│   │   ├── useProductStore.ts
│   │   ├── useBatchStore.ts
│   │   ├── useInventoryStore.ts
│   │   ├── useBOMStore.ts
│   │   ├── useScheduleStore.ts
│   │   └── useMRPStore.ts
│   ├── App.tsx              # Главный компонент с роутингом
│   └── main.tsx             # Точка входа
├── package.json
├── tailwind.config.js
└── vite.config.ts
```

## Функциональность

### 1. Управление продуктами (`/products`)
- Просмотр списка продуктов с фильтрацией по типу
- Создание новых продуктов (RAW_MATERIAL, BULK, PACKAGING, FINISHED_GOOD)
- Удаление продуктов

### 2. Управление спецификациями (`/bom`)
- Просмотр дерева спецификации для продукта
- Добавление компонентов в спецификацию
- Удаление строк спецификации

### 3. Управление партиями (`/batches`)
- Просмотр списка производственных партий
- Создание новых партий
- Запуск и завершение партий (PLANNED → IN_PROGRESS → COMPLETED)

### 4. Остатки на складе (`/inventory`)
- Просмотр остатков с фильтрацией по статусу (FINISHED/SEMI_FINISHED)
- Статистика по общему количеству, доступным и зарезервированным остаткам

### 5. Расписание производства (`/schedule`)
- Gantt-диаграмма с визуализацией задач по рабочим центрам
- Настройка горизонта планирования (7/14/30 дней)

### 6. MRP - Планирование потребности (`/mrp`)
- Консолидация заказов по продуктам
- Отображение приоритетов и крайних сроков
- Настройка горизонта планирования

## API Интеграция

Все API вызовы идут через `src/services/api.ts` с использованием Axios.

Формат ответа от backend:
```typescript
{
  success: boolean;
  data: T;
  error?: string;
}
```

## Состояние приложения

Управление состоянием осуществляется через Zustand stores в папке `src/store/`.

Каждый store предоставляет:
- Данные (массивы/объекты)
- Флаги загрузки (`loading`)
- Ошибки (`error`)
- Методы для работы с данными (fetch, create, update, delete)

## Стилизация

Используется Tailwind CSS с кастомными классами. Все компоненты используют utility-first подход.

## Разработка

Для разработки рекомендуется:
1. Убедиться, что backend запущен на `http://localhost:8000`
2. Запустить frontend: `npm run dev`
3. Открыть браузер: http://localhost:5173

## Тестирование

```bash
npm run lint
```

## Известные ограничения

- Gantt-диаграмма использует упрощённую визуализацию (для production рекомендуется использовать библиотеку типа `react-gantt-timeline` или `dhtmlx-gantt`)
- Нет поддержки drag-and-drop для BOM (можно добавить с помощью `react-beautiful-dnd`)
- Нет real-time обновлений (можно добавить через WebSocket)
