"""
Продвинутый анализатор спортивных событий с использованием Claude AI
Включает специализированные промпты и контекстный анализ
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime

from config.claude_config import CLAUDE_CONFIG, SYSTEM_PROMPTS, CONFIDENCE_THRESHOLDS

logger = logging.getLogger(__name__)


class AdvancedClaudeAnalyzer:
    """Продвинутый анализатор с использованием Claude AI"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or CLAUDE_CONFIG.get("api_key", "YOUR_CLAUDE_API_KEY")
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = CLAUDE_CONFIG.get("model", "claude-3-5-sonnet-20241022")
        
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
    
    async def analyze_football_match(self, betboom_data: Dict[str, Any], 
                                   scores24_data: Dict[str, Any]) -> Dict[str, Any]:
        """Глубокий анализ футбольного матча"""
        
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

Уровень лиги: {scores24_data.get('league_level')}

🎯 ЗАДАЧИ АНАЛИЗА:
1. Определи истинного фаворита матча на основе всех данных
2. Оцени, ведет ли сейчас фаворит в счете
3. Спрогнозируй вероятность победы ведущей команды
4. Учти влияние времени матча на исход
5. Дай рекомендацию по ставке

⚠️ КРИТЕРИИ РЕКОМЕНДАЦИИ:
- Рекомендуй ставку только при уверенности >80%
- Учитывай что поздние голы (60+ минута) критичнее
- Анализируй не только текущий счет, но и общую картину
- Будь консервативен - лучше пропустить сомнительный матч

Ответь в JSON формате:
{{
    "confidence": число_от_0_до_100,
    "is_favorite_leading": true/false,
    "favorite_team": "название_команды_фаворита",
    "reasoning": "обоснование_до_80_символов",
    "recommendation": "bet"/"skip",
    "detailed_analysis": {{
        "form_analysis": "анализ_формы_команд",
        "position_analysis": "анализ_позиций_в_таблице", 
        "time_factor": "влияние_времени_матча",
        "key_factors": ["ключевой_фактор_1", "ключевой_фактор_2"]
    }}
}}
"""
        
        return await self._make_claude_request(system_prompt, user_prompt)
    
    async def analyze_tennis_match(self, betboom_data: Dict[str, Any], 
                                 scores24_data: Dict[str, Any]) -> Dict[str, Any]:
        """Глубокий анализ теннисного матча"""
        
        system_prompt = SYSTEM_PROMPTS["tennis"]
        
        user_prompt = f"""
АНАЛИЗ LIVE ТЕННИСНОГО МАТЧА

🎾 ОСНОВНЫЕ ДАННЫЕ:
Матч: {betboom_data.get('player1')} vs {betboom_data.get('player2')}
Счет по сетам: {betboom_data.get('sets_score')}
Счет в геймах: {betboom_data.get('games_score')}
Турнир: {betboom_data.get('tournament')}
Коэффициенты: 1={betboom_data.get('odds', {}).get('1')} 2={betboom_data.get('odds', {}).get('2')}

📊 СТАТИСТИКА ИГРОКОВ:
{betboom_data.get('player1')}:
- Рейтинг: {scores24_data.get('ranking1')}
- Форма: {scores24_data.get('form1')}
- Предпочтение покрытия: {scores24_data.get('surface_preference1')}

{betboom_data.get('player2')}:
- Рейтинг: {scores24_data.get('ranking2')}
- Форма: {scores24_data.get('form2')}
- Предпочтение покрытия: {scores24_data.get('surface_preference2')}

Очные встречи: {scores24_data.get('head_to_head')} (побед первого-второго)

🎯 ЗАДАЧИ АНАЛИЗА:
1. Определи кто является фаворитом по рейтингу и форме
2. Оцени психологическое преимущество (выигрыш сета/большой разрыв)
3. Учти влияние очных встреч и покрытия
4. Спрогнозируй вероятность победы ведущего игрока

