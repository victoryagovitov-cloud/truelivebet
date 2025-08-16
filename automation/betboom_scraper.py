#!/usr/bin/env python3
"""
TrueLiveBet - Автоматический сбор данных с BetBoom
Автор: Виктор
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, Page
from loguru import logger

@dataclass
class Match:
    """Класс для хранения информации о матче"""
    sport: str
    league: str
    team1: str
    team2: str
    score: str
    time: str
    odds: Dict[str, float]
    status: str
    timestamp: datetime

class BetBoomScraper:
    """Класс для сбора данных с BetBoom"""
    
    def __init__(self):
        self.base_url = "https://betboom.ru"
        self.live_url = f"{self.base_url}/live"
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    async def start_browser(self):
        """Запуск браузера"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # False для отладки, True для продакшена
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                ]
            )
            self.page = await self.browser.new_page()
            
            # Устанавливаем заголовки для обхода защиты
            await self.page.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            logger.info("Браузер запущен успешно")
            
        except Exception as e:
            logger.error(f"Ошибка запуска браузера: {e}")
            raise
    
    async def navigate_to_live(self):
        """Переход на страницу лайв-ставок"""
        try:
            await self.page.goto(self.live_url, wait_until='networkidle')
            logger.info(f"Перешли на {self.live_url}")
            
            # Ждем загрузки контента
            await self.page.wait_for_selector('[data-testid="live-events"]', timeout=10000)
            
        except Exception as e:
            logger.error(f"Ошибка перехода на live страницу: {e}")
            # Пробуем альтернативный селектор
            try:
                await self.page.wait_for_selector('.live-events', timeout=5000)
                logger.info("Нашли альтернативный селектор")
            except:
                logger.warning("Не удалось найти селектор live событий")
    
    async def get_live_matches(self) -> List[Match]:
        """Получение списка лайв-матчей"""
        matches = []
        
        try:
            # Ищем все live матчи
            match_elements = await self.page.query_selector_all('[data-testid="match-item"]')
            
            if not match_elements:
                # Альтернативный поиск
                match_elements = await self.page.query_selector_all('.match-item, .event-item, .live-match')
            
            logger.info(f"Найдено {len(match_elements)} матчей")
            
            for element in match_elements:
                try:
                    match_data = await self.extract_match_data(element)
                    if match_data:
                        matches.append(match_data)
                except Exception as e:
                    logger.warning(f"Ошибка извлечения данных матча: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Ошибка получения live матчей: {e}")
        
        return matches
    
    async def extract_match_data(self, element) -> Optional[Match]:
        """Извлечение данных о матче"""
        try:
            # Извлекаем основную информацию
            sport = await self.get_text(element, '[data-testid="sport"], .sport, .sport-name')
            league = await self.get_text(element, '[data-testid="league"], .league, .tournament')
            team1 = await self.get_text(element, '[data-testid="team1"], .team1, .home-team')
            team2 = await self.get_text(element, '[data-testid="team2"], .team2, .away-team')
            score = await self.get_text(element, '[data-testid="score"], .score, .match-score')
            time = await self.get_text(element, '[data-testid="time"], .time, .match-time')
            status = await self.get_text(element, '[data-testid="status"], .status, .match-status')
            
            # Извлекаем коэффициенты
            odds = await self.extract_odds(element)
            
            if all([sport, team1, team2]):  # Проверяем обязательные поля
                return Match(
                    sport=sport,
                    league=league or "Неизвестная лига",
                    team1=team1,
                    team2=team2,
                    score=score or "0:0",
                    time=time or "0'",
                    odds=odds,
                    status=status or "live",
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            logger.warning(f"Ошибка извлечения данных: {e}")
        
        return None
    
    async def get_text(self, element, selector: str) -> str:
        """Получение текста по селектору"""
        try:
            text_element = await element.query_selector(selector)
            if text_element:
                return await text_element.text_content() or ""
        except:
            pass
        return ""
    
    async def extract_odds(self, element) -> Dict[str, float]:
        """Извлечение коэффициентов"""
        odds = {}
        try:
            # Ищем коэффициенты для разных исходов
            odd_selectors = [
                '[data-testid="odd-1"], .odd-1, .home-odd',
                '[data-testid="odd-x"], .odd-x, .draw-odd',
                '[data-testid="odd-2"], .odd-2, .away-odd'
            ]
            
            odd_names = ['1', 'X', '2']
            
            for selector, name in zip(odd_selectors, odd_names):
                try:
                    odd_element = await element.query_selector(selector)
                    if odd_element:
                        odd_text = await odd_element.text_content()
                        if odd_text:
                            odds[name] = float(odd_text.strip())
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Ошибка извлечения коэффициентов: {e}")
        
        return odds
    
    async def close(self):
        """Закрытие браузера"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("Браузер закрыт")
        except Exception as e:
            logger.error(f"Ошибка закрытия браузера: {e}")

async def main():
    """Основная функция"""
    scraper = BetBoomScraper()
    
    try:
        await scraper.start_browser()
        await scraper.navigate_to_live()
        
        # Получаем live матчи
        matches = await scraper.get_live_matches()
        
        logger.info(f"Собрано {len(matches)} матчей:")
        for match in matches:
            logger.info(f"{match.sport}: {match.team1} vs {match.team2} - {match.score} ({match.time})")
        
        # Здесь будет логика анализа и отправки в Telegram
        
    except Exception as e:
        logger.error(f"Ошибка в main: {e}")
    finally:
        await scraper.close()

if __name__ == "__main__":
    # Настройка логирования
    logger.add("logs/betboom_scraper.log", rotation="1 day", retention="7 days")
    
    # Запуск
    asyncio.run(main())
