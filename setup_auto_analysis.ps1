# TrueLiveBet - Настройка автоматического анализа
# Запускать от имени администратора

Write-Host "🚀 TrueLiveBet - Настройка автоматического анализа" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""

# Проверяем права администратора
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Этот скрипт требует права администратора!" -ForegroundColor Red
    Write-Host "Запустите PowerShell от имени администратора" -ForegroundColor Yellow
    pause
    exit
}

Write-Host "✅ Права администратора подтверждены" -ForegroundColor Green
Write-Host ""

# Получаем путь к проекту
$projectPath = Get-Location
$batFile = Join-Path $projectPath "auto_analysis.bat"

Write-Host "📁 Путь к проекту: $projectPath" -ForegroundColor Cyan
Write-Host "📄 Файл для запуска: $batFile" -ForegroundColor Cyan
Write-Host ""

# Создаем задачу в планировщике Windows
$taskName = "TrueLiveBet_AutoAnalysis"
$taskDescription = "Автоматический анализ матчей BetBoom каждые 4 часа"

Write-Host "🔧 Создаю задачу в планировщике Windows..." -ForegroundColor Yellow

# Удаляем существующую задачу, если есть
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "🗑️ Удалена существующая задача" -ForegroundColor Yellow
} catch {
    # Задача не существовала
}

# Создаем новую задачу
$action = New-ScheduledTaskAction -Execute $batFile -WorkingDirectory $projectPath
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 4) -RepetitionDuration (New-TimeSpan -Days 365)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $taskDescription
    Write-Host "✅ Задача успешно создана!" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка создания задачи: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Попробуйте создать задачу вручную через Планировщик задач Windows" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Инструкция по ручной настройке:" -ForegroundColor Cyan
Write-Host "1. Откройте 'Планировщик задач Windows'" -ForegroundColor White
Write-Host "2. Создайте 'Простую задачу'" -ForegroundColor White
Write-Host "3. Название: TrueLiveBet_AutoAnalysis" -ForegroundColor White
Write-Host "4. Триггер: Каждые 4 часа" -ForegroundColor White
Write-Host "5. Действие: Запуск программы" -ForegroundColor White
Write-Host "6. Программа: $batFile" -ForegroundColor White
Write-Host "7. Рабочая папка: $projectPath" -ForegroundColor White
Write-Host ""

Write-Host "🎯 Теперь анализ будет происходить автоматически каждые 4 часа!" -ForegroundColor Green
Write-Host "📱 Результаты будут отправляться в Telegram канал @truelivebet" -ForegroundColor Green
Write-Host ""

pause
