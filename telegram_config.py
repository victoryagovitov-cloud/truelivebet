#!/usr/bin/env python3
"""
Конфигурация для Telegram бота
Замените значения на свои!
"""

# Настройки Telegram бота
TELEGRAM_CONFIG = {
    "bot_token": "YOUR_BOT_TOKEN_HERE",  # Замените на ваш токен бота
    "chat_id": "@truelivebet",  # ID чата или канала
    "test_mode": True  # Режим тестирования
}

# Примеры прогнозов для тестирования
SAMPLE_PREDICTIONS = [
    {
        "match": "Спартак - ЦСКА",
        "prediction": "Победа Спартака",
        "confidence": 85,
        "odds": 2.15,
        "analysis": "Спартак в отличной форме, играет дома, последние 5 матчей выиграл"
    },
    {
        "match": "Зенит - Локомотив", 
        "prediction": "Ничья",
        "confidence": 72,
        "odds": 3.40,
        "analysis": "Обе команды в равной форме, исторически много ничьих"
    },
    {
        "match": "Динамо - Краснодар",
        "prediction": "Победа Краснодара",
        "confidence": 78,
        "odds": 2.85,
        "analysis": "Краснодар показывает стабильную игру в гостях"
    }
]

# Настройки форматирования
MESSAGE_TEMPLATE = """
⚽ **ПРОГНОЗ НА МАТЧ: {match}**

🎯 **Прогноз:** {prediction}
📊 **Уверенность:** {confidence}%
💰 **Коэффициент:** {odds}

📝 **Анализ:** {analysis}

🚀 **TrueLiveBet система всегда на вашей стороне!** ⚽📱
"""
