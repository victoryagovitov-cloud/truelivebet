#!/bin/bash

echo "🧠 Sports Analyzer System - Быстрый запуск"
echo "=========================================="

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python3"
    exit 1
fi

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
pip3 install -r requirements.txt --break-system-packages

# Запускаем одноразовый анализ
echo "🚀 Запускаем анализ..."
python3 start_analyzer.py --mode once

echo "✅ Анализ завершен!"
echo "📁 Проверьте файл sports_analyzer.log для деталей"