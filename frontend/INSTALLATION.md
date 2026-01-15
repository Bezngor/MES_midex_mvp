# Инструкция по установке и запуску Frontend

## Требования

Для работы frontend приложения необходимо установить:

1. **Node.js** (версия 18 или выше)
2. **npm** (обычно устанавливается вместе с Node.js)

## Установка Node.js

### Вариант 1: Официальный установщик (рекомендуется, НЕ требует прав администратора)

1. Перейдите на сайт: https://nodejs.org/
2. Скачайте **LTS версию** (Long Term Support) - это стабильная версия
3. Запустите скачанный `.msi` файл
4. Следуйте инструкциям установщика
5. Убедитесь, что опция **"Add to PATH"** отмечена (обычно включена по умолчанию)
6. После установки **перезапустите терминал/PowerShell**

**Прямые ссылки для скачивания:**
- 64-bit Windows: https://nodejs.org/dist/v24.12.0/node-v24.12.0-x64.msi
- ARM64 Windows: https://nodejs.org/dist/v24.12.0/node-v24.12.0-arm64.msi

### Вариант 2: Через winget (Windows Package Manager, если установлен)

```powershell
winget install OpenJS.NodeJS.LTS
```

### Вариант 3: Через Chocolatey (требует прав администратора)

⚠️ **Внимание:** Chocolatey требует запуска PowerShell от имени администратора!

1. Запустите PowerShell от имени администратора (правой кнопкой → "Запуск от имени администратора")
2. Выполните:
   ```powershell
   choco install nodejs
   ```

**Если возникла ошибка с lock файлом:**
```powershell
# Удалите lock файл (требует прав администратора)
Remove-Item "C:\ProgramData\chocolatey\lib\80b5db4ae59a27a4e5a98bc869b3316f892f2838" -Force
# Затем повторите установку
choco install nodejs
```

## Проверка установки

После установки **обязательно перезапустите терминал/PowerShell**, затем проверьте:

```powershell
node --version
npm --version
```

Ожидаемый вывод:
```
v18.x.x или выше
9.x.x или выше
```

Если команды не распознаются после перезапуска терминала, см. раздел "Решение проблем" ниже.

## Установка зависимостей проекта

После успешной установки Node.js:

```powershell
cd frontend
npm install
```

Это может занять несколько минут при первом запуске.

## Запуск приложения

```powershell
npm run dev
```

Приложение будет доступно по адресу: http://localhost:5173

## Альтернативные менеджеры пакетов

Если у вас установлен **yarn** или **pnpm**, вы можете использовать их вместо npm:

```powershell
# С yarn
yarn install
yarn dev

# С pnpm
pnpm install
pnpm dev
```

## Решение проблем

### npm не распознаётся после установки Node.js

1. **Перезапустите терминал/PowerShell** (это важно!)
2. Проверьте переменные окружения PATH:
   ```powershell
   $env:PATH -split ';' | Select-String node
   ```
3. Если Node.js не найден в PATH:
   - Обычно Node.js устанавливается в: `C:\Program Files\nodejs\` или `C:\Users\ВашеИмя\AppData\Local\Programs\nodejs\`
   - Добавьте этот путь в системные переменные окружения PATH:
     - Откройте "Переменные среды" (через поиск Windows)
     - Найдите переменную `Path` в разделе "Системные переменные"
     - Добавьте путь к Node.js (например: `C:\Program Files\nodejs\`)
     - Перезапустите терминал

### Ошибки при установке зависимостей

Если возникают ошибки при `npm install`:

1. Очистите кэш npm:
   ```powershell
   npm cache clean --force
   ```

2. Удалите папку `node_modules` и файл `package-lock.json`:
   ```powershell
   Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
   Remove-Item package-lock.json -ErrorAction SilentlyContinue
   ```

3. Повторите установку:
   ```powershell
   npm install
   ```

### Проблемы с правами доступа

Если возникают ошибки доступа:

1. Запустите PowerShell от имени администратора
2. Или используйте флаг `--unsafe-perm`:
   ```powershell
   npm install --unsafe-perm
   ```

### Chocolatey: ошибка "Unable to obtain lock file access"

Если вы пытаетесь установить через Chocolatey и получаете ошибку с lock файлом:

1. Запустите PowerShell **от имени администратора**
2. Удалите lock файл:
   ```powershell
   Remove-Item "C:\ProgramData\chocolatey\lib\80b5db4ae59a27a4e5a98bc869b3316f892f2838" -Force -ErrorAction SilentlyContinue
   ```
3. Повторите установку:
   ```powershell
   choco install nodejs
   ```

**Или просто используйте официальный установщик** - он не требует прав администратора и проще в использовании.

## Быстрая проверка установки

Запустите скрипт проверки (PowerShell):
```powershell
cd frontend
.\check-node.ps1
```

## Дополнительная информация

- Документация Node.js: https://nodejs.org/docs/
- Документация npm: https://docs.npmjs.com/
- Документация Vite: https://vitejs.dev/
