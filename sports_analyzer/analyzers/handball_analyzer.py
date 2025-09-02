"""
Анализатор гандбольных матчей
Находит прямые победы и анализирует тоталы
"""

import math
from typing import List, Dict, Any
from .base_analyzer import BaseAnalyzer
from config.settings import BETTING_SITES


class HandballAnalyzer(BaseAnalyzer):
    """Анализатор гандбольных матчей"""
    
    def __init__(self, fuzzy_matcher):
        super().__init__(fuzzy_matcher, "handball")
    
    async def get_betboom_matches(self) -> List[Dict[str, Any]]:
        """Получает live гандбольные матчи с BetBoom"""
        url = BETTING_SITES["betboom"]["handball"]
        
        response = await self.browser_request(url, "get_live_matches")
        
        # Заглушка данных
        matches = [
            {
                "team1": "Барселона",
                "team2": "Киль",
                "score": "25:20",
                "minute": 35,
                "half": 2,
                "odds": {"1": 1.45, "X": 8.50, "2": 2.85},
                "is_locked": False,
                "league": "Лига чемпионов"
            },
            {
                "team1": "ПСЖ",
                "team2": "Варшава",
                "score": "18:16", 
                "minute": 50,
                "half": 2,
                "odds": {"1": 1.95, "X": 12.0, "2": 1.75},
                "is_locked": False,
                "league": "Лига чемпионов"
            }
        ]
        
        self.logger.info(f"Получено {len(matches)} гандбольных матчей с BetBoom")
        return matches
    
    async def get_scores24_matches(self) -> List[Dict[str, Any]]:
        """Получает live гандбольные матчи со Scores24"""
        url = BETTING_SITES["scores24"]["handball"]
        
        response = await self.browser_request(url, "get_live_matches")
        
        # Заглушка данных
        matches = [
            {
                "team1": "Барселона Эспаньол",
                "team2": "THW Kiel",
                "league_position1": 1,
                "league_position2": 4,
                "form1": "WWWDW",
                "form2": "WDLWW",
                "avg_goals_per_match1": 32.5,
                "avg_goals_per_match2": 28.3
            },
            {
                "team1": "Paris Saint-Germain",
                "team2": "Wisla Plock",
                "league_position1": 2,
                "league_position2": 8,
                "form1": "WWDWW",
                "form2": "LDWLL",
                "avg_goals_per_match1": 30.2,
                "avg_goals_per_match2": 25.8
            }
        ]
        
        self.logger.info(f"Получено {len(matches)} гандбольных матчей со Scores24")
        return matches
    
    def filter_matches_by_criteria(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Фильтрует матчи по критериям гандбола"""
        filtered = []
        
        for match in matches:
            score = match.get('score', '')
            minute = match.get('minute', 0)
            half = match.get('half', 1)
            
            # Парсим счет
            if ':' in score:
                try:
                    goals1, goals2 = map(int, score.split(':'))
                    goal_difference = abs(goals1 - goals2)
                    
                    # Критерий 1: Разрыв ≥5 голов (для прямых побед)
                    if goal_difference >= 5:
                        match['analysis_type'] = 'victory'
                        filtered.append(match)
                        self.logger.debug(f"Матч прошел фильтр (победа): {match['team1']} - {match['team2']} ({score})")
                    
                    # Критерий 2: Тоталы (2-й тайм, 10-45 минута)
                    elif half == 2 and 10 <= minute <= 45:
                        match['analysis_type'] = 'total'
                        match['total_goals'] = goals1 + goals2
                        match['minutes_played'] = minute + 30  # Первый тайм + текущие минуты
                        filtered.append(match)
                        self.logger.debug(f"Матч прошел фильтр (тотал): {match['team1']} - {match['team2']} ({score})")
                    
                except ValueError:
                    self.logger.warning(f"Не удалось распарсить счет: {score}")
                    continue
        
        return filtered
    
    async def analyze_match_statistics(self, betboom_match: Dict[str, Any], 
                                     scores24_match: Dict[str, Any]) -> Dict[str, Any]:
        """Анализирует статистику гандбольного матча через Claude AI"""
        analysis_type = betboom_match.get('analysis_type', 'victory')
        
        # Используем Claude для анализа
        if analysis_type == 'victory':
            claude_result = await self.claude_analyzer.analyze_handball_victory(
                betboom_match, scores24_match
            )
        elif analysis_type == 'total':
            claude_result = await self.claude_analyzer.analyze_handball_total(
                betboom_match, scores24_match
            )
        else:
            return {"confidence": 0, "reasoning": "Неизвестный тип анализа"}
        
        # Если Claude анализ неудачен, используем fallback логику
        if claude_result.get('confidence', 0) == 0:
            if analysis_type == 'victory':
                return self._fallback_victory_analysis(betboom_match, scores24_match)
            else:
                return self._fallback_total_analysis(betboom_match, scores24_match)
        
        return claude_result
    
    def _fallback_victory_analysis(self, betboom_match: Dict[str, Any], 
                                  scores24_match: Dict[str, Any]) -> Dict[str, Any]:
        """Резервный анализ вероятности победы при большом разрыве"""
        score = betboom_match.get('score', '')
        goals1, goals2 = map(int, score.split(':'))
        
        leading_team = 1 if goals1 > goals2 else 2
        goal_difference = abs(goals1 - goals2)
        
        # Анализ формы команд
        form1 = scores24_match.get('form1', '')
        form2 = scores24_match.get('form2', '')
        
        form_score1 = self._calculate_form_score(form1)
        form_score2 = self._calculate_form_score(form2)
        
        # Анализ позиций
        pos1 = scores24_match.get('league_position1', 10)
        pos2 = scores24_match.get('league_position2', 10)
        
        # Базовая уверенность на основе разрыва
        base_confidence = min(95, 60 + goal_difference * 5)
        
        # Корректировка на основе статистики
        if leading_team == 1:
            if form_score1 > form_score2 and pos1 < pos2:
                confidence = min(95, base_confidence + 15)
                reasoning = f"Ведет сильнейшая команда с разрывом {goal_difference} голов, лучшая форма и позиция в таблице"
            elif form_score1 > form_score2 or pos1 < pos2:
                confidence = min(90, base_confidence + 10)
                reasoning = f"Ведет с разрывом {goal_difference} голов, статистическое преимущество"
            else:
                confidence = max(50, base_confidence - 10)
                reasoning = f"Большой разрыв {goal_difference} голов, но статистика не в пользу лидера"
        else:
            if form_score2 > form_score1 and pos2 < pos1:
                confidence = min(95, base_confidence + 15)
                reasoning = f"Ведет сильнейшая команда с разрывом {goal_difference} голов, лучшая форма и позиция в таблице"
            elif form_score2 > form_score1 or pos2 < pos1:
                confidence = min(90, base_confidence + 10)
                reasoning = f"Ведет с разрывом {goal_difference} голов, статистическое преимущество"
            else:
                confidence = max(50, base_confidence - 10)
                reasoning = f"Большой разрыв {goal_difference} голов, но статистика не в пользу лидера"
        
        return {
            "confidence": round(confidence),
            "reasoning": reasoning,
            "bet_type": "victory",
            "leading_team": leading_team,
            "goal_difference": goal_difference
        }
    
    def _fallback_total_analysis(self, betboom_match: Dict[str, Any], 
                                scores24_match: Dict[str, Any]) -> Dict[str, Any]:
        """Резервный анализ тоталов по формуле из требований"""
        total_goals = betboom_match.get('total_goals', 0)
        minutes_played = betboom_match.get('minutes_played', 60)
        
        # Формула расчета прогнозного тотала
        predicted_total_raw = (total_goals / minutes_played) * 60
        predicted_total = math.ceil(predicted_total_raw)  # Округление в большую сторону
        
        # Построение интервала
        total_under = predicted_total + 4  # ТМ
        total_over = predicted_total - 4   # ТБ
        
        # Определение темпа игры
        if total_goals < minutes_played:
            pace = "МЕДЛЕННЫЙ"
            recommendation = f"ТМ {total_under}"
            pace_description = "Медленный"
        elif total_goals > minutes_played:
            pace = "БЫСТРЫЙ"
            recommendation = f"ТБ {total_over}"
            pace_description = "Быстрый"
        else:
            pace = "НЕЙТРАЛЬНЫЙ"
            recommendation = f"ТМ {total_under} или ТБ {total_over}"
            pace_description = "Нейтральный"
        
        # Уверенность зависит от стабильности темпа
        tempo_stability = abs(total_goals - minutes_played)
        if tempo_stability >= 10:
            confidence = 85
        elif tempo_stability >= 5:
            confidence = 80
        else:
            confidence = 75
        
        return {
            "confidence": confidence,
            "bet_type": "total",
            "predicted_total": predicted_total,
            "recommendation": recommendation,
            "pace": pace,
            "pace_description": pace_description,
            "total_goals": total_goals,
            "minutes_played": minutes_played,
            "reasoning": f"{pace_description} темп игры ({total_goals} голов за {minutes_played} минут)"
        }
    
    def _calculate_form_score(self, form: str) -> int:
        """Вычисляет очки формы команды"""
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