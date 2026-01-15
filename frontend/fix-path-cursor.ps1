# Скрипт для обновления PATH в текущей сессии PowerShell Cursor
# Используйте этот скрипт, если npm не распознаётся в Cursor после установки Node.js

Write-Host "Обновление PATH для текущей сессии..." -ForegroundColor Cyan
Write-Host ""

# Получаем системный PATH
$systemPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")

# Объединяем пути
$fullPath = "$systemPath;$userPath"

# Обновляем PATH в текущей сессии
$env:PATH = $fullPath

Write-Host "✓ PATH обновлён" -ForegroundColor Green
Write-Host ""

# Проверяем Node.js и npm
Write-Host "Проверка Node.js и npm:" -ForegroundColor Cyan
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js не найден" -ForegroundColor Red
}

try {
    $npmVersion = npm --version 2>&1
    Write-Host "✓ npm: v$npmVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ npm не найден" -ForegroundColor Red
    Write-Host ""
    Write-Host "Попробуйте перезапустить Cursor полностью" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Теперь вы можете выполнить:" -ForegroundColor Green
Write-Host "  npm install" -ForegroundColor Cyan
