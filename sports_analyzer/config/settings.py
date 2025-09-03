"""
Конфигурация анализатора спортивных событий
"""

from typing import Dict, Any

# Основные настройки
ANALYSIS_CONFIG = {
    "cycle_minutes": 50,
    "confidence_threshold": 80,  # Минимальная вероятность победы фаворита
    "fuzzy_match_threshold": 70,  # Минимальный процент совпадения для fuzzy matching
}

# URL сайтов для анализа
BETTING_SITES = {
    "betboom": {
        "football": "https://betboom.ru/sport/football?type=live",
        "tennis": "https://betboom.ru/sport/tennis?type=live", 
        "table_tennis": "https://betboom.ru/sport/table-tennis?type=live",
        "handball": "https://betboom.ru/sport/handball?type=live"
    },
    "scores24": {
        "football": "https://scores24.live/ru/soccer?matchesFilter=live",
        "tennis": "https://scores24.live/ru/tennis?matchesFilter=live",
        "table_tennis": "https://scores24.live/ru/table-tennis?matchesFilter=live", 
        "handball": "https://scores24.live/ru/handball"
    }
}

# Критерии отбора матчей по видам спорта
SPORT_CRITERIA = {
    "football": {
        "score_condition": "non_draw",  # Не ничейный счет
        "min_confidence": 80,
        "analysis_factors": ["team_form", "league_position", "league_level"]
    },
    "tennis": {
        "score_conditions": [
            "first_set_won",  # Выиграл первый сет
            "first_set_lead_4plus"  # Ведет в первом сете с разрывом ≥4
        ],
        "min_confidence": 80,
        "analysis_factors": ["player_form", "ranking", "head_to_head"]
    },
    "table_tennis": {
        "score_conditions": ["sets_1_0", "sets_2_0"],  # 1:0 или 2:0 по сетам
        "min_confidence": 80,
        "analysis_factors": ["player_form", "ranking"]
    },
    "handball": {
        "victory_condition": "lead_5plus",  # Разрыв ≥5 голов
        "total_conditions": {
            "min_minute": 10,  # Анализ с 10-й минуты
            "max_minute": 45,  # До 45-й минуты
            "half": 2  # Только во втором тайме
        },
        "min_confidence": 80,
        "analysis_factors": ["team_form", "league_position", "avg_goals"]
    }
}

# Шаблоны для вывода результатов
OUTPUT_TEMPLATES = {
    "football": """<b>⚽ {team1} – {team2}</b>
🏟️ Счет: <b>{score}</b> ({minute}')
✅ Ставка: <b>П1</b>
📊 Кэф: <b>{odds}</b>
📌 <i>{reasoning}</i>""",
    
    "tennis": """<b>🎾 {player1} – {player2}</b>
🎯 Счет: <b>{sets_score}</b> ({games_score})
✅ Ставка: <b>Победа {winner}</b>
📊 Кэф: <b>{odds}</b>
📌 <i>{reasoning}</i>""",
    
    "table_tennis": """<b>🏓 {player1} – {player2}</b>
🎯 Счет: <b>{sets_score}</b>
✅ Ставка: <b>Победа {winner}</b>
📊 Кэф: <b>{odds}</b>
📌 <i>{reasoning}</i>""",
    
    "handball_victory": """<b>🤾 {team1} – {team2}</b>
🏟️ Счет: <b>{score}</b> ({minute}')
✅ Ставка: <b>П1</b>
📊 Кэф: <b>{odds}</b>
📌 <i>{reasoning}</i>""",
    
    "handball_total": """<b>🤾 {team1} – {team2}</b>
🏟️ Счет: <b>{score}</b> ({minute}')
📈 Прогнозный тотал: <b>{predicted_total}</b> голов
🎯 Рекомендация: <b>{recommendation}</b>
📌 <i>Основание: {pace_description} темп игры ({total_goals} голов за {minutes_played} минут)</i>"""
}

# Заголовок финального отчета
REPORT_HEADER = """<b>🎯 LIVE-ПРЕДЛОЖЕНИЯ НА </b>(<i>{time} МСК, {date}</i>)<b> 🎯</b>"""

REPORT_FOOTER = """<b>——————————————————</b>
<b>💎 TrueLiveBet – Мы всегда на Вашей стороне! 💎</b>"""

# Разделители для видов спорта
SPORT_SEPARATORS = {
    "football": """<b>—————————————</b>
<b>⚽ ФУТБОЛ ⚽</b>
<b>—————————————</b>""",
    
    "tennis": """<b>—————————————</b>
<b>🎾 ТЕННИС 🎾</b>
<b>—————————————</b>""",
    
    "table_tennis": """<b>—————————————</b>
<b>🏓 НАСТ. ТЕННИС 🏓</b>
<b>—————————————</b>""",
    
    "handball": """<b>—————————————</b>
<b>🤾 ГАНДБОЛ 🤾</b>
<b>—————————————</b>"""
}