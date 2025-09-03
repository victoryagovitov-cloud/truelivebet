#!/usr/bin/env python3
"""
Главный модуль анализатора спортивных событий TrueLiveBet
Выполняет циклический анализ каждые 50 минут
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
import schedule
import time

from analyzers.football_analyzer import FootballAnalyzer
from analyzers.tennis_analyzer import TennisAnalyzer
from analyzers.table_tennis_analyzer import TableTennisAnalyzer
from analyzers.handball_analyzer import HandballAnalyzer
from utils.fuzzy_matcher import FuzzyMatcher
from utils.report_generator import ReportGenerator
from utils.advanced_claude_analyzer import AdvancedClaudeAnalyzer
from config.settings import ANALYSIS_CONFIG

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sports_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SportsAnalyzer:
    """Основной класс анализатора спортивных событий"""
    
    def __init__(self):
        self.fuzzy_matcher = FuzzyMatcher()
        self.report_generator = ReportGenerator()
        self.claude_analyzer = AdvancedClaudeAnalyzer()
        
        # Инициализация анализаторов для каждого вида спорта
        self.analyzers = {
            'football': FootballAnalyzer(self.fuzzy_matcher),
            'tennis': TennisAnalyzer(self.fuzzy_matcher),
            'table_tennis': TableTennisAnalyzer(self.fuzzy_matcher),
            'handball': HandballAnalyzer(self.fuzzy_matcher)
        }
        
        logger.info("SportsAnalyzer инициализирован с Claude AI интеграцией")
    
    async def run_analysis_cycle(self) -> Dict[str, List[Dict[str, Any]]]:
        """Выполняет полный цикл анализа всех видов спорта"""
        logger.info("Начало цикла анализа")
        
        results = {}
        
        try:
            # Параллельный анализ всех видов спорта
            tasks = []
            for sport_name, analyzer in self.analyzers.items():
                task = asyncio.create_task(
                    analyzer.analyze(),
                    name=f"analyze_{sport_name}"
                )
                tasks.append((sport_name, task))
            
            # Ожидание завершения всех задач
            for sport_name, task in tasks:
                try:
                    sport_results = await task
                    results[sport_name] = sport_results
                    logger.info(f"Анализ {sport_name} завершен: найдено {len(sport_results)} рекомендаций")
                except Exception as e:
                    logger.error(f"Ошибка анализа {sport_name}: {e}")
                    results[sport_name] = []
            
            # Генерация и отправка отчета
            if any(results.values()):
                report = self.report_generator.generate_telegram_report(results)
                await self.report_generator.send_to_telegram(report)
                logger.info("Отчет отправлен в Telegram")
            else:
                logger.info("Подходящих матчей не найдено")
                
        except Exception as e:
            logger.error(f"Ошибка в цикле анализа: {e}")
        
        logger.info("Цикл анализа завершен")
        return results
    
    def run_scheduled_analysis(self):
        """Запускает анализ по расписанию"""
        logger.info("Запуск запланированного анализа")
        asyncio.run(self.run_analysis_cycle())
    
    def start_scheduler(self):
        """Запускает планировщик с циклом 50 минут"""
        logger.info("Запуск планировщика (цикл 50 минут)")
        
        # Планирование выполнения каждые 50 минут
        schedule.every(50).minutes.do(self.run_scheduled_analysis)
        
        # Первый запуск сразу
        self.run_scheduled_analysis()
        
        # Основной цикл планировщика
        while True:
            schedule.run_pending()
            time.sleep(60)  # Проверка каждую минуту


def main():
    """Главная функция запуска"""
    analyzer = SportsAnalyzer()
    
    try:
        analyzer.start_scheduler()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        logger.info("Анализатор остановлен")


if __name__ == "__main__":
    main()