"""
Конфигурация для Claude AI анализатора
"""

import os
from typing import Dict, Any

# Настройки Claude API
CLAUDE_CONFIG = {
    "api_key": os.getenv("CLAUDE_API_KEY", "DEMO_MODE"),  # Тестовый режим
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 1000,
    "temperature": 0.1,  # Низкая температура для точного анализа
    "timeout": 30
}

# Системные промпты для разных видов спорта
SYSTEM_PROMPTS = {
    "football": """Ты профессиональный аналитик футбольных матчей с 15-летним опытом. 
Твоя специализация - live анализ с фокусом на статистику команд, форму, позиции в таблице.
Ты консервативен в оценках и рекомендуешь ставки только при высокой уверенности (>80%).
Всегда учитываешь время матча - поздние голы критичнее ранних.""",
    
    "tennis": """Ты эксперт по теннису с глубоким пониманием психологии игры.
Специализируешься на анализе live матчей, учитываешь рейтинги ATP/WTA, форму, очные встречи.
Понимаешь важность выигрыша первого сета и критичность разрывов в геймах.
Консервативен в прогнозах, фокус на фаворитах.""",
    
    "table_tennis": """Ты специалист по настольному теннису с экспертизой в ITTF рейтингах.
Анализируешь быстро меняющуюся динамику игры, важность преимущества в сетах.
Учитываешь что в настольном теннисе инициатива может быстро переходить.
Фокус на стабильности игроков и их текущей форме.""",
    
    "handball": """Ты аналитик гандбольных матчей с пониманием темпа игры и тактики.
Специализируешься на анализе разрывов в счете и прогнозировании тоталов.
Понимаешь математику гандбола: важность разрывов, влияние времени на результат.
Эксперт в анализе темпа игры для прогнозирования тоталов."""
}

# Критерии уверенности для разных видов спорта
CONFIDENCE_THRESHOLDS = {
    "football": {
        "min_confidence": 80,
        "excellent_confidence": 90,
        "factors": ["team_form", "league_position", "goal_difference", "match_time"]
    },
    "tennis": {
        "min_confidence": 80,
        "excellent_confidence": 88,
        "factors": ["ranking_difference", "set_advantage", "form", "head_to_head"]
    },
    "table_tennis": {
        "min_confidence": 80,
        "excellent_confidence": 90,
        "factors": ["ranking_difference", "sets_advantage", "form", "performance"]
    },
    "handball": {
        "min_confidence": 80,
        "excellent_confidence": 85,
        "factors": ["goal_difference", "match_time", "team_form", "pace_analysis"]
    }
}

# Шаблоны промптов для быстрого анализа
QUICK_ANALYSIS_PROMPTS = {
    "favorite_check": """
На основе данных определи кто является фаворитом в этом матче:
{match_data}

Ответь одним словом: "team1", "team2" или "equal"
""",
    
    "confidence_check": """
Оцени уверенность в победе команды/игрока {leader} в данной ситуации:
{situation_data}

Ответь числом от 0 до 100.
""",
    
    "pace_analysis": """
Проанализируй темп гандбольного матча:
Голов: {goals}, Минут: {minutes}
Средняя результативность команд: {avg_goals}

Ответь: "БЫСТРЫЙ", "МЕДЛЕННЫЙ" или "НЕЙТРАЛЬНЫЙ"
"""
}

# Настройки для обработки ответов Claude
RESPONSE_PROCESSING = {
    "max_retries": 3,
    "retry_delay": 1,  # секунды
    "fallback_confidence": 50,
    "json_validation": True,
    "required_fields": ["confidence", "recommendation", "reasoning"]
}