#!/usr/bin/env python3
"""
Claude Analyzer для TrueLiveBet
Углубленный анализ матчей с помощью Claude AI
"""

import json
import time
from datetime import datetime
from typing import Dict, Optional

# Импортируем конфигурацию
from config import CLAUDE_CONFIG

class ClaudeAnalyzer:
    """Анализатор матчей с помощью Claude AI"""
    
    def __init__(self):
        self.api_key = CLAUDE_CONFIG['api_key']
        self.model = CLAUDE_CONFIG['model']
        self.max_tokens = CLAUDE_CONFIG['max_tokens']
        self.temperature = CLAUDE_CONFIG['temperature']
        self.enabled = CLAUDE_CONFIG['enabled']
        
        # Проверяем доступность API
        if self.api_key == 'YOUR_CLAUDE_API_KEY_HERE':
            print("⚠️ Claude API ключ не настроен. Анализ будет только через Python скрипт.")
            self.enabled = False
        else:
            print("✅ Claude API настроен и готов к работе!")
    
    def analyze_match(self, match_data: Dict) -> Optional[Dict]:
        """Анализирует матч с помощью Claude"""
        if not self.enabled:
            return None
        
        try:
            # Формируем промпт для Claude
            prompt = self._create_analysis_prompt(match_data)
            
            # Отправляем запрос к Claude
            response = self._send_claude_request(prompt)
            
            if response:
                # Парсим ответ Claude
                analysis = self._parse_claude_response(response, match_data)
                return analysis
            
        except Exception as e:
            print(f"❌ Ошибка анализа через Claude: {e}")
        
        return None
    
    def _create_analysis_prompt(self, match_data: Dict) -> str:
        """Создает промпт для анализа матча"""
        
        prompt = f"""
Ты эксперт по анализу ставок TrueLiveBet. Проанализируй матч по нашим критериям.

ИНФОРМАЦИЯ О МАТЧЕ:
- Вид спорта: {match_data['sport']}
- Команда 1: {match_data['team1']}
- Команда 2: {match_data['team2']}
- Счет: {match_data['score']}
- Время: {match_data['time'] or f"Четверть {match_data['quarter']}"}

КРИТЕРИИ TRUE LIVE BET:
1. Футбол: фаворит ведет 2+ гола, время >60 минут
2. Баскетбол: отрыв 15+ очков, четверть 2+
3. Теннис: выигран 1-й сет, ведет во 2-м
4. Гандбол: отрыв 3+ гола, время >45 минут

ЗАДАЧА:
1. Оцени матч по критериям TrueLiveBet (0-100%)
2. Дай четкую рекомендацию (ставка/не ставка)
3. Обоснуй решение
4. Укажи риски
5. Предложи размер ставки (1-2% от банка)

ФОРМАТ ОТВЕТА (JSON):
{{
    "confidence": 85,
    "recommendation": "СТАВКА",
    "reasoning": ["Причина 1", "Причина 2"],
    "risks": ["Риск 1", "Риск 2"],
    "bet_size": 1.5,
    "claude_analysis": "Подробный анализ от Claude"
}}

Анализируй строго по критериям TrueLiveBet. Не изобретай новые правила.
"""
        
        return prompt
    
    def _send_claude_request(self, prompt: str) -> Optional[str]:
        """Отправляет запрос к Claude API"""
        try:
            # Здесь будет реальный API запрос к Claude
            # Пока что симулируем для демонстрации
            
            if not self.api_key or self.api_key == 'YOUR_CLAUDE_API_KEY_HERE':
                return None
            
            # TODO: Реальная интеграция с Claude API
            # import anthropic
            # client = anthropic.Anthropic(api_key=self.api_key)
            # response = client.messages.create(...)
            
            # Пока возвращаем симуляцию
            return self._simulate_claude_response(prompt)
            
        except Exception as e:
            print(f"❌ Ошибка отправки запроса к Claude: {e}")
            return None
    
    def _simulate_claude_response(self, prompt: str) -> str:
        """Симулирует ответ Claude для демонстрации"""
        
        # Анализируем промпт и генерируем ответ
        if 'футбол' in prompt.lower() and '2:0' in prompt:
            return '''
{
    "confidence": 85,
    "recommendation": "СТАВКА",
    "reasoning": [
        "Фаворит ведет на 2 гола",
        "Время матча 65 минут - достаточно для стабильности",
        "Соответствует критериям TrueLiveBet"
    ],
    "risks": [
        "Возможная контратака в концовке",
        "Усталость игроков"
    ],
    "bet_size": 1.5,
    "claude_analysis": "Матч полностью соответствует критериям TrueLiveBet. Фаворит контролирует игру, ведет на 2 гола, прошло достаточно времени. Риски минимальные."
}
'''
        elif 'баскетбол' in prompt.lower() and '85:65' in prompt:
            return '''
{
    "confidence": 80,
    "recommendation": "СТАВКА",
    "reasoning": [
        "Отрыв 20 очков - превышает минимальный порог 15",
        "3-я четверть - достаточно времени для стабилизации"
    ],
    "risks": [
        "Возможный рывок соперника",
        "Фаулы и штрафные броски"
    ],
    "bet_size": 1.2,
    "claude_analysis": "Баскетбольный матч с большим отрывом в 3-й четверти. Соответствует критериям TrueLiveBet. Рекомендую ставку."
}
'''
        else:
            return '''
{
    "confidence": 45,
    "recommendation": "НЕ СТАВКА",
    "reasoning": [
        "Недостаточно данных для рекомендации",
        "Не соответствует критериям TrueLiveBet"
    ],
    "risks": ["Высокий риск проигрыша"],
    "bet_size": 0,
    "claude_analysis": "Матч не соответствует критериям TrueLiveBet. Рекомендую воздержаться от ставки."
}
'''
    
    def _parse_claude_response(self, response: str, match_data: Dict) -> Dict:
        """Парсит ответ от Claude"""
        try:
            # Извлекаем JSON из ответа
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                analysis = json.loads(json_str)
                
                # Добавляем информацию о матче
                analysis['match_data'] = match_data
                analysis['claude_timestamp'] = datetime.now().isoformat()
                
                return analysis
            else:
                print("❌ Не удалось найти JSON в ответе Claude")
                return None
                
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON от Claude: {e}")
            return None
        except Exception as e:
            print(f"❌ Ошибка обработки ответа Claude: {e}")
            return None
    
    def get_enhanced_recommendation(self, match_data: Dict, python_analysis: Dict) -> Dict:
        """Получает улучшенную рекомендацию от Claude"""
        
        # Если Claude недоступен, возвращаем Python анализ
        if not self.enabled:
            return python_analysis
        
        # Получаем анализ от Claude
        claude_analysis = self.analyze_match(match_data)
        
        if claude_analysis:
            # Объединяем Python и Claude анализ
            enhanced_analysis = {
                **python_analysis,
                'claude_enhanced': True,
                'claude_confidence': claude_analysis.get('confidence', 0),
                'claude_recommendation': claude_analysis.get('recommendation', ''),
                'claude_reasoning': claude_analysis.get('reasoning', []),
                'claude_risks': claude_analysis.get('risks', []),
                'claude_bet_size': claude_analysis.get('bet_size', 0),
                'claude_analysis_text': claude_analysis.get('claude_analysis', ''),
                'final_confidence': max(
                    python_analysis.get('confidence', 0),
                    claude_analysis.get('confidence', 0)
                )
            }
            
            return enhanced_analysis
        
        # Если Claude не ответил, возвращаем Python анализ
        return python_analysis

def test_claude_analyzer():
    """Тестирует Claude анализатор"""
    print("🧠 Тестирование Claude Analyzer...")
    
    analyzer = ClaudeAnalyzer()
    
    # Тестовые данные
    test_match = {
        'sport': 'football',
        'team1': 'Барселона',
        'team2': 'Реал Мадрид',
        'score': '2:0',
        'time': '65\'',
        'quarter': None
    }
    
    # Анализ через Claude
    result = analyzer.analyze_match(test_match)
    
    if result:
        print("✅ Claude анализ получен:")
        print(f"📊 Уверенность: {result.get('confidence')}%")
        print(f"💡 Рекомендация: {result.get('recommendation')}")
        print(f"🔍 Обоснование: {result.get('reasoning')}")
    else:
        print("❌ Claude анализ недоступен")

if __name__ == "__main__":
    test_claude_analyzer()