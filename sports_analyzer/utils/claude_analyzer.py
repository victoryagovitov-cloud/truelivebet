"""
Модуль для анализа спортивных матчей с помощью Claude AI
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class ClaudeAnalyzer:
    """Анализатор спортивных событий на базе Claude AI"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "YOUR_CLAUDE_API_KEY"
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-5-sonnet-20241022"
        
        # Заголовки для API запросов
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
    
    async def analyze_football_match(self, betboom_data: Dict[str, Any], 
                                   scores24_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ футбольного матча через Claude"""
        
        prompt = f"""
Ты эксперт по анализу футбольных матчей. Проанализируй следующий live матч и определи вероятность победы команды, которая сейчас ведет в счете.

ДАННЫЕ МАТЧА (BetBoom):
- Команды: {betboom_data.get('team1')} vs {betboom_data.get('team2')}
- Текущий счет: {betboom_data.get('score')}
- Минута: {betboom_data.get('minute')}'
- Лига: {betboom_data.get('league')}
- Коэффициенты: П1={betboom_data.get('odds', {}).get('1')}, Х={betboom_data.get('odds', {}).get('X')}, П2={betboom_data.get('odds', {}).get('2')}

СТАТИСТИКА (Scores24):
- Позиции в таблице: {scores24_data.get('league_position1')} vs {scores24_data.get('league_position2')}
- Форма команд: {scores24_data.get('form1')} vs {scores24_data.get('form2')} (W=победа, D=ничья, L=поражение)
- Голы за последние 5 матчей: {scores24_data.get('recent_goals1')} vs {scores24_data.get('recent_goals2')}
- Уровень лиги: {scores24_data.get('league_level')}

ЗАДАЧА:
1. Определи, является ли команда, ведущая в счете, объективным фаворитом
2. Оцени вероятность ее победы (в процентах)
3. Дай краткое обоснование (максимум 80 символов)

ТРЕБОВАНИЯ:
- Рекомендуй ставку только если вероятность >80%
- Учитывай время матча (поздние голы важнее)
- Анализируй форму, позицию в таблице, уровень лиги
- Будь консервативен в оценках

Ответь СТРОГО в JSON формате:
{{
    "confidence": число_от_0_до_100,
    "is_favorite_leading": true/false,
    "reasoning": "краткое_обоснование_до_80_символов",
    "recommendation": "bet"/"skip",
    "analysis_details": "подробный_анализ"
}}
"""
        
        return await self._make_claude_request(prompt)
    
    async def analyze_tennis_match(self, betboom_data: Dict[str, Any], 
                                 scores24_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ теннисного матча через Claude"""
        
        prompt = f"""
Ты эксперт по анализу теннисных матчей. Проанализируй следующий live матч и определи вероятность победы игрока, который сейчас ведет.

ДАННЫЕ МАТЧА (BetBoom):
- Игроки: {betboom_data.get('player1')} vs {betboom_data.get('player2')}
- Счет по сетам: {betboom_data.get('sets_score')}
- Счет в геймах: {betboom_data.get('games_score')}
- Турнир: {betboom_data.get('tournament')}
- Коэффициенты: П1={betboom_data.get('odds', {}).get('1')}, П2={betboom_data.get('odds', {}).get('2')}

СТАТИСТИКА (Scores24):
- Рейтинг ATP/WTA: {scores24_data.get('ranking1')} vs {scores24_data.get('ranking2')}
- Форма игроков: {scores24_data.get('form1')} vs {scores24_data.get('form2')} (W=победа, L=поражение)
- Очные встречи: {scores24_data.get('head_to_head')} (победы первого-второго)
- Предпочтение покрытия: {scores24_data.get('surface_preference1')} vs {scores24_data.get('surface_preference2')}

ЗАДАЧА:
1. Определи, является ли игрок, ведущий в матче, объективным фаворитом
2. Оцени вероятность его победы (в процентах)
3. Дай краткое обоснование

ОСОБЕННОСТИ ТЕННИСА:
- Выигрыш первого сета дает психологическое преимущество
- Разрыв в 4+ гейма в сете критичен
- Рейтинг и форма - ключевые факторы
- Очные встречи показывают стиль игры

Ответь СТРОГО в JSON формате:
{{
    "confidence": число_от_0_до_100,
    "is_favorite_leading": true/false,
    "reasoning": "краткое_обоснование_до_80_символов",
    "recommendation": "bet"/"skip",
    "analysis_details": "подробный_анализ"
}}
"""
        
        return await self._make_claude_request(prompt)
    
    async def analyze_table_tennis_match(self, betboom_data: Dict[str, Any], 
                                       scores24_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ матча настольного тенниса через Claude"""
        
        prompt = f"""
Ты эксперт по анализу настольного тенниса. Проанализируй следующий live матч и определи вероятность победы игрока, который ведет по сетам.

ДАННЫЕ МАТЧА (BetBoom):
- Игроки: {betboom_data.get('player1')} vs {betboom_data.get('player2')}
- Счет по сетам: {betboom_data.get('sets_score')}
- Текущий сет: {betboom_data.get('current_set_score')}
- Турнир: {betboom_data.get('tournament')}
- Коэффициенты: П1={betboom_data.get('odds', {}).get('1')}, П2={betboom_data.get('odds', {}).get('2')}

СТАТИСТИКА (Scores24):
- Рейтинг ITTF: {scores24_data.get('ranking1')} vs {scores24_data.get('ranking2')}
- Форма игроков: {scores24_data.get('form1')} vs {scores24_data.get('form2')}
- Процент побед: {scores24_data.get('recent_performance1')}% vs {scores24_data.get('recent_performance2')}%

ЗАДАЧА:
1. Определи, является ли игрок, ведущий по сетам, объективным фаворитом
2. Оцени вероятность его победы
3. Дай краткое обоснование

ОСОБЕННОСТИ НАСТОЛЬНОГО ТЕННИСА:
- Преимущество в сетах критично (до 3-4 сетов)
- Быстрая смена инициативы возможна
- Рейтинг ITTF очень важен
- Форма и стабильность ключевые

Ответь СТРОГО в JSON формате:
{{
    "confidence": число_от_0_до_100,
    "is_favorite_leading": true/false,
    "reasoning": "краткое_обоснование_до_80_символов",
    "recommendation": "bet"/"skip",
    "analysis_details": "подробный_анализ"
}}
"""
        
        return await self._make_claude_request(prompt)
    
    async def analyze_handball_victory(self, betboom_data: Dict[str, Any], 
                                     scores24_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ гандбольного матча (прямая победа) через Claude"""
        
        prompt = f"""
Ты эксперт по анализу гандбольных матчей. Проанализируй следующий live матч где одна команда ведет с большим разрывом.

ДАННЫЕ МАТЧА (BetBoom):
- Команды: {betboom_data.get('team1')} vs {betboom_data.get('team2')}
- Текущий счет: {betboom_data.get('score')}
- Минута: {betboom_data.get('minute')}' ({betboom_data.get('half')}-й тайм)
- Лига: {betboom_data.get('league')}
- Коэффициенты: П1={betboom_data.get('odds', {}).get('1')}, П2={betboom_data.get('odds', {}).get('2')}

СТАТИСТИКА (Scores24):
- Позиции в таблице: {scores24_data.get('league_position1')} vs {scores24_data.get('league_position2')}
- Форма команд: {scores24_data.get('form1')} vs {scores24_data.get('form2')}
- Средняя результативность: {scores24_data.get('avg_goals_per_match1')} vs {scores24_data.get('avg_goals_per_match2')} голов за матч

ЗАДАЧА:
1. Определи, сможет ли ведущая команда удержать преимущество
2. Оцени вероятность ее победы
3. Учти особенности гандбола

ОСОБЕННОСТИ ГАНДБОЛА:
- Разрыв в 5+ голов обычно критичен
- Время матча важно (поздние голы сложнее отыграть)
- Форма команд и позиция в таблице показательны
- Результативность команд влияет на стиль игры

Ответь СТРОГО в JSON формате:
{{
    "confidence": число_от_0_до_100,
    "is_favorite_leading": true/false,
    "reasoning": "краткое_обоснование_до_80_символов",
    "recommendation": "bet"/"skip",
    "analysis_details": "подробный_анализ"
}}
"""
        
        return await self._make_claude_request(prompt)
    
    async def analyze_handball_total(self, betboom_data: Dict[str, Any], 
                                   scores24_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ тотала в гандбольном матче через Claude"""
        
        total_goals = betboom_data.get('total_goals', 0)
        minutes_played = betboom_data.get('minutes_played', 60)
        predicted_total = betboom_data.get('predicted_total', 60)
        
        prompt = f"""
Ты эксперт по анализу тоталов в гандболе. Проанализируй темп игры и дай рекомендацию по тоталу.

ДАННЫЕ МАТЧА:
- Команды: {betboom_data.get('team1')} vs {betboom_data.get('team2')}
- Текущий счет: {betboom_data.get('score')}
- Минута: {betboom_data.get('minute')}' (2-й тайм)
- Всего голов: {total_goals}
- Сыграно минут: {minutes_played}
- Прогнозный тотал: {predicted_total} (по формуле)

РАСЧЕТ ТОТАЛА:
- ТМ (тотал меньше) = {predicted_total + 4}
- ТБ (тотал больше) = {predicted_total - 4}

СТАТИСТИКА КОМАНД:
- Средняя результативность: {scores24_data.get('avg_goals_per_match1')} vs {scores24_data.get('avg_goals_per_match2')}
- Форма: {scores24_data.get('form1')} vs {scores24_data.get('form2')}

ЛОГИКА АНАЛИЗА:
- Если голов < минут → МЕДЛЕННЫЙ темп → рекомендуй ТМ
- Если голов > минут → БЫСТРЫЙ темп → рекомендуй ТБ
- Если голов ≈ минут → можно рассмотреть обе ставки

ЗАДАЧА:
1. Оцени текущий темп игры
2. Спрогнозируй будет ли он сохраняться
3. Дай рекомендацию по тоталу
4. Оцени уверенность в прогнозе

Ответь СТРОГО в JSON формате:
{{
    "confidence": число_от_0_до_100,
    "pace": "БЫСТРЫЙ"/"МЕДЛЕННЫЙ"/"НЕЙТРАЛЬНЫЙ",
    "recommendation": "ТБ_число"/"ТМ_число"/"обе_ставки",
    "reasoning": "краткое_обоснование_до_80_символов",
    "bet_type": "total",
    "analysis_details": "подробный_анализ_темпа_игры"
}}
"""
        
        return await self._make_claude_request(prompt)
    
    async def _make_claude_request(self, prompt: str) -> Dict[str, Any]:
        """Выполняет запрос к Claude API"""
        
        # В тестовом режиме возвращаем заглушку
        if self.api_key == "YOUR_CLAUDE_API_KEY":
            logger.info("ТЕСТОВЫЙ РЕЖИМ Claude - возвращаем заглушку")
            return await self._get_mock_response(prompt)
        
        try:
            payload = {
                "model": self.model,
                "max_tokens": 1000,
                "temperature": 0.1,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Асинхронный запрос
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: requests.post(self.base_url, headers=self.headers, json=payload, timeout=30)
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['content'][0]['text']
                
                # Парсим JSON ответ от Claude
                try:
                    analysis_result = json.loads(content)
                    logger.info("Успешный анализ через Claude API")
                    return analysis_result
                except json.JSONDecodeError:
                    logger.error(f"Ошибка парсинга JSON ответа Claude: {content}")
                    return self._get_error_response()
            else:
                logger.error(f"Ошибка Claude API: {response.status_code} - {response.text}")
                return self._get_error_response()
                
        except Exception as e:
            logger.error(f"Исключение при запросе к Claude: {e}")
            return self._get_error_response()
    
    async def _get_mock_response(self, prompt: str) -> Dict[str, Any]:
        """Генерирует заглушку ответа для тестирования"""
        await asyncio.sleep(0.5)  # Имитация задержки API
        
        # Определяем тип анализа по промпту
        if "футбол" in prompt.lower():
            return {
                "confidence": 85,
                "is_favorite_leading": True,
                "reasoning": "Лидер таблицы ведет дома, отличная форма",
                "recommendation": "bet",
                "analysis_details": "Команда показывает стабильную игру, статистическое преимущество подтверждается"
            }
        elif "теннис" in prompt.lower() and "настольный" not in prompt.lower():
            return {
                "confidence": 82,
                "is_favorite_leading": True,
                "reasoning": "Выиграл сет, выше в рейтинге, хорошая форма",
                "recommendation": "bet",
                "analysis_details": "Психологическое преимущество после выигрыша сета, рейтинговый фаворит"
            }
        elif "настольный" in prompt.lower():
            return {
                "confidence": 88,
                "is_favorite_leading": True,
                "reasoning": "Ведет 2:0, топ рейтинг, стабильная игра",
                "recommendation": "bet",
                "analysis_details": "Преимущество в сетах критично, статистика в пользу лидера"
            }
        elif "гандбол" in prompt.lower():
            if "тотал" in prompt.lower():
                return {
                    "confidence": 80,
                    "pace": "БЫСТРЫЙ",
                    "recommendation": "ТБ_56",
                    "reasoning": "Высокий темп, результативные команды",
                    "bet_type": "total",
                    "analysis_details": "Игра идет в высоком темпе, команды показывают атакующий стиль"
                }
            else:
                return {
                    "confidence": 87,
                    "is_favorite_leading": True,
                    "reasoning": "Большой разрыв, сильнейшая команда",
                    "recommendation": "bet",
                    "analysis_details": "Разрыв в 5+ голов критичен, статистика подтверждает преимущество"
                }
        
        return self._get_error_response()
    
    def _get_error_response(self) -> Dict[str, Any]:
        """Возвращает ответ при ошибке"""
        return {
            "confidence": 0,
            "is_favorite_leading": False,
            "reasoning": "Ошибка анализа",
            "recommendation": "skip",
            "analysis_details": "Не удалось выполнить анализ"
        }
    
    async def analyze_multiple_matches(self, sport: str, matches_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Анализирует несколько матчей параллельно"""
        
        tasks = []
        for match_data in matches_data:
            betboom_match = match_data['betboom_match']
            scores24_match = match_data['scores24_match']
            
            if sport == 'football':
                task = self.analyze_football_match(betboom_match, scores24_match)
            elif sport == 'tennis':
                task = self.analyze_tennis_match(betboom_match, scores24_match)
            elif sport == 'table_tennis':
                task = self.analyze_table_tennis_match(betboom_match, scores24_match)
            elif sport == 'handball':
                if betboom_match.get('analysis_type') == 'total':
                    task = self.analyze_handball_total(betboom_match, scores24_match)
                else:
                    task = self.analyze_handball_victory(betboom_match, scores24_match)
            else:
                continue
            
            tasks.append(task)
        
        # Выполняем все анализы параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Обрабатываем результаты
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Ошибка анализа матча {i}: {result}")
            elif result.get('recommendation') == 'bet':
                # Добавляем исходные данные к результату
                result['original_data'] = matches_data[i]
                valid_results.append(result)
        
        return valid_results