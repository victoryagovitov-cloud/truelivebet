@echo off
echo ========================================
echo    TrueLiveBet Sports Analyzer
echo         С CLAUDE AI АНАЛИЗОМ
echo ========================================
echo.

cd /d "%~dp0"

echo Установка зависимостей...
pip install -r requirements.txt

echo.
echo Тестирование Claude анализа...
python test_claude_analysis.py

echo.
echo Запуск анализатора...
python start_analyzer.py --mode schedule

pause