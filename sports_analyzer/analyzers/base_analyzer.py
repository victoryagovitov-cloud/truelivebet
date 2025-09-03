"""
Базовый класс для анализаторов спортивных событий
Интегрирован с Claude AI для интеллектуального анализа
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json

from utils.claude_analyzer import ClaudeAnalyzer
from config.claude_config import CLAUDE_CONFIG

logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC):
    """Базовый класс для всех анализаторов видов спорта"""
    
    def __init__(self, fuzzy_matcher, sport_name: str):
        self.fuzzy_matcher = fuzzy_matcher
        self.sport_name = sport_name
        self.logger = logging.getLogger(f"{__name__}.{sport_name}")
        
        # Инициализация Claude анализатора
        self.claude_analyzer = ClaudeAnalyzer(CLAUDE_CONFIG.get("api_key"))
    
    @abstractmethod
    async def get_betboom_matches(self) -> List[Dict[str, Any]]:
        """Получает матчи с BetBoom (должен быть реализован в наследниках)"""
        pass
    
    @abstractmethod
    async def get_scores24_matches(self) -> List[Dict[str, Any]]:
        """Получает матчи со Scores24 (должен быть реализован в наследниках)"""
        pass
    
    @abstractmethod
    def filter_matches_by_criteria(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Фильтрует матчи по критериям вида спорта"""
        pass
    
    @abstractmethod
    async def analyze_match_statistics(self, betboom_match: Dict[str, Any], 
                                     scores24_match: Dict[str, Any]) -> Dict[str, Any]:
        """Анализирует статистику матча с помощью Claude AI"""
        
        # Выбираем метод анализа в зависимости от вида спорта
        if self.sport_name == 'football':
            return await self.claude_analyzer.analyze_football_match(betboom_match, scores24_match)
        elif self.sport_name == 'tennis':
            return await self.claude_analyzer.analyze_tennis_match(betboom_match, scores24_match)
        elif self.sport_name == 'table_tennis':
            return await self.claude_analyzer.analyze_table_tennis_match(betboom_match, scores24_match)
        elif self.sport_name == 'handball':
            if betboom_match.get('analysis_type') == 'total':
                return await self.claude_analyzer.analyze_handball_total(betboom_match, scores24_match)
            else:
                return await self.claude_analyzer.analyze_handball_victory(betboom_match, scores24_match)
        else:
            return {"confidence": 0, "reasoning": "Неподдерживаемый вид спорта"}
    
    async def analyze(self) -> List[Dict[str, Any]]:
        """Основной метод анализа"""
        self.logger.info(f"Начало анализа {self.sport_name}")
        
        try:
            # Получение данных с обеих платформ параллельно
            betboom_task = asyncio.create_task(self.get_betboom_matches())
            scores24_task = asyncio.create_task(self.get_scores24_matches())
            
            betboom_matches, scores24_matches = await asyncio.gather(
                betboom_task, scores24_task, return_exceptions=True
            )
            
            # Обработка возможных ошибок
            if isinstance(betboom_matches, Exception):
                self.logger.error(f"Ошибка получения данных BetBoom: {betboom_matches}")
                return []
            
            if isinstance(scores24_matches, Exception):
                self.logger.error(f"Ошибка получения данных Scores24: {scores24_matches}")
                return []
            
            # Фильтрация матчей по критериям
            filtered_matches = self.filter_matches_by_criteria(betboom_matches)
            self.logger.info(f"Отфильтровано {len(filtered_matches)} матчей из {len(betboom_matches)}")
            
            recommendations = []
            
            # Анализ каждого отфильтрованного матча
            for betboom_match in filtered_matches:
                try:
                    # Поиск соответствующего матча на Scores24
                    matched_data = self._find_matching_scores24_data(
                        betboom_match, scores24_matches
                    )
                    
                    if not matched_data:
                        self.logger.debug(f"Не найдено соответствие для матча: {betboom_match}")
                        continue
                    
                    # Анализ статистики через Claude AI
                    analysis_result = await self.analyze_match_statistics(
                        betboom_match, matched_data['match']
                    )
                    
                    # Проверка уверенности в прогнозе
                    if analysis_result.get('confidence', 0) >= 80:
                        # Проверка доступности ставки
                        if self._is_bet_available(betboom_match):
                            recommendation = self._format_recommendation(
                                betboom_match, matched_data, analysis_result
                            )
                            recommendations.append(recommendation)
                        else:
                            self.logger.debug(f"Ставка недоступна для матча: {betboom_match}")
                    else:
                        self.logger.debug(f"Низкая уверенность ({analysis_result.get('confidence', 0)}%) для матча: {betboom_match}")
                        
                except Exception as e:
                    self.logger.error(f"Ошибка анализа матча {betboom_match}: {e}")
                    continue
            
            self.logger.info(f"Анализ {self.sport_name} завершен: {len(recommendations)} рекомендаций")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Критическая ошибка анализа {self.sport_name}: {e}")
            return []
    
    def _find_matching_scores24_data(self, betboom_match: Dict[str, Any], 
                                   scores24_matches: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Находит соответствующий матч на Scores24"""
        # Для команд
        if 'team1' in betboom_match and 'team2' in betboom_match:
            return self.fuzzy_matcher.match_teams(
                betboom_match['team1'],
                betboom_match['team2'],
                scores24_matches
            )
        
        # Для игроков
        elif 'player1' in betboom_match and 'player2' in betboom_match:
            return self.fuzzy_matcher.match_players(
                betboom_match['player1'],
                betboom_match['player2'],
                scores24_matches
            )
        
        return None
    
    def _is_bet_available(self, match: Dict[str, Any]) -> bool:
        """Проверяет доступность ставки (отсутствие значка замка)"""
        return not match.get('is_locked', False)
    
    def _format_recommendation(self, betboom_match: Dict[str, Any], 
                             matched_data: Dict[str, Any], 
                             analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Форматирует рекомендацию для вывода"""
        # Объединяем все данные для форматирования
        recommendation_data = {
            **betboom_match,
            **matched_data,
            **analysis_result
        }
        
        return recommendation_data
    
    async def browser_request(self, url: str, action: str = "get_content") -> Dict[str, Any]:
        """
        Реальные Browser MCP запросы через automation/browser_mcp_client.py
        """
        self.logger.info(f"Browser MCP запрос: {action} -> {url}")
        
        try:
            # Импортируем Browser MCP клиент
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'automation'))
            from browser_mcp_client import get_live_matches, get_match_details, get_odds
            
            # Выполняем соответствующий запрос
            if action == "get_live_matches":
                # Определяем тип спорта из URL
                sport_type = self._extract_sport_type_from_url(url)
                return await get_live_matches(url, sport_type)
            elif action == "get_match_details":
                return await get_match_details(url)
            elif action == "get_odds":
                return await get_odds(url)
            else:
                # Fallback к заглушке для неизвестных действий
                await asyncio.sleep(1)
                return {
                    "status": "success",
                    "url": url,
                    "content": f"Browser MCP action: {action}",
                    "matches": []
                }
                
        except ImportError as e:
            self.logger.warning(f"Browser MCP клиент не найден, используем заглушку: {e}")
            # Fallback к заглушке если клиент не найден
            await asyncio.sleep(1)
            return {
                "status": "success",
                "url": url,
                "content": "Mock content from Browser MCP (fallback)",
                "matches": []
            }
        except Exception as e:
            self.logger.error(f"Ошибка Browser MCP запроса: {e}")
            return {
                "status": "error",
                "url": url,
                "error": str(e),
                "matches": []
            }
    
    def _extract_sport_type_from_url(self, url: str) -> str:
        """
        Извлечение типа спорта из URL
        
        Args:
            url: URL сайта
            
        Returns:
            Тип спорта
        """
        if "football" in url:
            return "football"
        elif "tennis" in url:
            return "tennis"
        elif "table-tennis" in url:
            return "table-tennis"
        elif "handball" in url:
            return "handball"
        else:
            return "football"  # По умолчанию