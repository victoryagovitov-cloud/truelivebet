#!/usr/bin/env python3
"""
TrueLiveBet - Умный отправитель в Telegram
Отправляет только свежие данные после анализа
"""

import json
import os
import time
from datetime import datetime
import urllib.request
import urllib.parse

class SmartTelegramSender:
    """Умный отправитель в Telegram - только свежие данные"""
    
    def __init__(self, token: str, chat_id: str = "@truelivebet"):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.last_sent_files = set()  # Отслеживаем уже отправленные файлы
        
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
    
    def get_fresh_analysis_file(self):
        """Находит самый свежий файл анализа"""
        recommendations_dir = "recommendations"
        
        if not os.path.exists(recommendations_dir):
            return None
        
        # Ищем файлы анализа
        analysis_files = []
        for filename in os.listdir(recommendations_dir):
            if filename.startswith('live_analysis_') and filename.endswith('.json') and not filename.endswith('_text.json'):
                file_path = os.path.join(recommendations_dir, filename)
                # Получаем время последнего изменения
                mtime = os.path.getmtime(file_path)
                analysis_files.append((file_path, mtime, filename))
        
        if not analysis_files:
            return None
        
        # Сортируем по времени изменения (самый свежий первый)
        analysis_files.sort(key=lambda x: x[1], reverse=True)
        
        return analysis_files[0][0]  # Возвращаем путь к самому свежему файлу
    
    def format_analysis_message(self, data):
        """Форматирует сообщение анализа"""
        total_matches = data.get('total_matches', 0)
        sports = data.get('sports_analyzed', [])
        best_bets = data.get('best_bets', [])
        
        message_text = f"""
📊 **TrueLiveBet - Новая рекомендация**

⏰ Время: {datetime.now().strftime('%H:%M:%S')} (МСК)
📈 Всего матчей: {total_matches}
⚽ Виды спорта: {', '.join(sports)}

🏆 **Лучшие ставки:**
"""
        
        for i, bet in enumerate(best_bets, 1):
            description = bet.get('description', 'Нет описания')
            confidence = bet.get('confidence', 0)
            category = bet.get('category', '👍')
            message_text += f"{i}. {category} {description} (уверенность: {confidence}%)\n"
        

        
        return message_text
    
    def send_fresh_analysis(self):
        """Отправляет только свежий анализ"""
        print("🔍 Ищем свежий файл анализа...")
        
        fresh_file = self.get_fresh_analysis_file()
        if not fresh_file:
            print("❌ Файлы анализа не найдены")
            return False
        
        print(f"📁 Найден свежий файл: {os.path.basename(fresh_file)}")
        
        try:
            with open(fresh_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Форматируем сообщение
            message_text = self.format_analysis_message(data)
            
            print("📤 Отправляю свежий анализ в Telegram...")
            print("=" * 60)
            
            # Отправляем в Telegram
            success = self.send_message(message_text)
            
            if success:
                print("✅ Свежий анализ успешно отправлен в Telegram!")
                # Запоминаем отправленный файл
                self.last_sent_files.add(os.path.basename(fresh_file))
            else:
                print("❌ Ошибка отправки анализа")
            
            return success
            
        except Exception as e:
            print(f"❌ Ошибка обработки файла {fresh_file}: {e}")
            return False
    
    def send_single_recommendation(self):
        """Отправляет одну рекомендацию (если есть)"""
        recommendations_dir = "recommendations"
        
        if not os.path.exists(recommendations_dir):
            return False
        
        # Ищем файл рекомендации
        for filename in os.listdir(recommendations_dir):
            if filename.startswith('recommendation_') and filename.endswith('.json'):
                file_path = os.path.join(recommendations_dir, filename)
                
                # Проверяем, не отправляли ли мы его уже
                if filename in self.last_sent_files:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    message_text = data.get('text', 'Нет текста рекомендации')
                    message_text += "\n\n🚀 **TrueLiveBet система всегда на вашей стороне!** ⚽📱"
                    
                    print(f"📤 Отправляю рекомендацию: {filename}")
                    
                    success = self.send_message(message_text)
                    
                    if success:
                        print("✅ Рекомендация отправлена!")
                        self.last_sent_files.add(filename)
                        return True
                    
                except Exception as e:
                    print(f"❌ Ошибка обработки рекомендации {filename}: {e}")
        
        return False

def main():
    """Главная функция"""
    token = "7824400107:AAGZqPdS0E0N3HsYpD8TW9m8c-bapFd-RHk"
    
    print("🚀 TrueLiveBet - УМНЫЙ отправитель в Telegram")
    print("=" * 60)
    print(f"🔑 Токен: {token[:10]}...{token[-10:]}")
    print(f"💬 Чат: @truelivebet")
    print("📊 Отправка: ТОЛЬКО свежие данные")
    print("=" * 60)
    
    # Создаем умный отправитель
    sender = SmartTelegramSender(token)
    
    # Отправляем только свежий анализ
    success = sender.send_fresh_analysis()
    
    if success:
        print("\n🎉 Свежий анализ отправлен в Telegram!")
        print("📱 Проверьте канал @truelivebet")
    else:
        print("\n❌ Ошибка отправки анализа")
        print("🔍 Проверьте наличие файлов анализа")

if __name__ == "__main__":
    main()
