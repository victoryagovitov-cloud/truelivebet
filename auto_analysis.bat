@echo off
echo 🚀 TrueLiveBet - АВТОМАТИЧЕСКИЙ АНАЛИЗ МАТЧЕЙ BETBOOM
echo ========================================================
echo.
echo 📱 Автоматический анализ и отправка в Telegram
echo 💬 Канал: @truelivebet
echo ⏰ Время запуска: %date% %time%
echo.

REM Запускаем Python скрипт для анализа
python automation/ai_analyzer.py

REM Отправляем результаты в Telegram
python send_to_telegram_fixed.py

echo.
echo ✅ Автоматический анализ завершен!
echo 📱 Результаты отправлены в Telegram
echo.
echo ⏸️ Нажмите любую клавишу для закрытия...
pause >nul
