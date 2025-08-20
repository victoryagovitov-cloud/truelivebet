#!/usr/bin/env python3
"""
TrueLiveBet - Автоматический отправитель в Telegram
Работает по расписанию и автоматически анализирует матчи
"""

import json
import os
import time
import schedule
from datetime import datetime
import urllib.request
import urllib.parse
import threading

class AutoTelegramSender:
    """Автоматический отправитель в Telegram"""
    
    def __init__(self, token: str, chat_id: str = "@truelivebet"):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.last_sent_files = set()  # Отслеживаем уже отправленные файлы
        self.is_running = False
        
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
        
        current_files = set()
        
        # Ищем все файлы рекомендаций
        for filename in os.listdir(recommendations_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(recommendations_dir, filename)
                current_files.add(filename)
                
                # Если файл новый - отправляем его
                if filename not in self.last_sent_files:
                    print(f"🆕 Найден новый файл: {filename}")
                    self.send_file(file_path)
                    self.last_sent_files.add(filename)
        
        # Удаляем несуществующие файлы из отслеживания
        self.last_sent_files = self.last_sent_files.intersection(current_files)
    
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
📊 **АВТОМАТИЧЕСКИЙ АНАЛИЗ ЛАЙВ МАТЧЕЙ BETBOOM**

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
    
    def send_daily_summary(self):
        """Отправляет ежедневную сводку"""
        message = f"""
📅 **ЕЖЕДНЕВНАЯ СВОДКА TRUELIVEBET**

⏰ Дата: {datetime.now().strftime('%d.%m.%Y')}
🕐 Время: {datetime.now().strftime('%H:%M:%S')} (МСК)

📊 **Статистика за день:**
• Файлов обработано: {len(self.last_sent_files)}
• Рекомендаций отправлено: {len([f for f in self.last_sent_files if 'recommendation' in f])}
• Анализов отправлено: {len([f for f in self.last_sent_files if 'analysis' in f])}

🎯 **Система работает автоматически**
🤖 TrueLiveBet Bot v2.0
        """
        
        print("📅 Отправляю ежедневную сводку...")
        self.send_message(message)
    
    def start_monitoring(self):
        """Запускает автоматический мониторинг"""
        print("🚀 TrueLiveBet - Автоматический отправитель запущен!")
        print("=" * 60)
        print(f"💬 Канал: {self.chat_id}")
        print(f"⏰ Время запуска: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        # Настраиваем расписание
        schedule.every(5).minutes.do(self.check_new_files)  # Каждые 5 минут
        schedule.every().hour.do(self.send_daily_summary)    # Каждый час
        
        print("📅 Расписание настроено:")
        print("   • Проверка новых файлов: каждые 5 минут")
        print("   • Ежедневная сводка: каждый час")
        print("=" * 60)
        
        self.is_running = True
        
        # Запускаем основной цикл
        while self.is_running:
            schedule.run_pending()
            time.sleep(30)  # Проверяем расписание каждые 30 секунд
    
    def stop_monitoring(self):
        """Останавливает автоматический мониторинг"""
        self.is_running = False
        print("⏹️ Автоматический мониторинг остановлен")

def main():
    """Главная функция"""
    token = "7824400107:AAGZqPdS0E0N3HsYpD8TW9m8c-bapFd-RHk"
    
    # Создаем автоматический отправитель
    sender = AutoTelegramSender(token)
    
    try:
        # Запускаем автоматический мониторинг
        sender.start_monitoring()
    except KeyboardInterrupt:
        print("\n⏹️ Получен сигнал остановки...")
        sender.stop_monitoring()
        print("👋 До свидания!")

if __name__ == "__main__":
    main()
