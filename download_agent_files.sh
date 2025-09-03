#!/bin/bash

echo "🚀 TrueLiveBet Agent - Скачивание файлов"
echo "=========================================="

# Создаем директорию для скачивания
mkdir -p ~/Downloads/truelivebet_agent
cd ~/Downloads/truelivebet_agent

echo "📁 Создана директория: ~/Downloads/truelivebet_agent"

# Копируем основные файлы агента
echo "📋 Копируем основные файлы агента..."
cp -r /workspace/sports_analyzer/ ./sports_analyzer/
cp /workspace/send_to_telegram*.py ./
cp /workspace/smart_telegram_sender.py ./
cp /workspace/telegram_config.py ./
cp /workspace/auto_*.py ./
cp /workspace/*.bat ./
cp /workspace/*.json ./
cp /workspace/*.md ./
cp /workspace/requirements_telegram.txt ./

# Копируем рекомендации и анализы
echo "📊 Копируем рекомендации и анализы..."
cp -r /workspace/recommendations/ ./recommendations/
cp -r /workspace/analysis/ ./analysis/

# Копируем архивы
echo "📦 Копируем готовые архивы..."
cp /workspace/*.tar.gz ./

echo "✅ Все файлы скопированы в ~/Downloads/truelivebet_agent/"
echo "📁 Содержимое директории:"
ls -la

echo ""
echo "🎯 Готовые архивы для скачивания:"
echo "   - truelivebet_agent_files.tar.gz (99K) - основные файлы агента"
echo "   - truelivebet_recommendations.tar.gz (16K) - рекомендации и анализы"
echo "   - truelivebet_agent_complete.tar.gz (117K) - полный архив"
echo ""
echo "📱 Для запуска агента:"
echo "   cd sports_analyzer && python3 start_analyzer.py --mode once"
echo "   python3 send_to_telegram_smart.py"