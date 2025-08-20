#!/usr/bin/env python3
"""
Простой тест системы TrueLiveBet
"""

print("🚀 TrueLiveBet - Простой тест")
print("=" * 40)

# Тест 1: Проверка конфигурации
print("\n1️⃣ Тест конфигурации...")
try:
    import config
    print(f"✅ Конфигурация загружена")
    print(f"   Канал: {config.TELEGRAM_CHANNEL_ID}")
    print(f"   Токен: {config.TELEGRAM_BOT_TOKEN[:10]}...{config.TELEGRAM_BOT_TOKEN[-10:]}")
except Exception as e:
    print(f"❌ Ошибка конфигурации: {e}")

# Тест 2: Проверка импортов
print("\n2️⃣ Тест импортов...")
try:
    from ai_analyzer import AIAnalyzer
    print("✅ AI анализатор импортирован")
except Exception as e:
    print(f"❌ Ошибка импорта AI анализатора: {e}")

try:
    from telegram_bot import TrueLiveBetBot
    print("✅ Telegram бот импортирован")
except Exception as e:
    print(f"❌ Ошибка импорта Telegram бота: {e}")

try:
    from channel_publisher import ChannelPublisher
    print("✅ Издатель канала импортирован")
except Exception as e:
    print(f"❌ Ошибка импорта издателя канала: {e}")

# Тест 3: Проверка форматирования
print("\n3️⃣ Тест форматирования...")
try:
    from datetime import datetime
    
    # Создаем тестовый анализ
    class TestAnalysis:
        def __init__(self):
            self.match_id = "test_match"
            self.confidence = 85.5
            self.recommendation = "Ставить на победу команды 1"
            self.reasoning = "Команда 1 ведет 2:0, контроль мяча 65%, удары 8:2"
            self.risk_level = "средний"
            self.category = "🎯"
            self.timestamp = datetime.now().isoformat()
    
    test_analysis = TestAnalysis()
    print(f"✅ Тестовый анализ создан: {test_analysis.category} - {test_analysis.confidence:.1f}%")
    
    # Тестируем форматирование
    category_name = {
        "💀": "МЕРТВЫЕ (>95%)",
        "🎯": "ИДЕАЛЬНЫЕ (85-95%)", 
        "⭐": "ОТЛИЧНЫЕ (80-85%)",
        "👍": "ХОРОШИЕ (75-80%)"
    }.get(test_analysis.category, "АНАЛИЗ")
    
    print(f"   Категория: {category_name}")
    
except Exception as e:
    print(f"❌ Ошибка тестирования: {e}")

print("\n" + "=" * 40)
print("🏁 Тест завершен!")
print("\n📱 Следующие шаги:")
print("1. Установите зависимости: pip install -r requirements.txt")
print("2. Протестируйте бота: python test_bot.py")
print("3. Запустите систему: python main.py")
