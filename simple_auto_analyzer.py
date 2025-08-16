#!/usr/bin/env python3
"""
TrueLiveBet - Простой автоматический анализатор матчей
Работает только с встроенными модулями Python
"""

import json
import time
import logging
import urllib.request
import urllib.parse
from datetime import datetime
import os
import re

# Конфигурация
TELEGRAM_CONFIG = {
    'bot_token': '7824400107:AAGZqPdS0E0N3HsYpD8TW9m8c-bapFd-RHk',
    'chat_id': '678873745',
    'bot_username': 'TrueLiveBetBot'
}

PARSING_CONFIG = {
    'interval_minutes': 30,
    'betboom_url': 'https://betboom.ru',
    'max_matches_per_check': 10,
    'timeout_seconds': 30
}

ANALYSIS_CRITERIA = {
    'football': {
        'min_goal_difference': 2,
        'min_time_elapsed': 60,
        'confidence_threshold': 75
    },
    'basketball': {
        'min_point_difference': 15,
        'confidence_threshold': 70
    }
}

def send_telegram_message(message):
    """Отправляет сообщение в Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_CONFIG['bot_token']}/sendMessage"
        
        data = {
            'chat_id': TELEGRAM_CONFIG['chat_id'],
            'text': message,
            'parse_mode': 'HTML'
        }
        
        # Кодируем данные
        data_encoded = urllib.parse.urlencode(data).encode('utf-8')
        
        # Создаем запрос
        req = urllib.request.Request(url, data=data_encoded)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        # Отправляем запрос
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            result_json = json.loads(result)
            
            if result_json.get('ok'):
                print(f"✅ Сообщение отправлено: {result_json['result']['message_id']}")
                return True
            else:
                print(f"❌ Ошибка API: {result_json}")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False

def analyze_football_match(team1, team2, score, time_elapsed):
    """Анализирует футбольный матч"""
    try:
        # Парсим счет
        home_score, away_score = map(int, score.split(':'))
        goal_difference = abs(home_score - away_score)
        
        # Парсим время
        time_minutes = int(re.sub(r'[^\d]', '', time_elapsed) or 0)
        
        confidence = 0
        recommendation = ""
        reasoning = []
        
        # Проверяем критерии
        if (goal_difference >= ANALYSIS_CRITERIA['football']['min_goal_difference'] and
            time_minutes >= ANALYSIS_CRITERIA['football']['min_time_elapsed']):
            
            favorite = team1 if home_score > away_score else team2
            confidence = 80
            recommendation = f"Победа {favorite}"
            reasoning.append(f"Фаворит ведет на {goal_difference} гола")
            reasoning.append(f"Время матча: {time_minutes} минут")
        
        return {
            'confidence': confidence,
            'recommendation': recommendation,
            'reasoning': reasoning,
            'should_notify': confidence >= ANALYSIS_CRITERIA['football']['confidence_threshold']
        }
        
    except Exception as e:
        print(f"Ошибка анализа футбола: {e}")
        return {'confidence': 0, 'recommendation': '', 'reasoning': [], 'should_notify': False}

def analyze_basketball_match(team1, team2, score, quarter):
    """Анализирует баскетбольный матч"""
    try:
        # Парсим счет
        home_score, away_score = map(int, score.split(':'))
        point_difference = abs(home_score - away_score)
        
        confidence = 0
        recommendation = ""
        reasoning = []
        
        # Проверяем критерии
        if point_difference >= ANALYSIS_CRITERIA['basketball']['min_point_difference']:
            favorite = team1 if home_score > away_score else team2
            confidence = 70
            recommendation = f"Победа {favorite}"
            reasoning.append(f"Отрыв {point_difference} очков")
            reasoning.append(f"Квартал: {quarter}")
        
        return {
            'confidence': confidence,
            'recommendation': recommendation,
            'reasoning': reasoning,
            'should_notify': confidence >= ANALYSIS_CRITERIA['basketball']['confidence_threshold']
        }
        
    except Exception as e:
        print(f"Ошибка анализа баскетбола: {e}")
        return {'confidence': 0, 'recommendation': '', 'reasoning': [], 'should_notify': False}

def simulate_live_matches():
    """Симулирует live матчи для демонстрации"""
    print("🎯 Симулирую live матчи для демонстрации...")
    
    matches = [
        {
            'sport': 'football',
            'team1': 'Барселона',
            'team2': 'Реал Мадрид',
            'score': '2:0',
            'time': '65\'',
            'quarter': None
        },
        {
            'sport': 'basketball',
            'team1': 'ЦСКА',
            'team2': 'Спартак',
            'score': '85:65',
            'time': None,
            'quarter': '3'
        },
        {
            'sport': 'football',
            'team1': 'Манчестер Юнайтед',
            'team2': 'Ливерпуль',
            'score': '1:0',
            'time': '45\'',
            'quarter': None
        }
    ]
    
    return matches

def format_telegram_message(match, analysis_result):
    """Форматирует сообщение для Telegram"""
    sport_emoji = {'football': '⚽', 'basketball': '🏀'}.get(match['sport'], '🏆')
    
    message = f"""
