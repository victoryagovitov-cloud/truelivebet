#!/usr/bin/env python3
"""
TrueLiveBet - Веб-приложение для анализа ставок
Запуск: python run.py
"""

from app import app

if __name__ == '__main__':
    print("🎯 TrueLiveBet запускается...")
    print("🌐 Откройте браузер и перейдите по адресу: http://localhost:5000")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )