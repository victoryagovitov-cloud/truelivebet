#!/usr/bin/env python3
"""
TrueLiveBet - AI анализатор матчей
Автор: Виктор
"""

import asyncio
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from loguru import logger
from datetime import datetime

@dataclass
class AnalysisResult:
    """Результат AI анализа"""
    match_id: str
    confidence: float  # Уверенность в процентах
    recommendation: str  # Рекомендация
    reasoning: str  # Обоснование
    risk_level: str  # Уровень риска
    category: str  # Категория (💀🎯⭐👍)
    timestamp: str

class AIAnalyzer:
    """AI анализатор для матчей"""
    
    def __init__(self, openai_api_key: str = None, anthropic_api_key: str = None):
        self.openai_client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
        self.anthropic_client = AsyncAnthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        
        # Система анализа TrueLiveBet
        self.analysis_system = """
        Ты - эксперт по анализу лайв-ставок TrueLiveBet. Анализируй матчи по нашим правилам:

        🏆 СТРОГИЙ АНАЛИЗ (обязательно):
        - НИКОГДА не рекомендовать матч БЕЗ поиска реальной статистики!
        - Алгоритм: Счет → Поиск статистики → Чек-лист → Справка → Категория

        🎯 КАТЕГОРИИ:
        - 💀 >95% - Мертвые (требуют строгого анализа)
        - 🎯 85–95% - Идеальные
        - ⭐ 80–85% - Отличные  
        - 👍 75–80% - Хорошие

        ⚽ ФУТБОЛ:
        - ОТКРЫТ неничейный счет?
        - Фаворит уверенно ведет?
        - Справка об ОБЕИХ командах?

        🎾 ТЕННИС:
        - Выиграл 1-й сет?
        - ВЕДЕТ во 2-м?
        - Фаворит по ATP/WTA?
        - >80%?

        🏀 БАСКЕТБОЛ:
        - СУЩЕСТВЕННОЕ преимущество (15+ очков) в ЛЮБОЙ четверти?
        - Фаворит по уровню?

        🤾 ГАНДБОЛ:
        - Неничейный результат?
        - Анализ уровня ОБЕИХ команд?
        - Расчет времени vs средняя результативность?

        ВАЖНО: Всегда давай конкретные рекомендации с обоснованием!
        """
    
    async def analyze_match(self, match_data: Dict, additional_stats: Dict = None) -> AnalysisResult:
        """Анализ матча с помощью AI"""
        
        try:
            # Формируем промпт для анализа
            prompt = self._create_analysis_prompt(match_data, additional_stats)
            
            # Выбираем AI модель
            if self.anthropic_client:
                result = await self._analyze_with_anthropic(prompt)
            elif self.openai_client:
                result = await self._analyze_with_openai(prompt)
            else:
                # Fallback анализ без AI
                result = await self._fallback_analysis(match_data, additional_stats)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка AI анализа: {e}")
            return await self._fallback_analysis(match_data, additional_stats)
    
    def _create_analysis_prompt(self, match_data: Dict, additional_stats: Dict = None) -> str:
        """Создание промпта для AI анализа"""
        
        prompt = f"""
        {self.analysis_system}

        АНАЛИЗ МАТЧА:
        Вид спорта: {match_data.get('sport', 'Неизвестно')}
        Лига: {match_data.get('league', 'Неизвестно')}
        Команда 1: {match_data.get('team1', 'Неизвестно')}
        Команда 2: {match_data.get('team2', 'Неизвестно')}
        Счет: {match_data.get('score', '0:0')}
        Время: {match_data.get('time', '0\'')}
        Статус: {match_data.get('status', 'live')}
        Коэффициенты: {json.dumps(match_data.get('odds', {}), ensure_ascii=False)}
        """
        
        if additional_stats:
            prompt += f"\n\nДОПОЛНИТЕЛЬНАЯ СТАТИСТИКА:\n{json.dumps(additional_stats, ensure_ascii=False, indent=2)}"
        
        prompt += """

        ЗАДАЧА: Проанализируй этот матч по нашим правилам и дай рекомендацию.

        ОТВЕТ В ФОРМАТЕ JSON:
        {
            "confidence": 85.5,
            "recommendation": "Ставить на победу команды 1",
            "reasoning": "Команда 1 ведет 2:0, контроль мяча 65%, удары 8:2",
            "risk_level": "средний",
            "category": "🎯"
        }
        """
        
        return prompt
    
    async def _analyze_with_anthropic(self, prompt: str) -> AnalysisResult:
        """Анализ с помощью Anthropic Claude"""
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            return self._parse_ai_response(content)
            
        except Exception as e:
            logger.error(f"Ошибка Anthropic API: {e}")
            raise
    
    async def _analyze_with_openai(self, prompt: str) -> AnalysisResult:
        """Анализ с помощью OpenAI GPT"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": self.analysis_system},
                         {"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            return self._parse_ai_response(content)
            
        except Exception as e:
            logger.error(f"Ошибка OpenAI API: {e}")
            raise
    
    def _parse_ai_response(self, content: str) -> AnalysisResult:
        """Парсинг ответа AI"""
        try:
            # Ищем JSON в ответе
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                data = json.loads(json_str)
                
                return AnalysisResult(
                    match_id=f"{data.get('team1', '')}_{data.get('team2', '')}",
                    confidence=float(data.get('confidence', 75.0)),
                    recommendation=data.get('recommendation', 'Анализ не завершен'),
                    reasoning=data.get('reasoning', 'Недостаточно данных'),
                    risk_level=data.get('risk_level', 'высокий'),
                    category=data.get('category', '👍'),
                    timestamp=datetime.now().isoformat()
                )
        except Exception as e:
            logger.warning(f"Ошибка парсинга AI ответа: {e}")
        
        # Fallback если парсинг не удался
        return AnalysisResult(
            match_id="unknown",
            confidence=50.0,
            recommendation="Требуется дополнительный анализ",
            reasoning="AI анализ не завершен",
            risk_level="высокий",
            category="👍",
            timestamp=datetime.now().isoformat()
        )
    
    async def _fallback_analysis(self, match_data: Dict, additional_stats: Dict = None) -> AnalysisResult:
        """Fallback анализ без AI"""
        
        # Простая логика анализа
        confidence = 50.0
        category = "👍"
        risk_level = "высокий"
        
        # Анализируем счет
        score = match_data.get('score', '0:0')
        if ':' in score:
            home_score, away_score = map(int, score.split(':'))
            if home_score > away_score:
                confidence = 70.0
                category = "⭐"
                risk_level = "средний"
            elif away_score > home_score:
                confidence = 70.0
                category = "⭐"
                risk_level = "средний"
        
        return AnalysisResult(
            match_id=f"{match_data.get('team1', '')}_{match_data.get('team2', '')}",
            confidence=confidence,
            recommendation="Требуется дополнительный анализ статистики",
            reasoning="Fallback анализ - недостаточно данных для точной оценки",
            risk_level=risk_level,
            category=category,
            timestamp=datetime.now().isoformat()
        )
    
    async def batch_analyze(self, matches: List[Dict], additional_stats: Dict = None) -> List[AnalysisResult]:
        """Пакетный анализ нескольких матчей"""
        results = []
        
        for match in matches:
            try:
                result = await self.analyze_match(match, additional_stats)
                results.append(result)
                
                # Небольшая задержка между запросами
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Ошибка анализа матча {match.get('team1', '')} vs {match.get('team2', '')}: {e}")
                continue
        
        return results

# Пример использования
async def test_analyzer():
    """Тестирование анализатора"""
    analyzer = AIAnalyzer()
    
    test_match = {
        'sport': 'Футбол',
        'league': 'Премьер-лига',
        'team1': 'Манчестер Юнайтед',
        'team2': 'Ливерпуль',
        'score': '2:0',
        'time': '75\'',
        'odds': {'1': 1.5, 'X': 4.2, '2': 6.8},
        'status': 'live'
    }
    
    result = await analyzer.analyze_match(test_match)
    print(f"Результат анализа: {result}")

if __name__ == "__main__":
    asyncio.run(test_analyzer())
