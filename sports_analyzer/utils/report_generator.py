"""
Генератор отчетов для Telegram
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any
import requests
import logging

from config.settings import OUTPUT_TEMPLATES, REPORT_HEADER, REPORT_FOOTER, SPORT_SEPARATORS

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Генератор отчетов для отправки в Telegram"""
    
    def __init__(self):
        # Загружаем конфигурацию Telegram из существующего файла
        try:
            import sys
            import os
            sys.path.append('/workspace')
            from telegram_config import TELEGRAM_CONFIG
            self.telegram_config = TELEGRAM_CONFIG
        except ImportError:
            logger.warning("Не удалось загрузить telegram_config, используем заглушки")
            self.telegram_config = {
                "bot_token": "YOUR_BOT_TOKEN_HERE",
                "chat_id": "@truelivebet",
                "test_mode": True
            }
    
    def format_match_recommendation(self, sport: str, match_data: Dict[str, Any]) -> str:
        """Форматирует рекомендацию по матчу согласно шаблону"""
        template_key = sport
        
        # Для гандбола выбираем шаблон в зависимости от типа ставки
        if sport == 'handball':
            if match_data.get('bet_type') == 'total':
                template_key = 'handball_total'
            else:
                template_key = 'handball_victory'
        
        template = OUTPUT_TEMPLATES.get(template_key, "")
        
        try:
            return template.format(**match_data)
        except KeyError as e:
            logger.error(f"Ошибка форматирования шаблона {template_key}: {e}")
            return f"Ошибка форматирования данных матча: {match_data}"
    
    def generate_telegram_report(self, analysis_results: Dict[str, List[Dict[str, Any]]]) -> str:
        """Генерирует финальный отчет для Telegram"""
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        date_str = now.strftime("%d.%m.%Y")
        
        # Заголовок отчета
        report_lines = [REPORT_HEADER.format(time=time_str, date=date_str)]
        report_lines.append("")
        
        # Счетчик для сквозной нумерации
        recommendation_counter = 1
        
        # Обработка каждого вида спорта
        sport_order = ['football', 'tennis', 'table_tennis', 'handball']
        
        for sport in sport_order:
            recommendations = analysis_results.get(sport, [])
            
            if recommendations:
                # Добавляем разделитель для вида спорта
                report_lines.append(SPORT_SEPARATORS[sport])
                report_lines.append("")
                
                # Добавляем рекомендации
                for recommendation in recommendations:
                    formatted_rec = self.format_match_recommendation(sport, recommendation)
                    numbered_rec = f"{recommendation_counter}. {formatted_rec}"
                    report_lines.append(numbered_rec)
                    report_lines.append("")
                    recommendation_counter += 1
        
        # Если нет рекомендаций
        if recommendation_counter == 1:
            report_lines.append("<b>📭 В данный момент подходящих матчей не найдено</b>")
            report_lines.append("")
            report_lines.append("<i>Следующий анализ через 50 минут</i>")
            report_lines.append("")
        
        # Подвал отчета
        report_lines.append(REPORT_FOOTER)
        
        return "\n".join(report_lines)
    
    async def send_to_telegram(self, message: str) -> bool:
        """Отправляет сообщение в Telegram"""
        if self.telegram_config.get("test_mode", True):
            logger.info("ТЕСТОВЫЙ РЕЖИМ - сообщение не отправлено в Telegram")
            logger.info(f"Содержимое сообщения:\n{message}")
            return True
        
        try:
            bot_token = self.telegram_config.get("bot_token")
            chat_id = self.telegram_config.get("chat_id")
            
            if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
                logger.error("Токен Telegram бота не настроен")
                return False
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Сообщение успешно отправлено в Telegram")
                return True
            else:
                logger.error(f"Ошибка отправки в Telegram: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Исключение при отправке в Telegram: {e}")
            return False
    
    def save_report_to_file(self, report: str, filename: str = None) -> str:
        """Сохраняет отчет в файл"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/workspace/recommendations/live_report_{timestamp}.md"
        
        try:
            # Создаем директорию если не существует
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"Отчет сохранен в файл: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Ошибка сохранения отчета: {e}")
            return ""