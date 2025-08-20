#!/usr/bin/env python3
"""
TrueLiveBet - Тестовый цикл анализа каждые 5 минут
Для тестирования системы без внешних API
"""

import asyncio
import time
from datetime import datetime
import json
from config import get_config

print("🚀 TrueLiveBet - Тестовый цикл каждые 5 минут")
print("=" * 60)

# Имитация анализа матча
class MockAnalysis:
    def __init__(self, match_id, confidence, recommendation, reasoning, category):
        self.match_id = match_id
        self.confidence = confidence
        self.recommendation = recommendation
        self.reasoning = reasoning
        self.category = category
        self.timestamp = datetime.now().isoformat()

# Имитация скрапера
class MockScraper:
    def __init__(self):
        self.name = "Mock BetBoom Scraper"
    
    async def start_browser(self):
        print("🌐 Запуск браузера (имитация)")
        await asyncio.sleep(1)
    
    async def get_live_matches(self):
        print("📊 Сбор live матчей с BetBoom (имитация)")
        await asyncio.sleep(2)
        
        # Возвращаем тестовые матчи
        return [
            {
                'sport': '⚽ Футбол',
                'league': 'Премьер-лига',
                'team1': 'Спартак',
                'team2': 'ЦСКА',
                'score': '2:1',
                'time': '75 мин',
                'odds': {'1': 1.85, 'X': 3.40, '2': 4.20}
            },
            {
                'sport': '🎾 Теннис',
                'league': 'ATP 500',
                'team1': 'Новак Джокович',
                'team2': 'Карлос Алькарас',
                'score': '6:4, 5:3',
                'time': '2-й сет',
                'odds': {'1': 1.65, '2': 2.15}
            },
            {
                'sport': '🏀 Баскетбол',
                'league': 'Евролига',
                'team1': 'ЦСКА',
                'team2': 'Реал Мадрид',
                'score': '85:72',
                'time': '4-я четверть',
                'odds': {'1': 1.45, '2': 2.80}
            }
        ]
    
    async def close(self):
        print("🔒 Закрытие браузера (имитация)")
        await asyncio.sleep(1)

# Имитация AI анализатора
class MockAIAnalyzer:
    def __init__(self):
        self.name = "Mock AI Analyzer"
    
    async def analyze_match(self, match):
        print(f"🤖 Анализ матча: {match['team1']} vs {match['team2']}")
        await asyncio.sleep(1)
        
        # Простая логика анализа
        if match['sport'] == '⚽ Футбол':
            if match['score'].startswith('2:1') and match['time'] == '75 мин':
                confidence = 88.5
                category = "🎯"
                recommendation = "Ставить на победу Спартака"
                reasoning = "Спартак ведет 2:1 на 75-й минуте, контроль мяча 60%, удары 12:6"
            else:
                confidence = 75.0
                category = "👍"
                recommendation = "Наблюдать за развитием событий"
                reasoning = "Счет ничейный, время для анализа недостаточно"
        elif match['sport'] == '🎾 Теннис':
            if '6:4, 5:3' in match['score']:
                confidence = 92.0
                category = "💀"
                recommendation = "Ставить на победу Джоковича"
                reasoning = "Джокович выиграл 1-й сет 6:4, ведет 5:3 во 2-м, опыт и рейтинг"
            else:
                confidence = 78.0
                category = "⭐"
                recommendation = "Дождаться завершения сета"
                reasoning = "Сет в процессе, нужна дополнительная информация"
        else:  # Баскетбол
            if '85:72' in match['score'] and '4-я четверть' in match['time']:
                confidence = 95.0
                category = "💀"
                recommendation = "Ставить на победу ЦСКА"
                reasoning = "ЦСКА ведет 85:72 в 4-й четверти, преимущество 13 очков, время почти вышло"
            else:
                confidence = 80.0
                category = "⭐"
                recommendation = "Анализировать динамику четвертей"
                reasoning = "Нужна дополнительная информация о ходе матча"
        
        return MockAnalysis(
            match_id=f"{match['team1']}_{match['team2']}",
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning,
            category=category
        )

# Имитация Telegram бота
class MockTelegramBot:
    def __init__(self, token, channel_id):
        self.token = token
        self.channel_id = channel_id
        self.messages_sent = 0
    
    async def send_message(self, text):
        print(f"📱 ОТПРАВКА В TELEGRAM КАНАЛ: {self.channel_id}")
        print("=" * 60)
        print(text)
        print("=" * 60)
        self.messages_sent += 1
        print(f"✅ Сообщение #{self.messages_sent} отправлено!")
        return True

