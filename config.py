#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурация для TrueLiveBet Bot
"""

# Telegram Bot настройки
TELEGRAM_CONFIG = {
    'bot_token': '7824400107:AAGZqPdS0E0N3HsYpD8TW9m8c-bapFd-RHk',
    'chat_id': '678873745',  # ID чата для уведомлений
    'channel_id': '@truelivebet'  # ID канала
}

# Настройки парсинга
PARSING_CONFIG = {
    'interval_minutes': 2,  # Интервал проверки матчей (в минутах)
    'max_matches_per_check': 20,  # Максимум матчей за одну проверку
    'timeout_seconds': 30  # Таймаут для HTTP запросов
}

# Критерии анализа TrueLiveBet
ANALYSIS_CRITERIA = {
    'football': {
        'min_time': 15,  # Минимальное время матча для анализа
        'max_time': 85,  # Максимальное время матча для анализа
        'min_odds': 1.1,  # Минимальный коэффициент
        'max_odds': 3.0,  # Максимальный коэффициент
        'score_patterns': ['1:0', '2:0', '0:1', '0:2'],  # Выгодные счета
        'time_patterns': ['75-85', '80-90']  # Выгодное время
    },
    'basketball': {
        'min_time': 5,   # Минимальное время четверти
        'max_time': 10,  # Максимальное время четверти
        'min_odds': 1.1,
        'max_odds': 2.5,
        'score_patterns': ['15:10', '20:15', '25:20'],  # Выгодные счета
        'quarter_patterns': ['1-3', '2-4']  # Выгодные четверти
    },
    'tennis': {
        'min_games': 3,  # Минимальное количество геймов
        'min_odds': 1.1,
        'max_odds': 2.0,
        'score_patterns': ['6:4', '7:5', '6:3'],  # Выгодные счета
        'set_patterns': ['1-0', '2-0']  # Выгодные сеты
    }
}

# Источники данных (упрощенная система)
DATA_SOURCES = {
    'primary': {
        'betboom_live': 'https://betboom.ru/live',  # Основной источник live матчей
        'betboom_events': 'https://betboom.ru/events'  # События для деталей
    },
    'rankings': {
        'transfermarkt': 'https://www.transfermarkt.com'  # Только рейтинги и форма команд
    }
}

# Claude AI настройки
CLAUDE_CONFIG = {
    'api_key': 'YOUR_CLAUDE_API_KEY_HERE',  # Замените на ваш ключ
    'model': 'claude-3-sonnet-20240229',
    'max_tokens': 1000,
    'temperature': 0.7,
    'enabled': False  # Включить после получения API ключа
}

# Настройки логирования
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': 'logs/bot.log',
    'max_size_mb': 10,
    'backup_count': 5
}

# Настройки базы данных
DATABASE_CONFIG = {
    'matches_file': 'data/matches_history.json',
    'max_history_days': 30,
    'backup_enabled': True
}

# Настройки уведомлений
NOTIFICATION_CONFIG = {
    'min_confidence': 0.7,  # Минимальная уверенность для отправки
    'max_notifications_per_hour': 10,  # Максимум уведомлений в час
    'cooldown_minutes': 15  # Кулдаун между уведомлениями на один матч
}