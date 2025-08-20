#!/usr/bin/env python3
"""
TrueLiveBet - Исправленный отправитель в Telegram
Без SSL проблем и конфликтов с PostgreSQL
"""

import json
import os
from datetime import datetime
import urllib.request
import urllib.parse

class FixedTelegramSender:
    """Исправленный отправитель в Telegram через urllib"""
    
    def __init__(self, token: str, chat_id: str = "@truelivebet"):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}"
        
    def send_message(self, text: str) -> bool:
        """Отправляет сообщение в Telegram через urllib"""
        try:
            # Подготавливаем данные для отправки
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }
            
            # Кодируем данные
            encoded_data = urllib.parse.urlencode(data).encode('utf-8')
            
            # Создаем запрос
            req = urllib.request.Request(
                f"{self.api_url}/sendMessage",
                data=encoded_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            # Отправляем запрос
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('ok'):
                    print(f"✅ Сообщение отправлено! ID: {result['result']['message_id']}")
                    return True
                else:
                    print(f"❌ Ошибка Telegram: {result.get('description', 'Неизвестная ошибка')}")
                    return False
                
        except urllib.error.URLError as e:
            print(f"❌ Ошибка сети: {e}")
            return False
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return False
    
    def send_recommendation(self, file_path: str) -> bool:
        """Отправляет рекомендацию из файла"""
        try:
            # Читаем файл рекомендации
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Форматируем сообщение
            message_text = data.get('text', 'Нет текста рекомендации')
            
            # Добавляем слоган
            message_text += "\n\n🚀 **TrueLiveBet система всегда на вашей стороне!** ⚽📱"
            
            print("=" * 60)
            print("📤 ОТПРАВКА РЕКОМЕНДАЦИИ В TELEGRAM:")
            print(f"💬 Чат: {self.chat_id}")
            print(f"📁 Файл: {file_path}")
            print("=" * 60)
            
            # Отправляем в Telegram
            success = self.send_message(message_text)
            
            if success:
                print("✅ Рекомендация успешно отправлена в Telegram!")
            else:
                print("❌ Ошибка отправки рекомендации")
            
            return success
            
        except Exception as e:
            print(f"❌ Ошибка обработки файла {file_path}: {e}")
            return False
    
    def send_analysis(self, file_path: str) -> bool:
        """Отправляет анализ из файла"""
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
            
            message_text += f"\n🎯 Источник: {data.get('source', 'Betboom')}\n\n🚀 **TrueLiveBet система всегда на вашей стороне!** ⚽📱"
            
            print("=" * 60)
            print("📤 ОТПРАВКА АНАЛИЗА В TELEGRAM:")
            print(f"💬 Чат: {self.chat_id}")
            print(f"📁 Файл: {file_path}")
            print("=" * 60)
            
            # Отправляем в Telegram
            success = self.send_message(message_text)
            
            if success:
                print("✅ Анализ успешно отправлен в Telegram!")
            else:
                print("❌ Ошибка отправки анализа")
            
            return success
            
        except Exception as e:
            print(f"❌ Ошибка обработки файла {file_path}: {e}")
            return False
    
    def send_text_analysis(self, file_path: str) -> bool:
        """Отправляет текстовый анализ из файла"""
        try:
            # Читаем файл текстового анализа
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Получаем текст для отправки
            message_text = data.get('text', 'Нет текста для отправки')
            
            # Добавляем слоган
            message_text += "\n\n🚀 **TrueLiveBet система всегда на вашей стороне!** ⚽📱"
            
            print("=" * 60)
            print("📤 ОТПРАВКА ТЕКСТОВОГО АНАЛИЗА В TELEGRAM:")
            print(f"💬 Чат: {self.chat_id}")
            print(f"📁 Файл: {file_path}")
            print("=" * 60)
            
            # Отправляем в Telegram
            success = self.send_message(message_text)
            
            if success:
                print("✅ Текстовый анализ успешно отправлен в Telegram!")
            else:
                print("❌ Ошибка отправки текстового анализа")
            
            return success
            
        except Exception as e:
            print(f"❌ Ошибка обработки файла {file_path}: {e}")
            return False
    
    def send_all_recommendations(self) -> bool:
        """Отправляет все доступные рекомендации"""
        # Папка с рекомендациями
        recommendations_dir = "recommendations"
        
        if not os.path.exists(recommendations_dir):
            print(f"❌ Папка не найдена: {recommendations_dir}")
            return False
        
        print(f"🔍 Ищем файлы в: {os.path.abspath(recommendations_dir)}")
        
        # Список файлов для отправки
        files_to_send = []
        
        # Ищем файлы рекомендаций
        for filename in os.listdir(recommendations_dir):
            if filename.startswith('recommendation_') and filename.endswith('.json'):
                files_to_send.append(('recommendation', os.path.join(recommendations_dir, filename)))
            elif filename.startswith('live_analysis_') and filename.endswith('.json'):
                if filename.endswith('_text.json'):
                    files_to_send.append(('text_analysis', os.path.join(recommendations_dir, filename)))
                else:
                    files_to_send.append(('analysis', os.path.join(recommendations_dir, filename)))
        
        if not files_to_send:
            print("❌ Файлы для отправки не найдены")
            return False
        
        print(f"📁 Найдено файлов: {len(files_to_send)}")
        
        # Отправляем каждый файл
        success_count = 0
        total_count = len(files_to_send)
        
        for file_type, file_path in files_to_send:
            print(f"\n📤 Обрабатываю: {file_path}")
            
            if file_type == 'recommendation':
                success = self.send_recommendation(file_path)
            elif file_type == 'text_analysis':
                success = self.send_text_analysis(file_path)
            else:
                success = self.send_analysis(file_path)
            
            if success:
                success_count += 1
            
            # Небольшая задержка между сообщениями
            import time
            time.sleep(2)
        
        print(f"\n🎉 Отправлено: {success_count}/{total_count} файлов")
        return success_count > 0

def main():
    """Главная функция"""
    # Токен из конфига
    token = "7824400107:AAGZqPdS0E0N3HsYpD8TW9m8c-bapFd-RHk"
    
    print("🚀 TrueLiveBet - ИСПРАВЛЕННЫЙ отправитель в Telegram")
    print("=" * 60)
    print(f"🔑 Токен: {token[:10]}...{token[-10:]}")
    print(f"💬 Чат: @truelivebet")
    print("=" * 60)
    
    # Создаем отправитель
    sender = FixedTelegramSender(token)
    
    # Отправляем все рекомендации
    success = sender.send_all_recommendations()
    
    if success:
        print("\n🎉 Все сообщения отправлены в Telegram!")
        print("📱 Проверьте канал @truelivebet")
    else:
        print("\n❌ Ошибка отправки сообщений")
        print("🔍 Проверьте токен и права бота")

if __name__ == "__main__":
    # Запускаем
    main()
