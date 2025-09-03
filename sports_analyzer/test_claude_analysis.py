#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Claude анализа
"""

import asyncio
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.advanced_claude_analyzer import AdvancedClaudeAnalyzer


async def test_football_analysis():
    """Тест анализа футбольного матча"""
    print("🔍 Тестируем анализ футбольного матча...")
    
    analyzer = AdvancedClaudeAnalyzer()
    
    # Тестовые данные
    betboom_data = {
        "team1": "Манчестер Сити",
        "team2": "Ливерпуль",
        "score": "2:1", 
        "minute": 67,
        "league": "Премьер-лига",
        "odds": {"1": 1.85, "X": 3.20, "2": 4.50}
    }
    
    scores24_data = {
        "league_position1": 2,
        "league_position2": 3,
        "form1": "WWWDW",
        "form2": "WDWLW",
        "recent_goals1": 12,
        "recent_goals2": 8,
        "league_level": "top"
    }
    
    result = await analyzer.analyze_football_match(betboom_data, scores24_data)
    
    print("⚽ Результат анализа футбола:")
    print(f"   Уверенность: {result.get('confidence')}%")
    print(f"   Фаворит ведет: {result.get('is_favorite_leading')}")
    print(f"   Обоснование: {result.get('reasoning')}")
    print(f"   Рекомендация: {result.get('recommendation')}")
    print()


async def test_tennis_analysis():
    """Тест анализа теннисного матча"""
    print("🔍 Тестируем анализ теннисного матча...")
    
    analyzer = AdvancedClaudeAnalyzer()
    
    betboom_data = {
        "player1": "Новак Джокович",
        "player2": "Рафаэль Надаль",
        "sets_score": "1-0",
        "games_score": "6-4, 3-1",
        "tournament": "Australian Open",
        "odds": {"1": 1.65, "2": 2.20}
    }
    
    scores24_data = {
        "ranking1": 1,
        "ranking2": 2,
        "form1": "WWWLW",
        "form2": "WLWWL", 
        "head_to_head": "15-10",
        "surface_preference1": "hard",
        "surface_preference2": "clay"
    }
    
    result = await analyzer.analyze_tennis_match(betboom_data, scores24_data)
    
    print("🎾 Результат анализа тенниса:")
    print(f"   Уверенность: {result.get('confidence')}%")
    print(f"   Фаворит ведет: {result.get('is_favorite_leading')}")
    print(f"   Обоснование: {result.get('reasoning')}")
    print(f"   Рекомендация: {result.get('recommendation')}")
    print()


async def test_handball_total_analysis():
    """Тест анализа тотала в гандболе"""
    print("🔍 Тестируем анализ тотала в гандболе...")
    
    analyzer = AdvancedClaudeAnalyzer()
    
    betboom_data = {
        "team1": "Барселона",
        "team2": "Киль",
        "score": "25:23",
        "minute": 40,
        "half": 2,
        "analysis_type": "total",
        "total_goals": 48,
        "minutes_played": 40,
        "predicted_total": 72
    }
    
    scores24_data = {
        "avg_goals_per_match1": 32.5,
        "avg_goals_per_match2": 28.3,
        "form1": "WWWDW",
        "form2": "WDLWW"
    }
    
    result = await analyzer.analyze_handball_with_context(betboom_data, scores24_data)
    
    print("🤾 Результат анализа гандбольного тотала:")
    print(f"   Уверенность: {result.get('confidence')}%")
    print(f"   Темп игры: {result.get('pace')}")
    print(f"   Рекомендация: {result.get('recommendation')}")
    print(f"   Обоснование: {result.get('reasoning')}")
    print()


async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов Claude анализатора...\n")
    
    try:
        # Запускаем все тесты параллельно
        await asyncio.gather(
            test_football_analysis(),
            test_tennis_analysis(), 
            test_handball_total_analysis()
        )
        
        print("✅ Все тесты завершены успешно!")
        print("\n💡 Для использования реального Claude API:")
        print("   1. Получите API ключ на console.anthropic.com")
        print("   2. Установите: export CLAUDE_API_KEY='your-key'")
        print("   3. Перезапустите анализатор")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")


if __name__ == "__main__":
    asyncio.run(main())