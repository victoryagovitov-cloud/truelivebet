#!/usr/bin/env python3
"""
Конфигурация для TrueLiveBet
"""

# Telegram Bot настройки
TELEGRAM_CONFIG = {
    'bot_token': '7824400107:AAGZqPdS0E0N3HsYpD8TW9m8c-bapFd-RHk',  # Ваш токен
    'chat_id': '678873745',              # Ваш личный Chat ID
    'bot_username': 'TrueLiveBetBot'     # Имя вашего бота
}

# Настройки парсинга
PARSING_CONFIG = {
    'interval_minutes': 30,               # Периодичность парсинга (30 минут)
    'betboom_url': 'https://betboom.ru',  # URL BetBoom
    'max_matches_per_check': 50,          # Максимум матчей за одну проверку
    'timeout_seconds': 30                 # Таймаут для HTTP запросов
}

# Критерии анализа для разных видов спорта
ANALYSIS_CRITERIA = {
    'football': {
        'min_goal_difference': 2,         # Минимальная разница в голах
        'min_control_percentage': 60,     # Минимальный контроль мяча
        'min_time_elapsed': 60,           # Минимальное время матча (минуты)
        'confidence_threshold': 75        # Порог уверенности для уведомления
    },
    'tennis': {
        'min_set_difference': 1,          # Минимальная разница в сетах
        'min_games_in_set': 4,            # Минимальное количество геймов в сете
        'confidence_threshold': 70
    },
    'basketball': {
        'min_point_difference': 15,       # Минимальная разница в очках
        'min_quarter': 2,                 # Минимальный квартал для анализа
        'confidence_threshold': 70
    },
    'handball': {
        'min_goal_difference': 3,         # Минимальная разница в голах
        'min_time_elapsed': 45,           # Минимальное время матча
        'confidence_threshold': 75
    }
}

# Источники данных
DATA_SOURCES = {
    'betboom': {
        'live_url': 'https://betboom.ru/live',
        'api_url': 'https://betboom.ru/api/live',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    },
    'scores24': {
        'base_url': 'https://scores24.live',
        'search_url': 'https://scores24.live/search'
    },
    '4score': {
        'base_url': 'https://4score.ru',
        'search_url': 'https://4score.ru/search'
    }
}

# Логирование
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'truelivebet.log'
}

# База данных (простая JSON файл для начала)
DATABASE_CONFIG = {
    'file_path': 'data/matches_history.json',
    'backup_interval_hours': 24
}

# Уведомления
NOTIFICATION_CONFIG = {
    'telegram_enabled': True,
    'max_notifications_per_hour': 10,     # Максимум уведомлений в час
    'notification_cooldown_minutes': 5,   # Задержка между уведомлениями
    'include_match_url': True,            # Включать ссылку на матч
    'include_odds': True                  # Включать коэффициенты
}