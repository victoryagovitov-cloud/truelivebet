@echo off
chcp 65001 >nul
echo 🚀 TrueLiveBet - Тестовый цикл каждые 5 минут
echo ================================================
echo.
echo 📁 Переход в папку automation...
cd automation
echo.
echo 🐍 Запуск Python скрипта...
echo ⏰ Интервал: 5 минут
echo 📱 Канал: @truelivebet
echo.
echo 💡 Для остановки нажмите Ctrl+C
echo.
python test_5min_cycle.py
echo.
echo ⏸️ Скрипт завершен. Нажмите любую клавишу для выхода...
pause >nul
