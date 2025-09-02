"""
Модуль для fuzzy matching названий команд и игроков
Реализует интеллектуальное сопоставление с учетом различий в написании
"""

import re
from typing import List, Tuple, Optional
from difflib import SequenceMatcher
import unicodedata


class FuzzyMatcher:
    """Класс для нечеткого сопоставления названий команд и игроков"""
    
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        
        # Словари для нормализации названий
        self.team_aliases = {
            # Футбол
            "манчестер сити": ["ман сити", "manchester city", "man city"],
            "манчестер юнайтед": ["ман юнайтед", "manchester united", "man utd"],
            "барселона": ["барса", "barcelona", "fc barcelona"],
            "реал мадрид": ["реал", "real madrid", "real"],
            "пари сен жермен": ["псж", "psg", "paris sg"],
            
            # Гандбол  
            "барселона": ["барселона эспаньол", "fc barcelona handball"],
            "пари сен жермен": ["psg handball", "paris saint-germain"],
        }
        
        self.player_aliases = {
            # Теннис
            "новак джокович": ["джокович н.", "n.djokovic", "djokovic"],
            "рафаэль надаль": ["надаль р.", "r.nadal", "nadal"],
            "роджер федерер": ["федерер р.", "r.federer", "federer"],
            
            # Настольный теннис
            "тимо болль": ["болль т.", "t.boll", "boll"],
            "ма лонг": ["лонг м.", "ma long", "long"],
        }
    
    def normalize_text(self, text: str) -> str:
        """Нормализует текст для сравнения"""
        if not text:
            return ""
            
        # Приведение к нижнему регистру
        text = text.lower().strip()
        
        # Удаление диакритических знаков
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        
        # Удаление лишних символов и нормализация пробелов
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Удаление общих префиксов/суффиксов
        prefixes_to_remove = ['fc', 'fk', 'sk', 'ac', 'sc', 'club', 'team']
        suffixes_to_remove = ['fc', 'united', 'city', 'town', 'rovers']
        
        words = text.split()
        words = [w for w in words if w not in prefixes_to_remove + suffixes_to_remove]
        
        return ' '.join(words)
    
    def get_similarity(self, text1: str, text2: str) -> float:
        """Вычисляет степень схожести двух текстов"""
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)
        
        if not norm1 or not norm2:
            return 0.0
        
        # Основное сравнение
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Бонус за точные совпадения ключевых слов
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        if words1 & words2:  # Есть общие слова
            word_overlap = len(words1 & words2) / max(len(words1), len(words2))
            similarity = max(similarity, word_overlap * 0.9)
        
        # Проверка на сокращения и аббревиатуры
        if self._check_abbreviations(norm1, norm2):
            similarity = max(similarity, 0.8)
        
        return similarity
    
    def _check_abbreviations(self, text1: str, text2: str) -> bool:
        """Проверяет совпадения через аббревиатуры"""
        # Извлечение первых букв слов
        def get_initials(text):
            return ''.join(word[0] for word in text.split() if word)
        
        initials1 = get_initials(text1)
        initials2 = get_initials(text2)
        
        # Проверка различных вариантов аббревиатур
        return (
            initials1 in text2 or initials2 in text1 or
            text1.replace(' ', '') in text2.replace(' ', '') or
            text2.replace(' ', '') in text1.replace(' ', '')
        )
    
    def find_best_match(self, target: str, candidates: List[str]) -> Optional[Tuple[str, float]]:
        """Находит наилучшее совпадение из списка кандидатов"""
        if not target or not candidates:
            return None
        
        best_match = None
        best_score = 0.0
        
        # Проверка прямых алиасов
        target_norm = self.normalize_text(target)
        for alias_key, aliases in {**self.team_aliases, **self.player_aliases}.items():
            if target_norm == self.normalize_text(alias_key):
                for candidate in candidates:
                    candidate_norm = self.normalize_text(candidate)
                    if any(self.normalize_text(alias) == candidate_norm for alias in aliases):
                        return candidate, 1.0
        
        # Fuzzy matching
        for candidate in candidates:
            score = self.get_similarity(target, candidate)
            if score > best_score:
                best_score = score
                best_match = candidate
        
        # Возвращаем результат только если превышен порог
        if best_score >= self.threshold:
            return best_match, best_score
        
        return None
    
    def match_teams(self, team1_betboom: str, team2_betboom: str, 
                   scores24_matches: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """Сопоставляет команды между BetBoom и Scores24"""
        for match in scores24_matches:
            team1_scores = match.get('team1', '')
            team2_scores = match.get('team2', '')
            
            # Проверяем оба варианта порядка команд
            score1_1 = self.get_similarity(team1_betboom, team1_scores)
            score1_2 = self.get_similarity(team2_betboom, team2_scores)
            
            score2_1 = self.get_similarity(team1_betboom, team2_scores)
            score2_2 = self.get_similarity(team2_betboom, team1_scores)
            
            # Прямой порядок
            if score1_1 >= self.threshold and score1_2 >= self.threshold:
                avg_score = (score1_1 + score1_2) / 2
                return {
                    'match': match,
                    'confidence': avg_score,
                    'team1_mapped': team1_scores,
                    'team2_mapped': team2_scores
                }
            
            # Обратный порядок
            if score2_1 >= self.threshold and score2_2 >= self.threshold:
                avg_score = (score2_1 + score2_2) / 2
                return {
                    'match': match,
                    'confidence': avg_score,
                    'team1_mapped': team2_scores,
                    'team2_mapped': team1_scores
                }
        
        return None
    
    def match_players(self, player1_betboom: str, player2_betboom: str,
                     scores24_matches: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """Сопоставляет игроков между BetBoom и Scores24"""
        for match in scores24_matches:
            player1_scores = match.get('player1', '')
            player2_scores = match.get('player2', '')
            
            # Проверяем оба варианта порядка игроков
            score1_1 = self.get_similarity(player1_betboom, player1_scores)
            score1_2 = self.get_similarity(player2_betboom, player2_scores)
            
            score2_1 = self.get_similarity(player1_betboom, player2_scores)
            score2_2 = self.get_similarity(player2_betboom, player1_scores)
            
            # Прямой порядок
            if score1_1 >= self.threshold and score1_2 >= self.threshold:
                avg_score = (score1_1 + score1_2) / 2
                return {
                    'match': match,
                    'confidence': avg_score,
                    'player1_mapped': player1_scores,
                    'player2_mapped': player2_scores
                }
            
            # Обратный порядок
            if score2_1 >= self.threshold and score2_2 >= self.threshold:
                avg_score = (score2_1 + score2_2) / 2
                return {
                    'match': match,
                    'confidence': avg_score,
                    'player1_mapped': player2_scores,
                    'player2_mapped': player1_scores
                }
        
        return None