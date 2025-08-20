#!/usr/bin/env python3
"""
TrueLiveBet - Детальный отправитель в Telegram
Отправляет полный анализ с подробностями по каждой ставке
"""

import json
import os
import time
from datetime import datetime
import urllib.request
import urllib.parse

class DetailedTelegramSender:
    """Детальный отправитель в Telegram - полный анализ"""
    
    def __init__(self, token: str, chat_id: str = "@truelivebet"):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}"
        
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
    
    def format_detailed_message(self, data):
        """Форматирует детальное сообщение анализа"""
        total_matches = data.get('total_matches', 0)
        sports = data.get('sports_analyzed', [])
        best_bets = data.get('best_bets', [])
        
        message_text = f"""
📊 **TrueLiveBet - Детальный анализ**

⏰ Время: {datetime.now().strftime('%H:%M:%S')} (МСК)
📈 Всего матчей: {total_matches}
⚽ Виды спорта: {', '.join(sports)}

🏆 **Детальный анализ ставок:**
"""
        
        for i, bet in enumerate(best_bets, 1):
            description = bet.get('description', 'Нет описания')
            confidence = bet.get('confidence', 0)
            category = bet.get('category', '👍')
            reasoning = bet.get('reasoning', 'Нет обоснования')
            recommendation = bet.get('recommendation', 'Нет рекомендации')
            status = bet.get('status', 'UNKNOWN')
            
            message_text += f"""
**{i}. {category} {description}**
📊 Уверенность: {confidence}%
🎯 Статус: {status}
💡 Обоснование: {reasoning}
✅ Рекомендация: {recommendation}
---
"""
        
        # Добавляем анализ рисков
        risk_assessment = data.get('risk_assessment', {})
        overall_risk = risk_assessment.get('overall_risk', 'неизвестен')
        
        message_text += f"""
⚠️ **Анализ рисков:**
Общий риск: {overall_risk.upper()}

🏆 **TrueLiveBet - честный анализ!**
        """
        
        return message_text
    
    def send_detailed_analysis(self):
        """Отправляет детальный анализ"""
        print("🔍 Ищем файл для детального анализа...")
        
        # Ищем самый свежий файл
        recommendations_dir = "recommendations"
        if not os.path.exists(recommendations_dir):
            print("❌ Папка recommendations не найдена")
            return False
        
        analysis_files = []
        for filename in os.listdir(recommendations_dir):
            if filename.startswith('live_analysis_') and filename.endswith('.json') and not filename.endswith('_text.json'):
                file_path = os.path.join(recommendations_dir, filename)
                mtime = os.path.getmtime(file_path)
                analysis_files.append((file_path, mtime, filename))
        
        if not analysis_files:
            print("❌ Файлы анализа не найдены")
            return False
        
        # Сортируем по времени изменения (самый свежий первый)
        analysis_files.sort(key=lambda x: x[1], reverse=True)
        fresh_file = analysis_files[0][0]
        
        print(f"📁 Найден файл: {os.path.basename(fresh_file)}")
        
        try:
            with open(fresh_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Форматируем детальное сообщение
            message_text = self.format_detailed_message(data)
            
            print("📤 Отправляю детальный анализ в Telegram...")
            print("=" * 60)
            
            # Отправляем в Telegram
            success = self.send_message(message_text)
            
            if success:
                print("✅ Детальный анализ успешно отправлен в Telegram!")
                return True
            else:
                print("❌ Не удалось отправить детальный анализ")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка чтения файла: {e}")
            return False

def main():
    print("🚀 TrueLiveBet - ДЕТАЛЬНЫЙ отправитель в Telegram")
    print("=" * 60)
    
    # Токен бота
    TOKEN = "7824400107:AAGZqPdS0E0N3HsYpD8TW9m8c-bapFd-RHk"
    
    print(f"🔑 Токен: {TOKEN[:10]}...{TOKEN[-10:]}")
    print(f"💬 Чат: @truelivebet")
    print(f"📊 Отправка: ДЕТАЛЬНЫЙ анализ со всеми подробностями")
    print("=" * 60)
    
    sender = DetailedTelegramSender(TOKEN)
    success = sender.send_detailed_analysis()
    
    if success:
        print("\n🎉 Детальный анализ отправлен в Telegram!")
        print("📱 Проверьте канал @truelivebet")
    else:
        print("\n❌ Не удалось отправить детальный анализ")

if __name__ == "__main__":
    main()