⚠️ ОСОБЕННОСТИ ТЕННИСА:
- Выигрыш первого сета дает 60-70% шанс на победу
- Разрыв в 4+ гейма в сете критичен
- Рейтинг топ-10 vs топ-50 = существенная разница
- Форма важнее рейтинга для текущего матча

Ответь в JSON формате:
{{
    "confidence": число_от_0_до_100,
    "is_favorite_leading": true/false,
    "favorite_player": "имя_игрока_фаворита",
    "reasoning": "обоснование_до_80_символов",
    "recommendation": "bet"/"skip",
    "detailed_analysis": {{
        "ranking_advantage": "анализ_рейтингового_преимущества",
        "form_analysis": "анализ_текущей_формы",
        "psychological_factor": "психологические_факторы",
        "match_dynamics": "динамика_матча"
    }}
}}
"""
        
        return await self._make_claude_request(system_prompt, user_prompt)
    
    async def analyze_handball_with_context(self, betboom_data: Dict[str, Any], 
                                          scores24_data: Dict[str, Any]) -> Dict[str, Any]:
        """Контекстный анализ гандбольного матча"""
        
        analysis_type = betboom_data.get('analysis_type', 'victory')
        system_prompt = SYSTEM_PROMPTS["handball"]
        
        if analysis_type == 'total':
            # Специальный промпт для анализа тоталов
            user_prompt = f"""
АНАЛИЗ ТОТАЛА В LIVE ГАНДБОЛЬНОМ МАТЧЕ

