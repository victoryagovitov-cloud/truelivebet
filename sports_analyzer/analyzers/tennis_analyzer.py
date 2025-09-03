"""
Анализатор теннисных матчей  
Находит матчи где фаворит выиграл первый сет или ведет с большим разрывом
"""

import re
from typing import List, Dict, Any
from .base_analyzer import BaseAnalyzer
from config.settings import BETTING_SITES


class TennisAnalyzer(BaseAnalyzer):
    """Анализатор теннисных матчей"""
    
    def __init__(self, fuzzy_matcher):
        super().__init__(fuzzy_matcher, "tennis")
    
    async def get_betboom_matches(self) -> List[Dict[str, Any]]:
        """Получает live теннисные матчи с BetBoom"""
        url = BETTING_SITES["betboom"]["tennis"]
        
        response = await self.browser_request(url, "get_live_matches")
        
        # Заглушка данных
        matches = [
            {
                "player1": "Новак Джокович",
                "player2": "Рафаэль Надаль",
                "sets_score": "1-0",
                "games_score": "6-4, 3-1",
                "current_set": 2,
                "odds": {"1": 1.65, "2": 2.20},
                "is_locked": False,
                "tournament": "Australian Open"
            },
            {
                "player1": "Даниил Медведев", 
                "player2": "Александр Зверев",
                "sets_score": "0-0",
                "games_score": "6-2",
                "current_set": 1,
                "odds": {"1": 1.95, "2": 1.75},
                "is_locked": False,
                "tournament": "ATP Masters"
            }
        ]
        
        self.logger.info(f"Получено {len(matches)} теннисных матчей с BetBoom")
        return matches
    
    async def get_scores24_matches(self) -> List[Dict[str, Any]]:
        """Получает live теннисные матчи со Scores24"""
        url = BETTING_SITES["scores24"]["tennis"]
        
        response = await self.browser_request(url, "get_live_matches")
        
        # Заглушка данных
        matches = [
            {
                "player1": "Джокович Н.",
                "player2": "Надаль Р.",
                "ranking1": 1,
                "ranking2": 2,
                "form1": "WWWLW",  # Последние 5 матчей
                "form2": "WLWWL",
                "head_to_head": "15-10",  # Победы первого игрока - второго
                "surface_preference1": "hard",
                "surface_preference2": "clay"
            },
            {
                "player1": "Медведев Д.",
                "player2": "Зверев А.", 
                "ranking1": 3,
                "ranking2": 4,
                "form1": "LWWWW",
                "form2": "WWLWW",
                "head_to_head": "8-6",
                "surface_preference1": "hard",
                "surface_preference2": "hard"
            }
        ]
        
        self.logger.info(f"Получено {len(matches)} теннисных матчей со Scores24")
        return matches
    
    def filter_matches_by_criteria(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Фильтрует матчи по критериям тенниса"""
        filtered = []
        
        for match in matches:
            sets_score = match.get('sets_score', '')
            games_score = match.get('games_score', '')
            
            # Критерий 1: Выиграл первый сет (счет 1-0 по сетам)
            if sets_score == "1-0":
                filtered.append(match)
                self.logger.debug(f"Матч прошел фильтр (выиграл сет): {match['player1']} - {match['player2']}")
                continue
            
            # Критерий 2: Ведет в первом сете с разрывом ≥4 гейма
            if sets_score == "0-0" and games_score:
                try:
                    # Парсим счет в текущем сете
                    current_games = games_score.split(',')[-1].strip()
                    if '-' in current_games:
                        games1, games2 = map(int, current_games.split('-'))
                        games_difference = abs(games1 - games2)
                        
                        if games_difference >= 4:
                            filtered.append(match)
                            self.logger.debug(f"Матч прошел фильтр (разрыв в сете): {match['player1']} - {match['player2']} ({current_games})")
                
                except (ValueError, IndexError):
                    self.logger.warning(f"Не удалось распарсить счет в геймах: {games_score}")
                    continue
        
        return filtered
    
    async def analyze_match_statistics(self, betboom_match: Dict[str, Any], 
                                     scores24_match: Dict[str, Any]) -> Dict[str, Any]:
        """Анализирует статистику теннисного матча через Claude AI"""
        
        # Используем Claude для анализа
        claude_result = await self.claude_analyzer.analyze_tennis_match(
            betboom_match, scores24_match
        )
        
        # Если Claude анализ неудачен, используем fallback логику
        if claude_result.get('confidence', 0) == 0:
            return self._fallback_analysis(betboom_match, scores24_match)
        
        return claude_result
    
    def _fallback_analysis(self, betboom_match: Dict[str, Any], 
                          scores24_match: Dict[str, Any]) -> Dict[str, Any]:
        """Резервный анализ если Claude недоступен"""
        sets_score = betboom_match.get('sets_score', '')
        games_score = betboom_match.get('games_score', '')
        
        # Определяем кто ведет
        if sets_score == "1-0":
            leading_player = 1
            advantage_type = "set"
        else:
            # Анализируем текущий сет
            current_games = games_score.split(',')[-1].strip()
            games1, games2 = map(int, current_games.split('-'))
            leading_player = 1 if games1 > games2 else 2
            advantage_type = "games"
        
        # Анализ статистики игроков
        ranking1 = scores24_match.get('ranking1', 100)
        ranking2 = scores24_match.get('ranking2', 100)
        
        form1 = scores24_match.get('form1', '')
        form2 = scores24_match.get('form2', '')
        
        form_score1 = self._calculate_form_score(form1)
        form_score2 = self._calculate_form_score(form2)
        
        # Анализ очных встреч
        h2h = scores24_match.get('head_to_head', '0-0')
        h2h_wins1, h2h_wins2 = map(int, h2h.split('-'))
        
        # Рейтинг игроков (чем меньше число, тем лучше рейтинг)
        ranking_advantage1 = max(0, ranking2 - ranking1) * 2
        ranking_advantage2 = max(0, ranking1 - ranking2) * 2
        
        # Преимущество в очных встречах
        h2h_total = h2h_wins1 + h2h_wins2
        if h2h_total > 0:
            h2h_advantage1 = (h2h_wins1 / h2h_total - 0.5) * 20
            h2h_advantage2 = (h2h_wins2 / h2h_total - 0.5) * 20
        else:
            h2h_advantage1 = h2h_advantage2 = 0
        
        # Общий рейтинг игроков
        player1_rating = form_score1 + ranking_advantage1 + h2h_advantage1
        player2_rating = form_score2 + ranking_advantage2 + h2h_advantage2
        
        # Определяем фаворита и уверенность
        if leading_player == 1:
            is_favorite_leading = player1_rating >= player2_rating
            confidence = min(95, 65 + abs(player1_rating - player2_rating))
            favorite_name = betboom_match['player1']
        else:
            is_favorite_leading = player2_rating >= player1_rating  
            confidence = min(95, 65 + abs(player2_rating - player1_rating))
            favorite_name = betboom_match['player2']
        
        # Бонус за преимущество в сете
        if advantage_type == "set":
            confidence += 10
        
        # Если ведет не фаворит, снижаем уверенность
        if not is_favorite_leading:
            confidence = max(40, confidence - 30)
        
        # Формируем обоснование
        reasoning_parts = []
        
        if leading_player == 1:
            if ranking1 < ranking2:
                reasoning_parts.append(f"выше в рейтинге ({ranking1} vs {ranking2})")
            if form_score1 > form_score2:
                reasoning_parts.append("лучшая форма")
            if h2h_wins1 > h2h_wins2:
                reasoning_parts.append(f"преимущество в очных встречах ({h2h})")
        else:
            if ranking2 < ranking1:
                reasoning_parts.append(f"выше в рейтинге ({ranking2} vs {ranking1})")
            if form_score2 > form_score1:
                reasoning_parts.append("лучшая форма")
            if h2h_wins2 > h2h_wins1:
                reasoning_parts.append(f"преимущество в очных встречах ({h2h_wins2}-{h2h_wins1})")
        
        reasoning = ", ".join(reasoning_parts) if reasoning_parts else "статистические показатели"
        
        return {
            "confidence": round(confidence),
            "favorite_player": favorite_name,
            "is_favorite_leading": is_favorite_leading,
            "reasoning": reasoning,
            "player1_rating": round(player1_rating, 1),
            "player2_rating": round(player2_rating, 1),
            "advantage_type": advantage_type
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