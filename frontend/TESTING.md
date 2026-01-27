# Тестирование Frontend

## Установка зависимостей

```bash
cd frontend
npm install
```

## ESLint

Конфигурация ESLint находится в `.eslintrc.cjs`.

### Запуск линтера:

```bash
npm run lint
```

### Автоисправление:

```bash
npm run lint -- --fix
```

## Тестирование (Vitest)

### Установка зависимостей для тестирования:

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom @vitest/ui
```

### Запуск тестов:

```bash
# Интерактивный режим (watch mode)
npm test

# UI режим
npm run test:ui

# Одноразовый запуск с покрытием
npm run test:run
```

### Структура тестов:

- `src/test/setup.ts` - настройка тестового окружения
- `src/test/DsizPlanning.test.tsx` - тесты для DsizPlanningPage

### Покрытие кода:

Покрытие генерируется автоматически при запуске `npm run test:run`. Результаты доступны в:
- Консоль (текстовый формат)
- `coverage/` директория (HTML отчет)

## Type Checking

```bash
npm run type-check
```

## Команды

- `npm run dev` - запуск dev сервера
- `npm run build` - сборка production
- `npm run lint` - проверка кода ESLint
- `npm run type-check` - проверка типов TypeScript
- `npm test` - запуск тестов (watch mode)
- `npm run test:ui` - запуск тестов с UI
- `npm run test:run` - одноразовый запуск с покрытием
