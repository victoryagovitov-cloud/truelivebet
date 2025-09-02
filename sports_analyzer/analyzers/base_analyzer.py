"""
Базовый класс для анализаторов спортивных событий
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC):
    """Базовый класс для всех анализаторов видов спорта"""
    
    def __init__(self, fuzzy_matcher, sport_name: str):
        self.fuzzy_matcher = fuzzy_matcher
        self.sport_name = sport_name
        self.logger = logging.getLogger(f"{__name__}.{sport_name}")
    
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
    def analyze_match_statistics(self, betboom_match: Dict[str, Any], 
                               scores24_match: Dict[str, Any]) -> Dict[str, Any]:
        """Анализирует статистику матча для определения фаворита"""
        pass
    
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
                    
                    # Анализ статистики
                    analysis_result = self.analyze_match_statistics(
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
        Заглушка для Browser MCP запросов
        В реальной реализации здесь будет интеграция с Browser MCP
        """
        self.logger.info(f"Browser MCP запрос: {action} -> {url}")
        
        # Имитация задержки сетевого запроса
        await asyncio.sleep(1)
        
        # Заглушка ответа
        return {
            "status": "success",
            "url": url,
            "content": "Mock content from Browser MCP",
            "matches": []
        }