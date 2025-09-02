"""
Анализатор матчей настольного тенниса
Находит матчи где фаворит ведет 1:0 или 2:0 по сетам
"""

from typing import List, Dict, Any
from .base_analyzer import BaseAnalyzer
from config.settings import BETTING_SITES


class TableTennisAnalyzer(BaseAnalyzer):
    """Анализатор матчей настольного тенниса"""
    
    def __init__(self, fuzzy_matcher):
        super().__init__(fuzzy_matcher, "table_tennis")
    
    async def get_betboom_matches(self) -> List[Dict[str, Any]]:
        """Получает live матчи настольного тенниса с BetBoom"""
        url = BETTING_SITES["betboom"]["table_tennis"]
        
        response = await self.browser_request(url, "get_live_matches")
        
        # Заглушка данных
        matches = [
            {
                "player1": "Тимо Болль",
                "player2": "Ма Лонг",
                "sets_score": "2-0",
                "current_set_score": "8-5",
                "odds": {"1": 2.15, "2": 1.65},
                "is_locked": False,
                "tournament": "WTT Champions"
            },
            {
                "player1": "Фан Чжэндун",
                "player2": "Хуго Кальдерано",
                "sets_score": "1-0", 
                "current_set_score": "3-7",
                "odds": {"1": 1.45, "2": 2.55},
                "is_locked": False,
                "tournament": "WTT Star Contender"
            }
        ]
        
        self.logger.info(f"Получено {len(matches)} матчей настольного тенниса с BetBoom")
        return matches
    
    async def get_scores24_matches(self) -> List[Dict[str, Any]]:
        """Получает live матчи настольного тенниса со Scores24"""
        url = BETTING_SITES["scores24"]["table_tennis"]
        
        response = await self.browser_request(url, "get_live_matches")
        
        # Заглушка данных
        matches = [
            {
                "player1": "Болль Т.",
                "player2": "Лонг М.",
                "ranking1": 8,
                "ranking2": 2,
                "form1": "LWWWL",  # Последние 5 матчей
                "form2": "WWWWW",
                "recent_performance1": 75,  # Процент побед за последний месяц
                "recent_performance2": 90
            },
            {
                "player1": "Фан Ч.",
                "player2": "Кальдерано Х.",
                "ranking1": 1,
                "ranking2": 6,
                "form1": "WWWWW",
                "form2": "WLWWL", 
                "recent_performance1": 95,
                "recent_performance2": 70
            }
        ]
        
        self.logger.info(f"Получено {len(matches)} матчей настольного тенниса со Scores24")
        return matches
    
    def filter_matches_by_criteria(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Фильтрует матчи по критериям настольного тенниса"""
        filtered = []
        
        for match in matches:
            sets_score = match.get('sets_score', '')
            
            # Проверяем счет по сетам: 1-0 или 2-0
            if sets_score in ["1-0", "2-0"]:
                filtered.append(match)
                self.logger.debug(f"Матч прошел фильтр: {match['player1']} - {match['player2']} ({sets_score})")
        
        return filtered
    
    def analyze_match_statistics(self, betboom_match: Dict[str, Any], 
                               scores24_match: Dict[str, Any]) -> Dict[str, Any]:
        """Анализирует статистику матча настольного тенниса"""
        sets_score = betboom_match.get('sets_score', '')
        
        # Определяем кто ведет по сетам
        if sets_score.startswith("1-0") or sets_score.startswith("2-0"):
            leading_player = 1
        else:
            leading_player = 2
        
        # Анализ статистики игроков
        ranking1 = scores24_match.get('ranking1', 100)
        ranking2 = scores24_match.get('ranking2', 100)
        
        form1 = scores24_match.get('form1', '')
        form2 = scores24_match.get('form2', '')
        
        performance1 = scores24_match.get('recent_performance1', 50)
        performance2 = scores24_match.get('recent_performance2', 50)
        
        form_score1 = self._calculate_form_score(form1)
        form_score2 = self._calculate_form_score(form2)
        
        # Рейтинговое преимущество (чем меньше число рейтинга, тем лучше)
        ranking_advantage1 = max(0, ranking2 - ranking1) * 3
        ranking_advantage2 = max(0, ranking1 - ranking2) * 3
        
        # Общий рейтинг игроков
        player1_rating = form_score1 + ranking_advantage1 + performance1 * 0.5
        player2_rating = form_score2 + ranking_advantage2 + performance2 * 0.5
        
        # Определяем фаворита и уверенность
        if leading_player == 1:
            is_favorite_leading = player1_rating >= player2_rating
            confidence = min(95, 70 + abs(player1_rating - player2_rating) * 0.8)
            favorite_name = betboom_match['player1']
        else:
            is_favorite_leading = player2_rating >= player1_rating
            confidence = min(95, 70 + abs(player2_rating - player1_rating) * 0.8)
            favorite_name = betboom_match['player2']
        
        # Бонус за преимущество в сетах
        if sets_score == "2-0":
            confidence += 15  # Больший бонус за 2:0
        elif sets_score == "1-0":
            confidence += 10
        
        # Если ведет не фаворит, снижаем уверенность
        if not is_favorite_leading:
            confidence = max(35, confidence - 35)
        
        # Формируем обоснование
        reasoning_parts = []
        
        if leading_player == 1:
            if ranking1 < ranking2:
                reasoning_parts.append(f"выше в рейтинге ({ranking1} vs {ranking2})")
            if form_score1 > form_score2:
                reasoning_parts.append("лучшая форма")
            if performance1 > performance2:
                reasoning_parts.append(f"стабильная игра ({performance1}% побед)")
        else:
            if ranking2 < ranking1:
                reasoning_parts.append(f"выше в рейтинге ({ranking2} vs {ranking1})")
            if form_score2 > form_score1:
                reasoning_parts.append("лучшая форма")
            if performance2 > performance1:
                reasoning_parts.append(f"стабильная игра ({performance2}% побед)")
        
        reasoning = ", ".join(reasoning_parts) if reasoning_parts else "статистические показатели"
        
        return {
            "confidence": round(confidence),
            "favorite_player": favorite_name,
            "is_favorite_leading": is_favorite_leading,
            "reasoning": reasoning,
            "player1_rating": round(player1_rating, 1),
            "player2_rating": round(player2_rating, 1),
            "sets_advantage": sets_score
        }
    
    def _calculate_form_score(self, form: str) -> int:
        """Вычисляет очки формы игрока"""
        if not form:
            return 50
        
        score = 0
        for result in form:
            if result == 'W':
                score += 20
            elif result == 'L':
                score += 0
        
        return score