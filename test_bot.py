#!/usr/bin/env python3
"""
Тестовый скрипт для TrueLiveBet Bot
"""

import requests
import json
from datetime import datetime

# Конфигурация бота
BOT_TOKEN = '7824400107:AAGZqPdS0E0N3HsYpD8TW9m8c-bapFd-RHk'
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

def test_bot_connection():
    """Тестирует подключение к боту"""
    print("🔍 Тестирую подключение к боту...")
    
    try:
        response = requests.get(f"{BASE_URL}/getMe")
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info['ok']:
                print(f"✅ Бот подключен!")
                print(f"📱 Имя: {bot_info['result']['first_name']}")
                print(f"🔗 Username: @{bot_info['result']['username']}")
                print(f"🆔 ID: {bot_info['result']['id']}")
                return True
            else:
                print(f"❌ Ошибка API: {bot_info}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def get_updates():
    """Получает обновления от бота"""
    print("\n📥 Получаю обновления...")
    
    try:
        response = requests.get(f"{BASE_URL}/getUpdates")
        if response.status_code == 200:
            updates = response.json()
            if updates['ok'] and updates['result']:
                print(f"✅ Найдено {len(updates['result'])} обновлений:")
                
                for update in updates['result']:
                    if 'message' in update:
                        message = update['message']
                        chat_id = message['chat']['id']
                        chat_type = message['chat']['type']
                        user_name = message['from'].get('first_name', 'Неизвестно')
                        
                        print(f"💬 Chat ID: {chat_id} ({chat_type})")
                        print(f"👤 Пользователь: {user_name}")
                        
                        if 'text' in message:
                            print(f"📝 Сообщение: {message['text']}")
                        print("-" * 40)
                        
                        return chat_id
                else:
                    print("📭 Обновлений не найдено")
                    print("💡 Отправьте боту сообщение /start и попробуйте снова")
                    return None
            else:
                print("📭 Обновлений нет")
                return None
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка получения обновлений: {e}")
        return None

def send_test_message(chat_id):
    """Отправляет тестовое сообщение"""
    print(f"\n📤 Отправляю тестовое сообщение в чат {chat_id}...")
    
    test_message = f"""
🎯 <b>TrueLiveBet Bot - Тестовое сообщение</b>

✅ Бот успешно настроен и работает!
⏰ Время: {datetime.now().strftime('%H:%M:%S')}
🔍 Готов к анализу матчей с BetBoom

📊 <b>Что умеет бот:</b>
• Автоматический мониторинг live-матчей
• Анализ по критериям TrueLiveBet
• Уведомления о подходящих матчах
• Периодичность проверки: каждые 30 минут

🎉 <b>Бот готов к работе!</b>
"""
    
    try:
        data = {
            'chat_id': chat_id,
            'text': test_message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(f"{BASE_URL}/sendMessage", data=data)
        
        if response.status_code == 200:
            result = response.json()
            if result['ok']:
                print("✅ Тестовое сообщение отправлено!")
                return True
            else:
                print(f"❌ Ошибка API: {result}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🎯 TrueLiveBet Bot - Тестирование")
    print("=" * 50)
    
    # Тест подключения
    if not test_bot_connection():
        print("❌ Не удалось подключиться к боту")
        return
    
    # Получаем обновления
    chat_id = get_updates()
    
    if chat_id:
        print(f"\n🎯 Найден Chat ID: {chat_id}")
        
        # Отправляем тестовое сообщение
        if send_test_message(chat_id):
            print(f"\n✅ Бот полностью настроен!")
            print(f"📝 Обновите config.py:")
            print(f"   chat_id: '{chat_id}'")
            print(f"\n🚀 Теперь можно запускать auto_analyzer.py!")
        else:
            print("❌ Не удалось отправить тестовое сообщение")
    else:
        print("\n💡 Для получения Chat ID:")
        print("1. Найдите @TrueLiveBetBot в Telegram")
        print("2. Нажмите Start или отправьте /start")
        print("3. Запустите этот скрипт снова")

if __name__ == "__main__":
    main()