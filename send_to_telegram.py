#!/usr/bin/env python3
"""
TrueLiveBet - Простой отправитель в Telegram
Отправляет файлы рекомендаций прямо в Telegram
"""

import json
import os
from datetime import datetime

def read_json_file(file_path):
    """Читает JSON файл"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка чтения {file_path}: {e}")
        return None

def format_recommendation_message(data):
    """Форматирует сообщение рекомендации"""
    return data.get('text', 'Нет текста рекомендации')

def format_analysis_message(data):
    """Форматирует сообщение анализа"""
    total_matches = data.get('total_matches', 0)
    sports = data.get('sports_analyzed', [])
    best_bets = data.get('best_bets', [])
    
    message = f"""
📊 **АНАЛИЗ ЛАЙВ МАТЧЕЙ BETBOOM**

⏰ Время: {datetime.now().strftime('%H:%M:%S')} (МСК)
📈 Всего матчей: {total_matches}
⚽ Виды спорта: {', '.join(sports)}

🏆 **Лучшие ставки:**
"""
    
    for i, bet in enumerate(best_bets[:3], 1):
        description = bet.get('description', 'Нет описания')
        confidence = bet.get('confidence', 0)
        message += f"{i}. {description} (уверенность: {confidence}%)\n"
    
    message += f"\n🎯 Источник: {data.get('source', 'Betboom')}"
    return message

def send_to_telegram(message, chat_id="@truelivebet"):
    """Отправляет сообщение в Telegram (пока только в консоль)"""
    print("=" * 80)
    print("📤 ОТПРАВКА В TELEGRAM:")
    print(f"💬 Чат: {chat_id}")
    print(f"⏰ Время: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)
    print(message)
    print("=" * 80)
    print("✅ Сообщение готово к отправке в Telegram!")
    print("🔗 Для реальной отправки нужно подключить python-telegram-bot")
    print("=" * 80)

def main():
    """Главная функция"""
    print("🚀 TrueLiveBet - Отправитель в Telegram")
    print("=" * 50)
    
    # Папка с рекомендациями
    recommendations_dir = "recommendations"
    
    if not os.path.exists(recommendations_dir):
        print(f"❌ Папка не найдена: {recommendations_dir}")
        return
    
    print(f"🔍 Ищем файлы в: {os.path.abspath(recommendations_dir)}")
    
    # Список файлов для отправки
    files_to_send = []
    
    # Ищем файлы рекомендаций
    for filename in os.listdir(recommendations_dir):
        if filename.startswith('recommendation_') and filename.endswith('.json'):
            files_to_send.append(('recommendation', os.path.join(recommendations_dir, filename)))
        elif filename.startswith('live_analysis_') and filename.endswith('.json'):
            files_to_send.append(('analysis', os.path.join(recommendations_dir, filename)))
    
    if not files_to_send:
        print("❌ Файлы для отправки не найдены")
        return
    
    print(f"📁 Найдено файлов: {len(files_to_send)}")
    
    # Отправляем каждый файл
    for file_type, file_path in files_to_send:
        print(f"\n📤 Обрабатываю: {file_path}")
        
        data = read_json_file(file_path)
        if not data:
            continue
        
        if file_type == 'recommendation':
            message = format_recommendation_message(data)
        else:
            message = format_analysis_message(data)
        
        send_to_telegram(message)
    
    print(f"\n🎉 Обработано файлов: {len(files_to_send)}")
    print("📱 Теперь можно подключить реальный Telegram API!")

if __name__ == "__main__":
    main()
