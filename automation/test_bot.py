#!/usr/bin/env python3
"""
TrueLiveBet - Тестирование Telegram бота
Автор: Виктор
"""

import asyncio
from loguru import logger
from telegram_bot import TrueLiveBetBot
from config import TELEGRAM_BOT_TOKEN

async def test_bot():
    """Тестирование бота"""
    try:
        print("🤖 Тестирование TrueLiveBet Telegram бота...")
        print(f"📱 Токен: {TELEGRAM_BOT_TOKEN[:10]}...{TELEGRAM_BOT_TOKEN[-10:]}")
        
        # Создаем бота
        bot = TrueLiveBetBot(TELEGRAM_BOT_TOKEN)
        print("✅ Бот создан успешно")
        
        # Инициализируем
        await bot.application.initialize()
        print("✅ Приложение инициализировано")
        
        # Получаем информацию о боте
        bot_info = await bot.application.bot.get_me()
        print(f"📋 Информация о боте:")
        print(f"   Имя: {bot_info.first_name}")
        print(f"   Username: @{bot_info.username}")
        print(f"   ID: {bot_info.id}")
        
        print("\n🎯 Бот готов к работе!")
        print("💡 Отправь команду /start боту @TrueLiveBetBot")
        
        # Останавливаем бота
        await bot.application.stop()
        await bot.application.shutdown()
        
    except Exception as e:
        logger.error(f"Ошибка тестирования: {e}")
        print(f"❌ Ошибка: {e}")

async def test_commands():
    """Тестирование команд бота"""
    try:
        print("\n🧪 Тестирование команд бота...")
        
        bot = TrueLiveBetBot(TELEGRAM_BOT_TOKEN)
        
        # Тестируем команды
        commands = [
            ("start", "Приветствие"),
            ("help", "Справка"),
            ("about", "О проекте"),
            ("stats", "Статистика"),
            ("analyze", "Анализ"),
            ("live", "Live матчи")
        ]
        
        for command, description in commands:
            try:
                # Проверяем, что команда зарегистрирована
                handlers = bot.application.handlers.get(0, [])
                command_found = any(
                    hasattr(handler, 'command') and handler.command == command
                    for handler in handlers
                )
                
                status = "✅" if command_found else "❌"
                print(f"   {status} /{command} - {description}")
                
            except Exception as e:
                print(f"   ❌ /{command} - Ошибка: {e}")
        
        print("\n🎯 Тестирование команд завершено!")
        
    except Exception as e:
        logger.error(f"Ошибка тестирования команд: {e}")

async def main():
    """Главная функция тестирования"""
    print("🚀 TrueLiveBet - Тестирование системы")
    print("=" * 50)
    
    # Тестируем бота
    await test_bot()
    
    # Тестируем команды
    await test_commands()
    
    print("\n" + "=" * 50)
    print("🏁 Тестирование завершено!")
    print("\n📱 Следующие шаги:")
    print("1. Открой @TrueLiveBetBot в Telegram")
    print("2. Отправь команду /start")
    print("3. Протестируй все команды")
    print("4. Если все работает - запускай основную систему!")

if __name__ == "__main__":
    # Настройка логирования
    logger.add("logs/test_bot.log", rotation="1 day", retention="7 days")
    
    # Запуск тестирования
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование остановлено пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        logger.error(f"Критическая ошибка: {e}")
