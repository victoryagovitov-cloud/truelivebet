#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт отправки результатов анализа в Telegram
Запускается через GitHub Actions
"""

import os
import json
import requests
from datetime import datetime
import logging
import glob

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_to_telegram(text, bot_token, channel_id):
    """Отправляет сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    data = {
        "chat_id": channel_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            logger.info("✅ Анализ отправлен в Telegram")
            return True
        else:
            logger.error(f"❌ Ошибка отправки: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Ошибка отправки: {e}")
        return False

def format_analysis_message(analysis_data):
    """Форматирует сообщение с анализом"""
    try:
        message = "🎯 **TrueLiveBet - Результаты анализа!**\n\n"
        
        # Время анализа
        timestamp = datetime.now().strftime("%H:%M:%S")
        message += f"⏰ **Время:** {timestamp} (МСК)\n\n"
        
        # Статистика
        if 'total_matches' in analysis_data:
            message += f"📊 **Всего матчей:** {analysis_data['total_matches']}\n"
        
        if 'sports_analyzed' in analysis_data:
            sports = analysis_data['sports_analyzed']
            if isinstance(sports, list):
                message += f"🏆 **Виды спорта:** {', '.join(sports)}\n"
            else:
                message += f"🏆 **Виды спорта:** {sports}\n"
        
        # Лучшие ставки
        if 'best_bets' in analysis_data and analysis_data['best_bets']:
            message += "\n⭐ **Лучшие ставки:**\n"
            for i, bet in enumerate(analysis_data['best_bets'][:5], 1):
                if isinstance(bet, dict):
                    description = bet.get('description', str(bet))
                    confidence = bet.get('confidence', '')
                    
                    message += f"{i}. {description}\n"
                    if confidence:
                        message += f"   Уверенность: {confidence}%\n"
                else:
                    message += f"{i}. {bet}\n"
        
        # Разделитель
        message += "\n" + "─" * 40
        
        return message
        
    except Exception as e:
        logger.error(f"❌ Ошибка форматирования: {e}")
        return "🎯 **TrueLiveBet - Новый анализ получен!**\n\nАнализ обработан и готов к отправке."

def check_new_recommendations():
    """Проверяет новые рекомендации"""
    try:
        recommendations_dir = "recommendations"
        pattern = f"{recommendations_dir}/recommendation_*.json"
        
        new_recommendations = []
        
        for filename in glob.glob(pattern):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Проверяем статус
                if data.get('status') == 'new':
                    new_recommendations.append((filename, data))
                    
            except Exception as e:
                logger.error(f"❌ Ошибка чтения {filename}: {e}")
        
        return new_recommendations
        
    except Exception as e:
        logger.error(f"❌ Ошибка проверки рекомендаций: {e}")
        return []

def format_recommendation_message(recommendation_data):
    """Форматирует сообщение с рекомендацией"""
    try:
        message = "🎯 **TrueLiveBet - Новая рекомендация!**\n\n"
        
        # Добавляем время анализа
        timestamp = recommendation_data.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                moscow_time = dt.strftime("%H:%M:%S")
                message += f"⏰ **Время анализа:** {moscow_time} (МСК)\n\n"
            except:
                message += f"⏰ **Время анализа:** {timestamp}\n\n"
        
        # Добавляем текст рекомендации
        text = recommendation_data.get('text', '')
        if text:
            message += text
        else:
            message += "Новая рекомендация получена"
        
        # Добавляем разделитель
        message += "\n\n" + "─" * 40
        
        return message
        
    except Exception as e:
        logger.error(f"❌ Ошибка форматирования рекомендации: {e}")
        return "🎯 **TrueLiveBet - Новая рекомендация!**\n\nРекомендация получена и готова к отправке."

def main():
    """Основная функция"""
    logger.info("🚀 Запуск отправки анализа в Telegram...")
    
    # Получаем токены
    bot_token = os.environ.get('BOT_TOKEN')
    channel_id = os.environ.get('CHANNEL_ID')
    
    if not bot_token or not channel_id:
        logger.error("❌ Отсутствуют токены Telegram")
        return
    
    logger.info(f"📱 Бот настроен для канала: {channel_id}")
    
    # Проверяем новые рекомендации
    new_recommendations = check_new_recommendations()
    
    if new_recommendations:
        logger.info(f"📊 Найдено {len(new_recommendations)} новых рекомендаций")
        
        # Отправляем каждую рекомендацию
        for filename, data in new_recommendations:
            try:
                logger.info(f"📤 Отправка рекомендации {data.get('id', 'unknown')}")
                
                # Форматируем сообщение
                message = format_recommendation_message(data)
                
                # Отправляем в Telegram
                if send_to_telegram(message, bot_token, channel_id):
                    logger.info(f"✅ Рекомендация {data.get('id', 'unknown')} отправлена")
                    
                    # Обновляем статус
                    data['status'] = 'sent'
                    data['sent_at'] = datetime.now().isoformat()
                    
                    # Сохраняем обновленный файл
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                else:
                    logger.error(f"❌ Не удалось отправить рекомендацию {data.get('id', 'unknown')}")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка обработки рекомендации: {e}")
    
    # Проверяем основной анализ
    try:
        analysis_file = 'recommendations/live_analysis_test.json'
        
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            # Формируем сообщение
            message = format_analysis_message(analysis_data)
            logger.info(f"📝 Сообщение с анализом сформировано, длина: {len(message)} символов")
            
            # Отправляем в Telegram
            if send_to_telegram(message, bot_token, channel_id):
                logger.info("✅ Анализ успешно отправлен в Telegram")
            else:
                logger.error("❌ Не удалось отправить анализ")
        else:
            logger.info("📭 Файл анализа не найден")
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки анализа: {e}")
    
    logger.info("🎯 Отправка завершена")

if __name__ == "__main__":
    main()
