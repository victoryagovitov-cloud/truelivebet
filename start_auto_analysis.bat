@echo off
title TrueLiveBet - Автоматический анализ
echo 🚀 TrueLiveBet - Автоматический анализ матчей BetBoom
echo ===================================================
echo.
echo 📱 Анализ будет происходить каждые 5 минут
echo 💬 Результаты отправляются в Telegram
echo ⏰ Время запуска: %date% %time%
echo.

:loop
echo.
echo 🔍 Запускаю анализ матчей...
echo ⏰ Время: %date% %time%
echo.

REM Запускаем анализ
python automation/ai_analyzer.py

REM Отправляем в Telegram
python send_to_telegram_fixed.py

echo.
echo ✅ Анализ завершен! Следующий запуск через 5 минут...
echo 📱 Результаты отправлены в Telegram канал @truelivebet
echo.

REM Ждем 5 минут (300 секунд)
timeout /t 300 /nobreak >nul

echo.
echo 🔄 Перезапускаю анализ...
goto loop
