@echo off
title TrueLiveBet - Быстрый запуск по схеме
echo 🚀 TrueLiveBet - Быстрый запуск по схеме
echo ===========================================
echo.
echo 📋 Схема работы ОТРАБОТАНА И СОХРАНЕНА
echo ✅ Все файлы готовы к работе
echo 🔄 Запускаю автоматический анализ...
echo.

REM Запускаем анализ и отправку
python send_to_telegram_fixed.py

echo.
echo ✅ Анализ завершен по схеме!
echo 📱 Результаты отправлены в Telegram
echo.
echo ⏸️ Нажмите любую клавишу для закрытия...
pause >nul
