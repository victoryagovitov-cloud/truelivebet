#!/usr/bin/env python3
"""
TrueLiveBet - Главный модуль автоматизации
Автор: Виктор
"""

import asyncio
import os
import time
from datetime import datetime
from typing import List, Dict
from loguru import logger
from betboom_scraper import BetBoomScraper
from ai_analyzer import AIAnalyzer
from telegram_bot import TrueLiveBetBot
from channel_publisher import ChannelPublisher

class TrueLiveBetAutomation:
    """Главный класс автоматизации TrueLiveBet"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.scraper = None
        self.analyzer = None
        self.bot = None
        self.is_running = False
        
        # Настройка логирования
        self._setup_logging()
        
        # Статистика работы
        self.stats = {
            'start_time': datetime.now(),
            'matches_analyzed': 0,
            'analyses_sent': 0,
            'errors': 0
        }
    
    def _setup_logging(self):
        """Настройка логирования"""
        # Создаем папку для логов
        os.makedirs("logs", exist_ok=True)
        
        # Настраиваем логирование
        logger.add(
            "logs/automation.log",
            rotation="1 day",
            retention="7 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )
        
        logger.info("Логирование настроено")
    
    async def initialize(self):
        """Инициализация всех компонентов"""
        try:
            logger.info("Инициализация TrueLiveBet автоматизации...")
            
            # Инициализируем скрапер
            self.scraper = BetBoomScraper()
            logger.info("Скрапер BetBoom инициализирован")
            
            # Инициализируем AI анализатор
            self.analyzer = AIAnalyzer(
                openai_api_key=self.config.get('openai_api_key'),
                anthropic_api_key=self.config.get('anthropic_api_key')
            )
            logger.info("AI анализатор инициализирован")
            
                    # Инициализируем Telegram бота
        if self.config.get('telegram_token'):
            self.bot = TrueLiveBetBot(self.config['telegram_token'])
            logger.info("Telegram бот инициализирован")
            
            # Инициализируем издатель канала
            if self.config.get('telegram_channel_id'):
                self.channel_publisher = ChannelPublisher(self.bot, self.config['telegram_channel_id'])
                logger.info(f"Издатель канала инициализирован: {self.config['telegram_channel_id']}")
            
            logger.info("Все компоненты инициализированы успешно!")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
            raise
    
    async def start_automation(self):
        """Запуск автоматизации"""
        try:
            self.is_running = True
            logger.info("Запуск автоматизации TrueLiveBet...")
            
            # Запускаем Telegram бота в фоне
            if self.bot:
                bot_task = asyncio.create_task(self.bot.start_bot())
                logger.info("Telegram бот запущен в фоне")
            
            # Основной цикл автоматизации
            while self.is_running:
                try:
                    await self._automation_cycle()
                    
                    # Ждем между циклами
                    await asyncio.sleep(self.config.get('cycle_interval', 300))  # 5 минут по умолчанию
                    
                except Exception as e:
                    logger.error(f"Ошибка в цикле автоматизации: {e}")
                    self.stats['errors'] += 1
                    await asyncio.sleep(60)  # Ждем минуту при ошибке
            
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки")
        except Exception as e:
            logger.error(f"Критическая ошибка автоматизации: {e}")
        finally:
            await self.stop_automation()
    
    async def _automation_cycle(self):
        """Один цикл автоматизации"""
        try:
            logger.info("Начало цикла автоматизации...")
            
            # 1. Сбор данных с BetBoom
            matches = await self._collect_matches()
            if not matches:
                logger.warning("Не удалось собрать матчи")
                return
            
            logger.info(f"Собрано {len(matches)} матчей")
            
            # 2. Анализ матчей с помощью AI
            analyses = await self._analyze_matches(matches)
            if not analyses:
                logger.warning("Не удалось проанализировать матчи")
                return
            
            logger.info(f"Проанализировано {len(analyses)} матчей")
            
            # 3. Фильтрация по нашим критериям
            filtered_analyses = self._filter_analyses(analyses)
            logger.info(f"Отфильтровано {len(filtered_analyses)} анализов")
            
                    # 4. Отправка результатов в Telegram
        if self.bot and filtered_analyses:
            await self._send_analyses(filtered_analyses)
            
            # 5. Публикация в канал
            if hasattr(self, 'channel_publisher') and filtered_analyses:
                await self._publish_to_channel(filtered_analyses)
            
            # Обновляем статистику
            self.stats['matches_analyzed'] += len(matches)
            self.stats['analyses_sent'] += len(filtered_analyses)
            
            logger.info(f"Цикл автоматизации завершен. Статистика: {self.stats}")
            
        except Exception as e:
            logger.error(f"Ошибка в цикле автоматизации: {e}")
            raise
    
    async def _collect_matches(self) -> List[Dict]:
        """Сбор матчей с BetBoom"""
        try:
            if not self.scraper:
                logger.error("Скрапер не инициализирован")
                return []
            
            # Запускаем браузер
            await self.scraper.start_browser()
            
            # Переходим на live страницу
            await self.scraper.navigate_to_live()
            
            # Получаем live матчи
            matches = await self.scraper.get_live_matches()
            
            # Закрываем браузер
            await self.scraper.close()
            
            # Конвертируем в словари для анализа
            match_dicts = []
            for match in matches:
                match_dict = {
                    'sport': match.sport,
                    'league': match.league,
                    'team1': match.team1,
                    'team2': match.team2,
                    'score': match.score,
                    'time': match.time,
                    'odds': match.odds,
                    'status': match.status,
                    'timestamp': match.timestamp.isoformat()
                }
                match_dicts.append(match_dict)
            
            return match_dicts
            
        except Exception as e:
            logger.error(f"Ошибка сбора матчей: {e}")
            return []
    
    async def _analyze_matches(self, matches: List[Dict]) -> List:
        """Анализ матчей с помощью AI"""
        try:
            if not self.analyzer:
                logger.error("AI анализатор не инициализирован")
                return []
            
            # Пакетный анализ всех матчей
            analyses = await self.analyzer.batch_analyze(matches)
            
            return analyses
            
        except Exception as e:
            logger.error(f"Ошибка AI анализа: {e}")
            return []
    
    def _filter_analyses(self, analyses: List) -> List:
        """Фильтрация анализов по нашим критериям"""
        try:
            filtered = []
            
            for analysis in analyses:
                # Фильтруем по уверенности (минимум 75%)
                if analysis.confidence >= 75.0:
                    filtered.append(analysis)
                    
                    # Логируем высокоуверенные анализы
                    if analysis.confidence >= 85.0:
                        logger.info(f"Высокоуверенный анализ: {analysis.category} - {analysis.confidence:.1f}%")
            
            return filtered
            
        except Exception as e:
            logger.error(f"Ошибка фильтрации анализов: {e}")
            return analyses
    
    async def _send_analyses(self, analyses: List):
        """Отправка анализов в Telegram"""
        try:
            if not self.bot:
                logger.warning("Telegram бот не инициализирован")
                return
            
            # Отправляем каждый анализ
            for analysis in analyses:
                try:
                    # Получаем список активных чатов (нужно реализовать)
                    active_chats = self._get_active_chats()
                    
                    for chat_id in active_chats:
                        await self.bot.send_analysis(chat_id, analysis)
                        logger.info(f"Анализ отправлен в чат {chat_id}")
                    
                    # Небольшая задержка между отправками
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Ошибка отправки анализа: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Ошибка отправки анализов: {e}")
    
    async def _publish_to_channel(self, analyses: List):
        """Публикация анализов в Telegram канал"""
        try:
            if not hasattr(self, 'channel_publisher'):
                logger.warning("Издатель канала не инициализирован")
                return
            
            # Публикуем анализы в канал
            results = await self.channel_publisher.publish_batch(analyses)
            logger.info(f"📢 Публикация в канал завершена: {results}")
            
            # Публикуем сводку
            await self.channel_publisher.publish_summary(analyses)
            
        except Exception as e:
            logger.error(f"Ошибка публикации в канал: {e}")
    
    def _get_active_chats(self) -> List[str]:
        """Получение списка активных чатов и каналов"""
        chats = []
        
        # Добавляем основной канал для публикации
        if self.config.get('telegram_channel_id'):
            chats.append(self.config['telegram_channel_id'])
        
        # Добавляем тестовый чат (если указан)
        if self.config.get('test_chat_id'):
            chats.append(self.config['test_chat_id'])
        
        return chats
    
    async def stop_automation(self):
        """Остановка автоматизации"""
        try:
            logger.info("Остановка автоматизации TrueLiveBet...")
            
            self.is_running = False
            
            # Останавливаем компоненты
            if self.scraper:
                await self.scraper.close()
            
            if self.bot:
                await self.bot.stop_bot()
            
            # Выводим финальную статистику
            uptime = datetime.now() - self.stats['start_time']
            logger.info(f"""
            🏁 АВТОМАТИЗАЦИЯ ОСТАНОВЛЕНА
            
            📊 Финальная статистика:
            ⏱ Время работы: {uptime}
            📈 Матчей проанализировано: {self.stats['matches_analyzed']}
            📤 Анализов отправлено: {self.stats['analyses_sent']}
            ❌ Ошибок: {self.stats['errors']}
            """)
            
        except Exception as e:
            logger.error(f"Ошибка остановки автоматизации: {e}")
    
    def get_status(self) -> Dict:
        """Получение статуса системы"""
        uptime = datetime.now() - self.stats['start_time']
        
        return {
            'status': 'running' if self.is_running else 'stopped',
            'uptime': str(uptime),
            'stats': self.stats.copy(),
            'components': {
                'scraper': self.scraper is not None,
                'analyzer': self.analyzer is not None,
                'bot': self.bot is not None
            }
        }

# Импортируем конфигурацию
from config import get_config, validate_config

async def main():
    """Главная функция"""
    try:
        # Загружаем конфигурацию
        config = get_config()
        
        # Проверяем корректность конфигурации
        if not validate_config():
            logger.error("Ошибка в конфигурации")
            return
        
        # Создаем и запускаем автоматизацию
        automation = TrueLiveBetAutomation(config)
        
        # Инициализируем
        await automation.initialize()
        
        # Запускаем
        await automation.start_automation()
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    # Настройка логирования
    logger.add("logs/main.log", rotation="1 day", retention="7 days")
    
    # Запуск
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Программа остановлена пользователем")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