🎯 <b>TrueLiveBet - Найден подходящий матч!</b>

{sport_emoji} <b>Вид спорта:</b> {match['sport'].title()}
🏆 <b>Матч:</b> {match['team1']} vs {match['team2']}
📊 <b>Счет:</b> {match['score']}
⏰ <b>Время:</b> {match['time'] or f"Квартал {match['quarter']}"}
📈 <b>Уверенность:</b> {analysis_result['confidence']}%

💡 <b>Рекомендация:</b> {analysis_result['recommendation'] or 'Анализ в процессе'}

🔍 <b>Обоснование:</b>
"""
    
    for reason in analysis_result['reasoning']:
        message += f"• {reason}\n"
    
    if not analysis_result['reasoning']:
        message += "• Недостаточно данных для рекомендации\n"
    
    message += f"\n⏰ <i>Анализ: {datetime.now().strftime('%H:%M:%S')}</i>"
    
    return message

def check_matches():
    """Проверяет матчи и анализирует их"""
    print(f"🔍 Проверка матчей в {datetime.now().strftime('%H:%M:%S')}...")
    
    # Получаем матчи (в демо-режиме симулируем)
    matches = simulate_live_matches()
    
    if not matches:
        print("📭 Матчи не найдены")
        return
    
    print(f"📊 Найдено {len(matches)} матчей")
    
    # Анализируем каждый матч
    for match in matches:
        try:
            print(f"\n🔍 Анализирую: {match['team1']} vs {match['team2']}")
            
            if match['sport'] == 'football':
                analysis_result = analyze_football_match(
                    match['team1'], match['team2'], 
                    match['score'], match['time']
                )
            elif match['sport'] == 'basketball':
                analysis_result = analyze_basketball_match(
                    match['team1'], match['team2'], 
                    match['score'], match['quarter']
                )
            else:
                continue
            
            print(f"📈 Уверенность: {analysis_result['confidence']}%")
            print(f"💡 Рекомендация: {analysis_result['recommendation']}")
            
            # Отправляем уведомление если нужно
            if analysis_result['should_notify']:
                print("🔔 Отправляю уведомление...")
                
                message = format_telegram_message(match, analysis_result)
                success = send_telegram_message(message)
                
                if success:
                    print("✅ Уведомление отправлено!")
                else:
                    print("❌ Ошибка отправки уведомления")
            else:
                print("⏰ Уведомление не требуется")
                
        except Exception as e:
            print(f"❌ Ошибка анализа матча: {e}")
            continue
    
    print(f"✅ Проверка завершена в {datetime.now().strftime('%H:%M:%S')}")

def main():
    """Основная функция"""
    print("🎯 TrueLiveBet - Простой автоматический анализатор")
    print("=" * 50)
    print(f"⏰ Периодичность проверки: {PARSING_CONFIG['interval_minutes']} минут")
    print(f"📱 Telegram Chat ID: {TELEGRAM_CONFIG['chat_id']}")
    print("=" * 50)
    
    # Отправляем приветственное сообщение
    welcome_message = f"""
🎯 <b>TrueLiveBet Bot запущен!</b>

⏰ Время запуска: {datetime.now().strftime('%H:%M:%S')}
🔍 Периодичность проверки: {PARSING_CONFIG['interval_minutes']} минут
📊 Готов к анализу матчей

🎉 <b>Бот работает в демо-режиме!</b>
"""
    
    print("📤 Отправляю приветственное сообщение...")
    if send_telegram_message(welcome_message):
        print("✅ Приветственное сообщение отправлено!")
    else:
        print("❌ Ошибка отправки приветственного сообщения")
    
    try:
        while True:
            # Проверяем матчи
            check_matches()
            
            # Ждем до следующей проверки
            wait_time = PARSING_CONFIG['interval_minutes'] * 60
            print(f"\n⏳ Следующая проверка через {PARSING_CONFIG['interval_minutes']} минут")
            print(f"⏰ Время: {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 50)
            
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
        
        # Отправляем сообщение об остановке
        stop_message = f"""
🛑 <b>TrueLiveBet Bot остановлен</b>

⏰ Время остановки: {datetime.now().strftime('%H:%M:%S')}
📊 Бот будет возобновлен при следующем запуске
"""
        send_telegram_message(stop_message)
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        
        # Отправляем сообщение об ошибке
        error_message = f"""
❌ <b>TrueLiveBet Bot - Критическая ошибка</b>

⏰ Время: {datetime.now().strftime('%H:%M:%S')}
🚨 Ошибка: {str(e)}

🔧 Требуется перезапуск бота
"""
        send_telegram_message(error_message)
        raise

if __name__ == "__main__":
    main()