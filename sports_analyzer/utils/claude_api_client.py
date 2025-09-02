"""
Клиент для работы с Claude API через официальную библиотеку Anthropic
"""

import asyncio
import json
import logging
from typing import Dict, Any
from anthropic import Anthropic

from config.claude_config import CLAUDE_CONFIG, SYSTEM_PROMPTS

logger = logging.getLogger(__name__)


class ClaudeAPIClient:
    """Клиент для работы с Claude API"""
    
    def __init__(self):
        self.api_key = CLAUDE_CONFIG.get("api_key")
        self.model = CLAUDE_CONFIG.get("model")
        self.max_tokens = CLAUDE_CONFIG.get("max_tokens", 1000)
        self.temperature = CLAUDE_CONFIG.get("temperature", 0.1)
        
        # Инициализация клиента Anthropic
        if self.api_key and "YOUR_CLAUDE_API_KEY" not in self.api_key:
            self.client = Anthropic(api_key=self.api_key)
            self.is_real_api = True
            logger.info("Claude API клиент инициализирован с реальным ключом")
        else:
            self.client = None
            self.is_real_api = False
            logger.info("Claude API работает в тестовом режиме")
    
    async def analyze_football_match(self, betboom_data: Dict[str, Any], 
                                   scores24_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ футбольного матча"""
        
        if not self.is_real_api:
            return await self._mock_football_analysis(betboom_data, scores24_data)
        
        system_prompt = SYSTEM_PROMPTS["football"]
        
        user_prompt = f"""
АНАЛИЗ LIVE ФУТБОЛЬНОГО МАТЧА

🏟️ ОСНОВНЫЕ ДАННЫЕ:
Матч: {betboom_data.get('team1')} vs {betboom_data.get('team2')}
Счет: {betboom_data.get('score')} ({betboom_data.get('minute')}')
Лига: {betboom_data.get('league')}
Коэффициенты: 1={betboom_data.get('odds', {}).get('1')} X={betboom_data.get('odds', {}).get('X')} 2={betboom_data.get('odds', {}).get('2')}

📊 СТАТИСТИКА КОМАНД:
{betboom_data.get('team1')}:
- Позиция в таблице: {scores24_data.get('league_position1')}
- Форма (последние 5): {scores24_data.get('form1')}
- Голы за 5 матчей: {scores24_data.get('recent_goals1')}

{betboom_data.get('team2')}:
- Позиция в таблице: {scores24_data.get('league_position2')}  
- Форма (последние 5): {scores24_data.get('form2')}
- Голы за 5 матчей: {scores24_data.get('recent_goals2')}

🎯 ЗАДАЧА: Определи вероятность победы ведущей команды. Рекомендуй ставку только при уверенности >80%.

Ответь СТРОГО в JSON:
{{
    "confidence": число_от_0_до_100,
    "is_favorite_leading": true/false,
    "reasoning": "обоснование_до_80_символов",
    "recommendation": "bet"/"skip"
}}
"""
        
        return await self._make_api_request(system_prompt, user_prompt)
    
    async def analyze_tennis_match(self, betboom_data: Dict[str, Any], 
                                 scores24_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ теннисного матча"""
        
        if not self.is_real_api:
            return await self._mock_tennis_analysis(betboom_data, scores24_data)
        
        system_prompt = SYSTEM_PROMPTS["tennis"]
        
        user_prompt = f"""
АНАЛИЗ LIVE ТЕННИСНОГО МАТЧА

🎾 ДАННЫЕ:
{betboom_data.get('player1')} vs {betboom_data.get('player2')}
Счет: {betboom_data.get('sets_score')} | {betboom_data.get('games_score')}
Турнир: {betboom_data.get('tournament')}

📊 СТАТИСТИКА:
Рейтинги: {scores24_data.get('ranking1')} vs {scores24_data.get('ranking2')}
Форма: {scores24_data.get('form1')} vs {scores24_data.get('form2')}
Очные встречи: {scores24_data.get('head_to_head')}

🎯 ЗАДАЧА: Оцени шансы ведущего игрока на победу.

Ответь в JSON:
{{
    "confidence": число_от_0_до_100,
    "is_favorite_leading": true/false,
    "reasoning": "обоснование_до_80_символов",
    "recommendation": "bet"/"skip"
}}
"""
        
        return await self._make_api_request(system_prompt, user_prompt)
    
    async def analyze_handball_total(self, betboom_data: Dict[str, Any], 
                                   scores24_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ тотала в гандболе"""
        
        if not self.is_real_api:
            return await self._mock_handball_total(betboom_data, scores24_data)
        
        system_prompt = SYSTEM_PROMPTS["handball"]
        
        total_goals = betboom_data.get('total_goals', 0)
        minutes = betboom_data.get('minutes_played', 60)
        predicted_total = betboom_data.get('predicted_total', 60)
        
        user_prompt = f"""
АНАЛИЗ ТОТАЛА В ГАНДБОЛЕ

🤾 МАТЧ: {betboom_data.get('team1')} vs {betboom_data.get('team2')}
Счет: {betboom_data.get('score')} ({betboom_data.get('minute')}')
Голов: {total_goals}, Минут: {minutes}

📈 РАСЧЕТ: ПТ = {predicted_total}
ТМ = {predicted_total + 4}, ТБ = {predicted_total - 4}

📊 СТАТИСТИКА:
Результативность: {scores24_data.get('avg_goals_per_match1')} vs {scores24_data.get('avg_goals_per_match2')}

🎯 ЗАДАЧА: Определи темп и рекомендуй тотал.

Ответь в JSON:
{{
    "confidence": число_от_0_до_100,
    "pace": "БЫСТРЫЙ"/"МЕДЛЕННЫЙ",
    "recommendation": "ТБ_{predicted_total - 4}"/"ТМ_{predicted_total + 4}",
    "reasoning": "обоснование",
    "bet_type": "total"
}}
"""
        
        return await self._make_api_request(system_prompt, user_prompt)
    
    async def _make_api_request(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Выполняет запрос к Claude API"""
        
        try:
            # Используем официальную библиотеку Anthropic
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ]
                )
            )
            
            # Извлекаем текст ответа
            content = response.content[0].text
            
            # Парсим JSON
            try:
                # Ищем JSON в ответе
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    result = json.loads(json_content)
                    
                    logger.info(f"✅ Claude анализ выполнен, уверенность: {result.get('confidence', 0)}%")
                    return result
                else:
                    logger.error("JSON не найден в ответе Claude")
                    return self._get_error_response()
                    
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON: {e}")
                logger.debug(f"Ответ Claude: {content}")
                return self._get_error_response()
                
        except Exception as e:
            logger.error(f"Ошибка запроса к Claude API: {e}")
            return self._get_error_response()
    
    # Заглушки для тестового режима
    async def _mock_football_analysis(self, betboom_data: Dict[str, Any], 
                                    scores24_data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        return {
            "confidence": 85,
            "is_favorite_leading": True,
            "reasoning": "Лидер таблицы ведет дома, отличная форма",
            "recommendation": "bet"
        }
    
    async def _mock_tennis_analysis(self, betboom_data: Dict[str, Any], 
                                  scores24_data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        return {
            "confidence": 88,
            "is_favorite_leading": True,
            "reasoning": "Выиграл сет, выше в рейтинге, хорошая форма",
            "recommendation": "bet"
        }
    
    async def _mock_handball_total(self, betboom_data: Dict[str, Any], 
                                 scores24_data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        predicted_total = betboom_data.get('predicted_total', 60)
        return {
            "confidence": 82,
            "pace": "БЫСТРЫЙ",
            "recommendation": f"ТБ_{predicted_total - 4}",
            "reasoning": "Высокий темп, атакующие команды",
            "bet_type": "total"
        }
    
    def _get_error_response(self) -> Dict[str, Any]:
        """Стандартный ответ при ошибке"""
        return {
            "confidence": 0,
            "reasoning": "Ошибка Claude API",
            "recommendation": "skip"
        }