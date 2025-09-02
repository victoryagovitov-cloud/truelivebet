#!/usr/bin/env python3
"""
Тест реального Claude API анализа
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.claude_api_client import ClaudeAPIClient


async def test_real_claude_football():
    """Тест реального анализа футбольного матча"""
    print("🧠 Тестируем РЕАЛЬНЫЙ Claude API анализ футбола...")
    
    client = ClaudeAPIClient()
    
    # Реалистичные тестовые данные
    betboom_data = {
        "team1": "Манчестер Сити",
        "team2": "Арсенал",
        "score": "2:0",
        "minute": 73,
        "league": "Премьер-лига",
        "odds": {"1": 1.25, "X": 6.50, "2": 9.00}
    }
    
    scores24_data = {
        "league_position1": 1,  # Сити - лидер
        "league_position2": 4,  # Арсенал - 4е место
        "form1": "WWWWW",       # Сити - 5 побед
        "form2": "WDLWL",       # Арсенал - нестабильно
        "recent_goals1": 14,    # Сити забил 14 за 5 матчей
        "recent_goals2": 8,     # Арсенал - 8 голов
        "league_level": "top"
    }
    
    result = await client.analyze_football_match(betboom_data, scores24_data)
    
    print("⚽ РЕЗУЛЬТАТ CLAUDE АНАЛИЗА:")
    print(f"   🎯 Уверенность: {result.get('confidence')}%")
    print(f"   👑 Фаворит ведет: {result.get('is_favorite_leading')}")
    print(f"   💭 Обоснование: {result.get('reasoning')}")
    print(f"   ✅ Рекомендация: {result.get('recommendation')}")
    print()
    
    return result


async def test_real_claude_tennis():
    """Тест реального анализа теннисного матча"""
    print("🧠 Тестируем РЕАЛЬНЫЙ Claude API анализ тенниса...")
    
    client = ClaudeAPIClient()
    
    betboom_data = {
        "player1": "Новак Джокович",
        "player2": "Карлос Алькарас",
        "sets_score": "1-0",
        "games_score": "6-3, 4-2",
        "tournament": "Wimbledon",
        "odds": {"1": 1.95, "2": 1.75}
    }
    
    scores24_data = {
        "ranking1": 1,     # Джокович - №1
        "ranking2": 3,     # Алькарас - №3
        "form1": "WWLWW",  # Джокович - хорошая форма
        "form2": "LWWWW",  # Алькарас - тоже хорошо
        "head_to_head": "3-2",  # Джокович ведет в очных
        "surface_preference1": "grass",  # Джокович любит траву
        "surface_preference2": "clay"    # Алькарас предпочитает грунт
    }
    
    result = await client.analyze_tennis_match(betboom_data, scores24_data)
    
    print("🎾 РЕЗУЛЬТАТ CLAUDE АНАЛИЗА:")
    print(f"   🎯 Уверенность: {result.get('confidence')}%")
    print(f"   👑 Фаворит ведет: {result.get('is_favorite_leading')}")
    print(f"   💭 Обоснование: {result.get('reasoning')}")
    print(f"   ✅ Рекомендация: {result.get('recommendation')}")
    print()
    
    return result


async def main():
    """Главная функция тестирования"""
    print("🚀 ТЕСТ РЕАЛЬНОГО CLAUDE API")
    print("=" * 40)
    print()
    
    try:
        # Тестируем футбол и теннис параллельно
        football_result, tennis_result = await asyncio.gather(
            test_real_claude_football(),
            test_real_claude_tennis()
        )
        
        print("📊 СВОДКА РЕЗУЛЬТАТОВ:")
        print("=" * 25)
        
        total_bets = 0
        if football_result.get('recommendation') == 'bet':
            total_bets += 1
            print(f"⚽ Футбол: РЕКОМЕНДУЕМ ({football_result.get('confidence')}%)")
        else:
            print(f"⚽ Футбол: пропускаем ({football_result.get('confidence')}%)")
        
        if tennis_result.get('recommendation') == 'bet':
            total_bets += 1
            print(f"🎾 Теннис: РЕКОМЕНДУЕМ ({tennis_result.get('confidence')}%)")
        else:
            print(f"🎾 Теннис: пропускаем ({tennis_result.get('confidence')}%)")
        
        print(f"\n🎯 Итого рекомендаций: {total_bets}")
        print()
        
        if total_bets > 0:
            print("✅ Claude AI работает и дает качественные рекомендации!")
        else:
            print("⚠️ Claude AI работает, но текущие матчи не соответствуют критериям")
        
        print("\n🔥 ПРЕИМУЩЕСТВА CLAUDE:")
        print("   • Понимает контекст и нюансы")
        print("   • Учитывает множество факторов одновременно")
        print("   • Дает естественные объяснения")
        print("   • Консервативен в рекомендациях")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")


if __name__ == "__main__":
    asyncio.run(main())