🤾 ДАННЫЕ МАТЧА:
{betboom_data.get('team1')} vs {betboom_data.get('team2')}
Счет: {betboom_data.get('score')} ({betboom_data.get('minute')}' - 2й тайм)
Всего голов: {betboom_data.get('total_goals')}
Сыграно минут: {betboom_data.get('minutes_played')}

📈 РАСЧЕТ ПО ФОРМУЛЕ:
Прогнозный тотал = ({betboom_data.get('total_goals')} / {betboom_data.get('minutes_played')}) × 60 = {betboom_data.get('predicted_total')}
ТМ (тотал меньше) = {betboom_data.get('predicted_total', 60) + 4}
ТБ (тотал больше) = {betboom_data.get('predicted_total', 60) - 4}

📊 СТАТИСТИКА КОМАНД:
Средняя результативность: {scores24_data.get('avg_goals_per_match1')} vs {scores24_data.get('avg_goals_per_match2')}
Форма команд: {scores24_data.get('form1')} vs {scores24_data.get('form2')}

🧮 ЛОГИКА ТЕМПА:
Текущий темп: {betboom_data.get('total_goals')} голов за {betboom_data.get('minutes_played')} минут
- Если голов < минут → МЕДЛЕННЫЙ темп → ТМ
- Если голов > минут → БЫСТРЫЙ темп → ТБ

🎯 ЗАДАЧИ:
1. Оцени будет ли текущий темп сохраняться
2. Учти усталость игроков и тактику команд
3. Проанализируй результативность команд
4. Дай точную рекомендацию по тоталу

Ответь в JSON:
{{
    "confidence": число_от_0_до_100,
    "pace": "БЫСТРЫЙ"/"МЕДЛЕННЫЙ"/"НЕЙТРАЛЬНЫЙ",
    "recommendation": "ТБ_{betboom_data.get('predicted_total', 60) - 4}"/"ТМ_{betboom_data.get('predicted_total', 60) + 4}",
    "reasoning": "обоснование_до_80_символов",
    "bet_type": "total",
    "predicted_total": {betboom_data.get('predicted_total', 60)},
    "analysis_details": "детальный_анализ_темпа_и_тенденций"
}}
"""
        else:
            # Промпт для анализа прямых побед
            user_prompt = f"""
АНАЛИЗ ПОБЕДЫ В LIVE ГАНДБОЛЬНОМ МАТЧЕ

🤾 ДАННЫЕ МАТЧА:
{betboom_data.get('team1')} vs {betboom_data.get('team2')}
Счет: {betboom_data.get('score')} ({betboom_data.get('minute')}' - 2й тайм)
Разрыв в счете: {abs(int(betboom_data.get('score', '0:0').split(':')[0]) - int(betboom_data.get('score', '0:0').split(':')[1]))} голов

📊 СТАТИСТИКА:
Позиции в таблице: {scores24_data.get('league_position1')} vs {scores24_data.get('league_position2')}
Форма команд: {scores24_data.get('form1')} vs {scores24_data.get('form2')}
Средняя результативность: {scores24_data.get('avg_goals_per_match1')} vs {scores24_data.get('avg_goals_per_match2')}

🎯 ОСОБЕННОСТИ ГАНДБОЛА:
- Разрыв 5+ голов обычно критичен
- Во втором тайме сложнее отыгрываться
- Усталость влияет на точность бросков
- Тактические фолы замедляют игру отстающей команды

ЗАДАЧИ:
1. Оцени вероятность удержания преимущества
2. Учти время матча и психологический фактор
3. Проанализируй способность отстающей команды к comeback'у
4. Дай точную оценку уверенности

Ответь в JSON:
{{
    "confidence": число_от_0_до_100,
    "is_favorite_leading": true/false,
    "favorite_team": "название_фаворита",
    "reasoning": "обоснование_до_80_символов",
    "recommendation": "bet"/"skip",
    "comeback_probability": число_от_0_до_100,
    "analysis_details": "детальный_анализ_шансов_на_comeback"
}}
"""
        
        return await self._make_claude_request(system_prompt, user_prompt)
    
    async def get_match_context_analysis(self, sport: str, all_matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Получает контекстный анализ всех матчей для лучшего понимания"""
        
        context_prompt = f"""
Ты анализируешь live {sport} матчи. Вот все доступные матчи:

{json.dumps(all_matches, ensure_ascii=False, indent=2)}

Проанализируй общую картину:
1. Какие лиги/турниры сейчас идут?
2. Есть ли явные фавориты среди матчей?
3. Какие матчи выглядят наиболее предсказуемыми?
4. На что стоит обратить особое внимание?

Ответь кратким анализом ситуации (до 200 слов).
"""
        
        return await self._make_claude_request("", context_prompt)
    
    async def validate_recommendation(self, sport: str, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Дополнительная валидация рекомендации через Claude"""
        
        validation_prompt = f"""
ВАЛИДАЦИЯ РЕКОМЕНДАЦИИ ПО СТАВКЕ

Вид спорта: {sport}
Рекомендация: {json.dumps(recommendation, ensure_ascii=False, indent=2)}

Проверь рекомендацию на:
1. Логичность обоснования
2. Соответствие уверенности фактам
3. Учет рисков
4. Качество анализа

Если находишь серьезные недочеты, скорректируй уверенность в меньшую сторону.

Ответь в JSON:
{{
    "is_valid": true/false,
    "corrected_confidence": число_от_0_до_100,
    "validation_notes": "замечания_по_анализу",
    "final_recommendation": "bet"/"skip"
}}
"""
        
        return await self._make_claude_request("", validation_prompt)
    
    async def _make_claude_request(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Выполняет запрос к Claude API с системным промптом"""
        
        # В тестовом режиме возвращаем умную заглушку
        if self.api_key == "YOUR_CLAUDE_API_KEY":
            logger.info("ТЕСТОВЫЙ РЕЖИМ Claude - генерируем умную заглушку")
            return await self._generate_smart_mock(user_prompt)
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user", 
                "content": user_prompt
            })
            
            payload = {
                "model": self.model,
                "max_tokens": CLAUDE_CONFIG.get("max_tokens", 1000),
                "temperature": CLAUDE_CONFIG.get("temperature", 0.1),
                "messages": messages
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
                
                # Извлекаем JSON из ответа
                try:
                    # Ищем JSON в ответе
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    
                    if json_start != -1 and json_end > json_start:
                        json_content = content[json_start:json_end]
                        analysis_result = json.loads(json_content)
                        
                        logger.info(f"Claude анализ выполнен, уверенность: {analysis_result.get('confidence', 0)}%")
                        return analysis_result
                    else:
                        logger.error("JSON не найден в ответе Claude")
                        return self._get_error_response()
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Ошибка парсинга JSON: {e}")
                    logger.debug(f"Содержимое ответа: {content}")
                    return self._get_error_response()
            else:
                logger.error(f"Ошибка Claude API: {response.status_code}")
                return self._get_error_response()
                
        except Exception as e:
            logger.error(f"Исключение при запросе к Claude: {e}")
            return self._get_error_response()
    
    async def _generate_smart_mock(self, prompt: str) -> Dict[str, Any]:
        """Генерирует умную заглушку на основе промпта"""
        await asyncio.sleep(0.8)  # Имитация времени обработки AI
        
        prompt_lower = prompt.lower()
        
        # Анализируем тип запроса
        if "футбол" in prompt_lower:
            # Извлекаем данные из промпта для умной заглушки
            confidence = 85 if "лидер таблицы" in prompt_lower else 82
            return {
                "confidence": confidence,
                "is_favorite_leading": True,
                "favorite_team": "Команда 1",
                "reasoning": "Статистическое преимущество, лучшая форма",
                "recommendation": "bet" if confidence >= 80 else "skip",
                "detailed_analysis": {
                    "form_analysis": "Команда показывает стабильные результаты",
                    "position_analysis": "Преимущество в турнирной таблице",
                    "time_factor": "Достаточно времени для контроля игры",
                    "key_factors": ["форма", "позиция", "домашнее поле"]
                }
            }
        
        elif "теннис" in prompt_lower and "настольный" not in prompt_lower:
            confidence = 88 if "1-0" in prompt_lower else 83
            return {
                "confidence": confidence,
                "is_favorite_leading": True,
                "favorite_player": "Игрок 1",
                "reasoning": "Рейтинговое преимущество, выиграл сет",
                "recommendation": "bet" if confidence >= 80 else "skip",
                "detailed_analysis": {
                    "ranking_advantage": "Существенная разница в рейтинге",
                    "form_analysis": "Стабильная игра в последних турнирах",
                    "psychological_factor": "Преимущество после выигрыша сета",
                    "match_dynamics": "Контролирует темп игры"
                }
            }
        
        elif "настольный" in prompt_lower:
            confidence = 90 if "2-0" in prompt_lower else 85
            return {
                "confidence": confidence,
                "is_favorite_leading": True,
                "favorite_player": "Игрок 1", 
                "reasoning": "Преимущество в сетах, топ рейтинг",
                "recommendation": "bet" if confidence >= 80 else "skip",
                "detailed_analysis": {
                    "ranking_advantage": "Топ рейтинг ITTF",
                    "form_analysis": "Отличная текущая форма",
                    "psychological_factor": "Уверенность после выигрыша сетов",
                    "match_dynamics": "Контролирует ритм игры"
                }
            }
        
        elif "гандбол" in prompt_lower:
            if "тотал" in prompt_lower:
                return {
                    "confidence": 82,
                    "pace": "БЫСТРЫЙ",
                    "recommendation": "ТБ_56",
                    "reasoning": "Высокий темп, атакующие команды",
                    "bet_type": "total",
                    "predicted_total": 60,
                    "analysis_details": "Команды играют в атакующем стиле, темп выше среднего"
                }
            else:
                return {
                    "confidence": 87,
                    "is_favorite_leading": True,
                    "favorite_team": "Команда 1",
                    "reasoning": "Большой разрыв, статистическое преимущество",
                    "recommendation": "bet",
                    "comeback_probability": 15,
                    "analysis_details": "Разрыв критичен для гандбола, время работает против отстающих"
                }
        
        return self._get_error_response()
    
    def _get_error_response(self) -> Dict[str, Any]:
        """Стандартный ответ при ошибке"""
        return {
            "confidence": 0,
            "is_favorite_leading": False,
            "reasoning": "Ошибка анализа Claude AI",
            "recommendation": "skip",
            "analysis_details": "Не удалось выполнить AI анализ"
        }