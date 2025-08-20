#!/usr/bin/env python3
"""
TrueLiveBet - Конфигурация автоматизации
Автор: Виктор
"""

import os
from typing import Dict

# Telegram Bot Token (ОБЯЗАТЕЛЬНО)
TELEGRAM_BOT_TOKEN = "7824400107:AAGZqPdS0E0N3HsYpD8TW9m8c-bapFd-RHk"

# AI API ключи (опционально)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # None если не указан
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')  # None если не указан

# Telegram канал для публикации прогнозов
TELEGRAM_CHANNEL_ID = "@truelivebet"

# Тестовый чат ID (замени на свой)
TEST_CHAT_ID = 123456789

# Интервал анализа в секундах (5 минут по умолчанию)
CYCLE_INTERVAL = 300

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_ROTATION = "1 day"
LOG_RETENTION = "7 days"

# Настройки браузера
BROWSER_HEADLESS = False  # False для отладки, True для продакшена
BROWSER_TIMEOUT = 10000  # 10 секунд

# Настройки AI
AI_MAX_TOKENS = 1000
AI_TEMPERATURE = 0.1

def get_config() -> Dict:
    """Получение конфигурации в виде словаря"""
    return {
        'telegram_token': TELEGRAM_BOT_TOKEN,
        'telegram_channel_id': TELEGRAM_CHANNEL_ID,
        'openai_api_key': OPENAI_API_KEY,
        'anthropic_api_key': ANTHROPIC_API_KEY,
        'test_chat_id': TEST_CHAT_ID,
        'cycle_interval': CYCLE_INTERVAL,
        'log_level': LOG_LEVEL,
        'log_rotation': LOG_ROTATION,
        'log_retention': LOG_RETENTION,
        'browser_headless': BROWSER_HEADLESS,
        'browser_timeout': BROWSER_TIMEOUT,
        'ai_max_tokens': AI_MAX_TOKENS,
        'ai_temperature': AI_TEMPERATURE
    }

def validate_config() -> bool:
    """Проверка корректности конфигурации"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ ОШИБКА: Не указан TELEGRAM_BOT_TOKEN")
        return False
    
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("❌ ОШИБКА: Замените TELEGRAM_BOT_TOKEN на реальный токен")
        return False
    
    print("✅ Конфигурация корректна")
    return True

if __name__ == "__main__":
    print("🔧 Конфигурация TrueLiveBet:")
    config = get_config()
    for key, value in config.items():
        if 'token' in key.lower() and value and isinstance(value, str):
            # Скрываем токен для безопасности
            print(f"{key}: {value[:10]}...{value[-10:]}")
        else:
            print(f"{key}: {value}")
    
    print("\n" + "="*50)
    validate_config()
