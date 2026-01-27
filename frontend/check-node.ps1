# Скрипт проверки установки Node.js и npm

Write-Host "Проверка установки Node.js и npm..." -ForegroundColor Cyan
Write-Host ""

# Проверка Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js установлен: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js НЕ установлен" -ForegroundColor Red
    Write-Host ""
    Write-Host "Для установки Node.js:" -ForegroundColor Yellow
    Write-Host "1. Перейдите на https://nodejs.org/" -ForegroundColor Yellow
    Write-Host "2. Скачайте LTS версию" -ForegroundColor Yellow
    Write-Host "3. Запустите установщик" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Проверка npm
try {
    $npmVersion = npm --version 2>&1
    Write-Host "✓ npm установлен: v$npmVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ npm НЕ установлен" -ForegroundColor Red
    Write-Host "npm обычно устанавливается вместе с Node.js" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Проверка версий:" -ForegroundColor Cyan

# Проверка минимальных версий
$nodeVersionNumber = (node --version).Replace('v', '').Split('.')[0]
$npmVersionNumber = (npm --version).Split('.')[0]

if ([int]$nodeVersionNumber -lt 18) {
    Write-Host "⚠ Предупреждение: Рекомендуется Node.js версии 18 или выше" -ForegroundColor Yellow
    Write-Host "  Текущая версия: $nodeVersion" -ForegroundColor Yellow
} else {
    Write-Host "✓ Версия Node.js соответствует требованиям (>= 18)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Готово! Вы можете запустить:" -ForegroundColor Green
Write-Host "  npm install" -ForegroundColor Cyan
Write-Host "  npm run dev" -ForegroundColor Cyan
