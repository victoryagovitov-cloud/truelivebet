@echo off
chcp 65001 >nul
echo 🚀 TrueLiveBet - Реальный тест Telegram каждые 5 минут
echo ======================================================
echo.
echo 📁 Переход в папку automation...
cd automation
echo.
echo 🐍 Запуск Python скрипта с реальной отправкой...
echo ⏰ Интервал: 5 минут
echo 📱 Канал: @truelivebet
echo 🔑 Токен: Настроен в config.py
echo.
echo 💡 Для остановки нажмите Ctrl+C
echo.
python real_telegram_sender.py
echo.
echo ⏸️ Скрипт завершен. Нажмите любую клавишу для выхода...
pause >nul
