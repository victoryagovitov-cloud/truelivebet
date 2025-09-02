"""
Анализатор футбольных матчей
Находит матчи где ведет сильнейшая команда с не ничейным счетом
"""

import re
from typing import List, Dict, Any
from .base_analyzer import BaseAnalyzer
from config.settings import BETTING_SITES


class FootballAnalyzer(BaseAnalyzer):
    """Анализатор футбольных матчей"""
    
    def __init__(self, fuzzy_matcher):
        super().__init__(fuzzy_matcher, "football")
    
    async def get_betboom_matches(self) -> List[Dict[str, Any]]:
        """Получает live футбольные матчи с BetBoom"""
        url = BETTING_SITES["betboom"]["football"]
        
        # Browser MCP запрос
        response = await self.browser_request(url, "get_live_matches")
        
        # Парсинг данных (заглушка - в реальности парсим HTML)
        matches = [
            {
                "team1": "Манчестер Сити",
                "team2": "Ливерпуль", 
                "score": "2:1",
                "minute": 67,
                "odds": {"1": 1.85, "X": 3.20, "2": 4.50},
                "is_locked": False,
                "league": "Премьер-лига"
            },
            {
                "team1": "Барселона",
                "team2": "Реал Мадрид",
                "score": "1:0", 
                "minute": 34,
                "odds": {"1": 2.10, "X": 3.40, "2": 3.20},
                "is_locked": False,
                "league": "Ла Лига"
            }
        ]
        
        self.logger.info(f"Получено {len(matches)} футбольных матчей с BetBoom")
        return matches
    
    async def get_scores24_matches(self) -> List[Dict[str, Any]]:
        """Получает live футбольные матчи со Scores24"""
        url = BETTING_SITES["scores24"]["football"]
        
        # Browser MCP запрос
        response = await self.browser_request(url, "get_live_matches")
        
        # Парсинг данных (заглушка)
        matches = [
            {
                "team1": "Ман Сити",
                "team2": "Ливерпуль",
                "league_position1": 2,
                "league_position2": 3,
                "form1": "WWWDW",  # Последние 5 матчей
                "form2": "WDWLW",
                "league_level": "top",
                "recent_goals1": 12,  # Голы за последние 5 матчей
                "recent_goals2": 8
            },
            {
                "team1": "Barcelona", 
                "team2": "Real Madrid",
                "league_position1": 1,
                "league_position2": 2,
                "form1": "WWWWW",
                "form2": "WWDWL", 
                "league_level": "top",
                "recent_goals1": 15,
                "recent_goals2": 11
            }
        ]
        
        self.logger.info(f"Получено {len(matches)} футбольных матчей со Scores24")
        return matches
    
    def filter_matches_by_criteria(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Фильтрует матчи с не ничейным счетом"""
        filtered = []
        
        for match in matches:
            score = match.get('score', '')
            
            # Парсим счет
            if ':' in score:
                try:
                    goals1, goals2 = map(int, score.split(':'))
                    
                    # Проверяем что счет не ничейный
                    if goals1 != goals2:
                        filtered.append(match)
                        self.logger.debug(f"Матч прошел фильтр: {match['team1']} - {match['team2']} ({score})")
                    
                except ValueError:
                    self.logger.warning(f"Не удалось распарсить счет: {score}")
                    continue
        
        return filtered
    
    def analyze_match_statistics(self, betboom_match: Dict[str, Any], 
                               scores24_match: Dict[str, Any]) -> Dict[str, Any]:
        """Анализирует статистику для определения фаворита"""
        score = betboom_match.get('score', '')
        
        try:
            goals1, goals2 = map(int, score.split(':'))
            leading_team = 1 if goals1 > goals2 else 2
            
            # Анализ формы команд
            form1 = scores24_match.get('form1', '')
            form2 = scores24_match.get('form2', '')
            
            form_score1 = self._calculate_form_score(form1)
            form_score2 = self._calculate_form_score(form2)
            
            # Анализ позиций в таблице
            pos1 = scores24_match.get('league_position1', 10)
            pos2 = scores24_match.get('league_position2', 10)
            
            position_advantage1 = max(0, pos2 - pos1) * 5  # Бонус за лучшую позицию
            position_advantage2 = max(0, pos1 - pos2) * 5
            
            # Анализ результативности
            goals_avg1 = scores24_match.get('recent_goals1', 0) / 5
            goals_avg2 = scores24_match.get('recent_goals2', 0) / 5
            
            # Общий рейтинг команд
            team1_rating = form_score1 + position_advantage1 + goals_avg1 * 10
            team2_rating = form_score2 + position_advantage2 + goals_avg2 * 10
            
            # Определяем фаворита и его уверенность
            if leading_team == 1:
                is_favorite_leading = team1_rating >= team2_rating
                confidence = min(95, 60 + abs(team1_rating - team2_rating) * 2)
                favorite_name = betboom_match['team1']
            else:
                is_favorite_leading = team2_rating >= team1_rating
                confidence = min(95, 60 + abs(team2_rating - team1_rating) * 2)
                favorite_name = betboom_match['team2']
            
            # Если ведет не фаворит, снижаем уверенность
            if not is_favorite_leading:
                confidence = max(30, confidence - 40)
            
            # Формируем обоснование
            reasoning_parts = []
            
            if leading_team == 1:
                if form_score1 > form_score2:
                    reasoning_parts.append(f"{betboom_match['team1']} в лучшей форме")
                if pos1 < pos2:
                    reasoning_parts.append(f"выше в таблице ({pos1} vs {pos2})")
                if goals_avg1 > goals_avg2:
                    reasoning_parts.append(f"более результативна")
            else:
                if form_score2 > form_score1:
                    reasoning_parts.append(f"{betboom_match['team2']} в лучшей форме")
                if pos2 < pos1:
                    reasoning_parts.append(f"выше в таблице ({pos2} vs {pos1})")
                if goals_avg2 > goals_avg1:
                    reasoning_parts.append(f"более результативна")
            
            reasoning = ", ".join(reasoning_parts) if reasoning_parts else "статистические показатели"
            
            return {
                "confidence": round(confidence),
                "favorite_team": favorite_name,
                "is_favorite_leading": is_favorite_leading,
                "reasoning": reasoning,
                "team1_rating": round(team1_rating, 1),
                "team2_rating": round(team2_rating, 1)
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа статистики: {e}")
            return {"confidence": 0, "reasoning": "Ошибка анализа"}
    
    def _calculate_form_score(self, form: str) -> int:
        """Вычисляет очки формы команды на основе последних результатов"""
        if not form:
            return 50
        
        score = 0
        for result in form:
            if result == 'W':
                score += 20
            elif result == 'D':
                score += 10
            elif result == 'L':
                score += 0
        
        return score