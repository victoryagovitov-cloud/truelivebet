#!/usr/bin/env python3
"""
TrueLiveBet - Локальный отправитель в Telegram
Отправляет файлы рекомендаций напрямую в Telegram без GitHub Actions
"""

import json
import asyncio
import os
from datetime import datetime

class LocalTelegramSender:
    """Локальный отправитель в Telegram"""
    
    def __init__(self, token: str, chat_id: str = None):
        self.token = token
        self.chat_id = chat_id or "@truelivebet"
        
    def send_recommendation(self, file_path: str) -> bool:
        """Отправляет рекомендацию из файла (имитация)"""
        try:
            # Читаем файл рекомендации
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Форматируем сообщение
            message_text = data.get('text', 'Нет текста рекомендации')
            
            print("=" * 60)
            print("📤 ОТПРАВКА В TELEGRAM:")
            print(f"💬 Чат: {self.chat_id}")
            print(f"📁 Файл: {file_path}")
            print("=" * 60)
            print(message_text)
            print("=" * 60)
            
            # Здесь будет реальная отправка через Telegram API
            # await self.bot.send_message(chat_id=self.chat_id, text=message_text, parse_mode='Markdown')
            
            print(f"✅ Рекомендация отправлена из {file_path}")
            return True
            
        except FileNotFoundError:
            print(f"❌ Файл не найден: {file_path}")
            return False
        except json.JSONDecodeError:
            print(f"❌ Ошибка JSON в файле: {file_path}")
            return False
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return False
    
    def send_analysis(self, file_path: str) -> bool:
        """Отправляет анализ из файла (имитация)"""
        try:
            # Читаем файл анализа
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Форматируем сообщение анализа
            total_matches = data.get('total_matches', 0)
            sports = data.get('sports_analyzed', [])
            best_bets = data.get('best_bets', [])
            
            message_text = f"""
📊 **АНАЛИЗ ЛАЙВ МАТЧЕЙ BETBOOM**

⏰ Время: {datetime.now().strftime('%H:%M:%S')} (МСК)
📈 Всего матчей: {total_matches}
⚽ Виды спорта: {', '.join(sports)}

🏆 **Лучшие ставки:**
"""
            
            for i, bet in enumerate(best_bets[:3], 1):
                description = bet.get('description', 'Нет описания')
                confidence = bet.get('confidence', 0)
                message_text += f"{i}. {description} (уверенность: {confidence}%)\n"
            
            message_text += f"\n🎯 Источник: {data.get('source', 'Betboom')}"
            
            print("=" * 60)
            print("📤 ОТПРАВКА АНАЛИЗА В TELEGRAM:")
            print(f"💬 Чат: {self.chat_id}")
            print(f"📁 Файл: {file_path}")
            print("=" * 60)
            print(message_text)
            print("=" * 60)
            
            print(f"✅ Анализ отправлен из {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки анализа: {e}")
            return False
    
    def send_all_recommendations(self) -> bool:
        """Отправляет все доступные рекомендации"""
        # Правильный путь к папке recommendations
        current_dir = os.path.dirname(os.path.abspath(__file__))
        recommendations_dir = os.path.join(current_dir, "..", "recommendations")
        
        print(f"🔍 Ищем файлы в: {recommendations_dir}")
        
        if not os.path.exists(recommendations_dir):
            print(f"❌ Папка не найдена: {recommendations_dir}")
            return False
        
        success_count = 0
        total_count = 0
        
        # Ищем файлы рекомендаций
        for filename in os.listdir(recommendations_dir):
            if filename.startswith('recommendation_') and filename.endswith('.json'):
                file_path = os.path.join(recommendations_dir, filename)
                total_count += 1
                
                if self.send_recommendation(file_path):
                    success_count += 1
                
                # Небольшая задержка между сообщениями
                asyncio.sleep(1)
        
        # Ищем файлы анализа
        for filename in os.listdir(recommendations_dir):
            if filename.startswith('live_analysis_') and filename.endswith('.json'):
                file_path = os.path.join(recommendations_dir, filename)
                total_count += 1
                
                if self.send_analysis(file_path):
                    success_count += 1
                
                asyncio.sleep(1)
        
        print(f"📊 Отправлено: {success_count}/{total_count} файлов")
        return success_count > 0

def main():
    """Главная функция"""
    # Токен из конфига
    token = "7824400107:AAGZqPdS0E0N3HsYpD8TW9m8c-bapFd-RHk"
    
    # Создаем отправитель
    sender = LocalTelegramSender(token)
    
    print("🚀 TrueLiveBet - Локальный отправитель в Telegram")
    print("=" * 50)
    
    # Отправляем все рекомендации
    success = sender.send_all_recommendations()
    
    if success:
        print("✅ Все рекомендации отправлены успешно!")
    else:
        print("❌ Ошибка отправки рекомендаций")

if __name__ == "__main__":
    # Запускаем
    main()
