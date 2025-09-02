@echo off
echo ========================================
echo    TrueLiveBet Sports Analyzer
echo ========================================
echo.

cd /d "%~dp0"

echo Установка зависимостей...
pip install -r requirements.txt

echo.
echo Запуск анализатора...
python start_analyzer.py --mode schedule

pause