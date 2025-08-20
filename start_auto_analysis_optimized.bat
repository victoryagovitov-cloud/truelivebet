@echo off
title TrueLiveBet - Оптимизированный анализ каждые 30 минут
echo 🚀 TrueLiveBet - Оптимизированный анализ матчей BetBoom
echo ===================================================
echo.
echo 📱 Анализ будет происходить каждые 30 минут
echo 💬 Результаты отправляются в Telegram
echo ⏰ Время запуска: %date% %time%
echo.
echo 💡 Оптимальная частота для точного анализа
echo 🔄 Без лишних обновлений, только важная информация
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
echo ✅ Анализ завершен! Следующий запуск через 30 минут...
echo 📱 Результаты отправлены в Telegram канал @truelivebet
echo.

REM Ждем 30 минут (1800 секунд)
timeout /t 1800 /nobreak >nul

echo.
echo 🔄 Перезапускаю анализ...
goto loop
