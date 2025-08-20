#!/usr/bin/env python3
"""
TrueLiveBet - Умный автоматический отправитель в Telegram
Работает по событиям: отправляет только новые файлы
"""

import json
import os
import time
from datetime import datetime
import urllib.request
import urllib.parse

class SmartTelegramSender:
    """Умный отправитель в Telegram - работает по событиям"""
    
    def __init__(self, token: str, chat_id: str = "@truelivebet"):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.sent_files = set()  # Уже отправленные файлы
        self.last_check = 0      # Время последней проверки
        
    def send_message(self, text: str) -> bool:
        """Отправляет сообщение в Telegram"""
        try:
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }
            
            encoded_data = urllib.parse.urlencode(data).encode('utf-8')
            req = urllib.request.Request(
                f"{self.api_url}/sendMessage",
                data=encoded_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('ok'):
                    print(f"✅ Сообщение отправлено! ID: {result['result']['message_id']}")
                    return True
                else:
                    print(f"❌ Ошибка Telegram: {result.get('description', 'Неизвестная ошибка')}")
                    return False
                
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            return False
    
    def check_new_files(self):
        """Проверяет новые файлы и отправляет их"""
        recommendations_dir = "recommendations"
        
        if not os.path.exists(recommendations_dir):
            return
        
        current_time = time.time()
        
        # Проверяем каждые 30 секунд (не каждые 5 минут!)
        if current_time - self.last_check < 30:
            return
        
        self.last_check = current_time
        
        # Ищем все файлы рекомендаций
        for filename in os.listdir(recommendations_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(recommendations_dir, filename)
                
                # Если файл новый - отправляем его
                if filename not in self.sent_files:
                    print(f"🆕 Найден новый файл: {filename}")
                    self.send_file(file_path)
                    self.sent_files.add(filename)
                    
                    # Небольшая задержка между отправками
                    time.sleep(2)
    
    def send_file(self, file_path: str):
        """Отправляет файл в зависимости от его типа"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'text' in data:  # Файл рекомендации
                message_text = data.get('text', 'Нет текста рекомендации')
                print(f"📤 Отправляю рекомендацию: {os.path.basename(file_path)}")
            else:  # Файл анализа
                message_text = self.format_analysis_message(data)
                print(f"📤 Отправляю анализ: {os.path.basename(file_path)}")
            
            # Отправляем в Telegram
            success = self.send_message(message_text)
            
            if success:
                print(f"✅ Файл {os.path.basename(file_path)} успешно отправлен!")
            else:
                print(f"❌ Ошибка отправки файла {os.path.basename(file_path)}")
                
        except Exception as e:
            print(f"❌ Ошибка обработки файла {file_path}: {e}")
    
    def format_analysis_message(self, data):
        """Форматирует сообщение анализа"""
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
        message_text += "\n🤖 *Сообщение отправлено автоматически*"
        
        return message_text
    
    def start_monitoring(self):
        """Запускает умный мониторинг"""
        print("🚀 TrueLiveBet - Умный автоматический отправитель запущен!")
        print("=" * 60)
        print(f"💬 Канал: {self.chat_id}")
        print(f"⏰ Время запуска: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        print("📋 Как это работает:")
        print("   1. Вы анализируете Betboom через чат (как обычно)")
        print("   2. Создаете файлы рекомендаций")
        print("   3. Система автоматически отправляет их в Telegram")
        print("   4. Проверка каждые 30 секунд (не каждые 5 минут!)")
        print("=" * 60)
        
        # Основной цикл мониторинга
        try:
            while True:
                self.check_new_files()
                time.sleep(10)  # Проверяем каждые 10 секунд
                
        except KeyboardInterrupt:
            print("\n⏹️ Получен сигнал остановки...")
            print("👋 До свидания!")

def main():
    """Главная функция"""
    token = "7824400107:AAGZqPdS0E0N3HsYpD8TW9m8c-bapFd-RHk"
    
    # Создаем умный отправитель
    sender = SmartTelegramSender(token)
    
    # Запускаем мониторинг
    sender.start_monitoring()

if __name__ == "__main__":
    main()
