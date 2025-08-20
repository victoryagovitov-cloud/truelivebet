@echo off
title TrueLiveBet - Анализ каждый час
echo 🚀 TrueLiveBet - Анализ матчей BetBoom каждый час
echo ===================================================
echo.
echo 📱 Анализ будет происходить каждый час
echo 💬 Результаты отправляются в Telegram
echo ⏰ Время запуска: %date% %time%
echo.
echo 💡 Стабильная частота для регулярных обновлений
echo 🔄 Оптимально для планирования ставок
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
echo ✅ Анализ завершен! Следующий запуск через 1 час...
echo 📱 Результаты отправлены в Telegram канал @truelivebet
echo.

REM Ждем 1 час (3600 секунд)
timeout /t 3600 /nobreak >nul

echo.
echo 🔄 Перезапускаю анализ...
goto loop
