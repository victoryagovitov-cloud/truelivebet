#!/usr/bin/env python3
"""
Демонстрация работы анализатора с Claude AI
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import SportsAnalyzer


async def demo_single_analysis():
    """Демонстрация одного цикла анализа"""
    print("🎯 ДЕМОНСТРАЦИЯ TRUELIVEBET SPORTS ANALYZER")
    print("=" * 50)
    print()
    
    analyzer = SportsAnalyzer()
    
    print("🔄 Запуск анализа всех видов спорта...")
    print("   (в тестовом режиме с заглушками данных)")
    print()
    
    # Запуск анализа
    results = await analyzer.run_analysis_cycle()
    
    print("📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
    print("=" * 30)
    
    total_recommendations = 0
    for sport, recommendations in results.items():
        sport_names = {
            'football': '⚽ Футбол',
            'tennis': '🎾 Теннис', 
            'table_tennis': '🏓 Настольный теннис',
            'handball': '🤾 Гандбол'
        }
        
        print(f"{sport_names.get(sport, sport)}: {len(recommendations)} рекомендаций")
        total_recommendations += len(recommendations)
    
    print(f"\n📈 Всего найдено: {total_recommendations} рекомендаций")
    print()
    
    if total_recommendations > 0:
        print("✅ Отчет сформирован и отправлен в Telegram!")
    else:
        print("📭 Подходящих матчей не найдено в данный момент")
    
    print()
    print("🔮 ВОЗМОЖНОСТИ CLAUDE AI:")
    print("   • Понимает контекст матча")
    print("   • Учитывает психологические факторы") 
    print("   • Адаптируется к уникальным ситуациям")
    print("   • Дает естественные обоснования")
    print()
    print("🚀 Для реального использования:")
    print("   1. Настройте Claude API ключ")
    print("   2. Подключите Browser MCP")
    print("   3. Запустите: python start_analyzer.py --mode schedule")


if __name__ == "__main__":
    asyncio.run(demo_single_analysis())