# Основной класс автоматизации
class TestAutomation:
    def __init__(self):
        self.config = get_config()
        self.scraper = MockScraper()
        self.analyzer = MockAIAnalyzer()
        self.bot = MockTelegramBot(
            self.config['telegram_token'],
            self.config['telegram_channel_id']
        )
        self.cycle_count = 0
        self.is_running = False
    
    async def run_cycle(self):
        """Выполнение одного цикла анализа"""
        self.cycle_count += 1
        current_time = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n🔄 ЦИКЛ #{self.cycle_count} - {current_time}")
        print("=" * 60)
        
        try:
            # 1. Запуск браузера
            await self.scraper.start_browser()
            
            # 2. Сбор матчей
            matches = await self.scraper.get_live_matches()
            print(f"📊 Найдено матчей: {len(matches)}")
            
            # 3. Анализ каждого матча
            analyses = []
            for match in matches:
                analysis = await self.analyzer.analyze_match(match)
                analyses.append(analysis)
                print(f"   {analysis.category} {match['team1']} vs {match['team2']} - {analysis.confidence:.1f}%")
            
            # 4. Фильтрация лучших прогнозов (>80%)
            best_analyses = [a for a in analyses if a.confidence > 80]
            
            if best_analyses:
                print(f"\n🎯 Найдено {len(best_analyses)} качественных прогнозов!")
                
                # 5. Отправка в Telegram
                for analysis in best_analyses:
                    message = self._format_message(analysis, matches)
                    await self.bot.send_message(message)
                    await asyncio.sleep(1)  # Пауза между сообщениями
            else:
                print("⚠️ Качественных прогнозов не найдено")
            
            # 6. Закрытие браузера
            await self.scraper.close()
            
            print(f"✅ Цикл #{self.cycle_count} завершен успешно!")
            
        except Exception as e:
            print(f"❌ Ошибка в цикле #{self.cycle_count}: {e}")
    
    def _format_message(self, analysis, matches):
        """Форматирование сообщения для Telegram"""
        # Находим матч по ID
        match = None
        for m in matches:
            if f"{m['team1']}_{m['team2']}" == analysis.match_id:
                match = m
                break
        
        if not match:
            return "Ошибка: матч не найден"
        
        # Определяем категорию
        category_name = {
            "💀": "МЕРТВЫЕ (>95%)",
            "🎯": "ИДЕАЛЬНЫЕ (85-95%)", 
            "⭐": "ОТЛИЧНЫЕ (80-85%)",
            "👍": "ХОРОШИЕ (75-80%)"
        }.get(analysis.category, "АНАЛИЗ")
        
        message = f"""
⚽ **ПРОГНОЗ НА МАТЧ: {match['team1']} vs {match['team2']}**

🏆 **Категория:** {category_name}
🎯 **Прогноз:** {analysis.recommendation}
📊 **Уверенность:** {analysis.confidence:.1f}%
💰 **Коэффициент:** {match['odds'].get('1', 'N/A')}

📝 **Анализ:** {analysis.reasoning}

⏰ **Время:** {match['time']}
🏟️ **Лига:** {match['league']}

🚀 **TrueLiveBet система всегда на вашей стороне!** ⚽📱
        """
        
        return message.strip()
    
    async def start(self):
        """Запуск автоматизации"""
        print("🚀 Запуск тестовой автоматизации TrueLiveBet...")
        print(f"📱 Канал: {self.config['telegram_channel_id']}")
        print(f"⏰ Интервал: 5 минут")
        print("=" * 60)
        
        self.is_running = True
        
        try:
            while self.is_running:
                await self.run_cycle()
                
                if self.is_running:
                    print(f"\n⏳ Ожидание 5 минут до следующего цикла...")
                    print(f"🕐 Следующий цикл в: {(datetime.now().timestamp() + 300):.0f}")
                    
                    # Ждем 5 минут (300 секунд)
                    await asyncio.sleep(300)
        
        except KeyboardInterrupt:
            print("\n🛑 Остановка автоматизации...")
            self.is_running = False
            await self.scraper.close()
            print("✅ Автоматизация остановлена")

async def main():
    """Главная функция"""
    automation = TestAutomation()
    await automation.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
