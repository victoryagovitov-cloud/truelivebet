#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrueLiveBet Bot - Автоматический анализ live матчей
Упрощенная система: BetBoom Live + Transfermarkt (рейтинги)
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random

# Импортируем конфигурацию
from config import (
    TELEGRAM_CONFIG, PARSING_CONFIG, ANALYSIS_CRITERIA,
    DATA_SOURCES, CLAUDE_CONFIG, LOGGING_CONFIG,
    DATABASE_CONFIG, NOTIFICATION_CONFIG
)

# Импортируем Claude анализатор
from claude_analyzer import ClaudeAnalyzer

# Настройка логирования
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BetBoomParser:
    """Парсер для BetBoom - основной источник live матчей"""
    
    def __init__(self):
        self.base_url = DATA_SOURCES['primary']['betboom_live']
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_live_matches(self) -> List[Dict]:
        """Получает live матчи с BetBoom"""
        try:
            logger.info("Получаю live матчи с BetBoom...")
            
            # Создаем запрос
            req = urllib.request.Request(
                self.base_url,
                headers=self.headers
            )
            
            # Выполняем запрос
            with urllib.request.urlopen(req, timeout=PARSING_CONFIG['timeout_seconds']) as response:
                html = response.read().decode('utf-8')
            
            # Парсим HTML (упрощенная версия)
            matches = self._parse_betboom_html(html)
            
            logger.info(f"Найдено {len(matches)} live матчей")
            return matches
            
        except Exception as e:
            logger.error(f"Ошибка при получении матчей с BetBoom: {e}")
            # Возвращаем демо-данные для тестирования
            return self._get_demo_matches()
    
    def _parse_betboom_html(self, html: str) -> List[Dict]:
        """Парсит HTML BetBoom для извлечения live матчей"""
        # В реальной версии здесь будет парсинг HTML
        # Сейчас возвращаем демо-данные
        return self._get_demo_matches()
    
    def _get_demo_matches(self) -> List[Dict]:
        """Демо-данные для тестирования"""
        return [
            {
                'id': 'demo_1',
                'sport': 'football',
                'team1': 'Црвена Звезда',
                'team2': 'Лех Познань',
                'score': '1:0',
                'time': '88',
                'status': 'live',
                'odds': {'1': 1.1, 'X': 8.5, '2': 15.0},
                'url': 'https://betboom.ru/bet/87654321'
            },
            {
                'id': 'demo_2',
                'sport': 'basketball',
                'team1': 'Барселона',
                'team2': 'Реал Мадрид',
                'score': '25:20',
                'time': '8',
                'quarter': '2',
                'status': 'live',
                'odds': {'1': 1.8, '2': 2.1},
                'url': 'https://betboom.ru/event/12345678'
            },
            {
                'id': 'demo_3',
                'sport': 'tennis',
                'team1': 'Новак Джокович',
                'team2': 'Карлос Алькарас',
                'score': '6:4, 7:5',
                'sets': '2:0',
                'status': 'live',
                'odds': {'1': 1.5, '2': 2.5},
                'url': 'https://betboom.ru/event/98765432'
            }
        ]

class TransfermarktRankings:
    """Получение рейтингов и формы команд с Transfermarkt"""
    
    def __init__(self):
        self.base_url = DATA_SOURCES['rankings']['transfermarkt']
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_team_rankings(self, team_name: str) -> Dict:
        """Получает рейтинги команды с Transfermarkt"""
        try:
            logger.info(f"Получаю рейтинги для команды: {team_name}")
            
            # В реальной версии здесь будет поиск команды на Transfermarkt
            # Сейчас возвращаем демо-данные
            return self._get_demo_rankings(team_name)
            
        except Exception as e:
            logger.error(f"Ошибка при получении рейтингов для {team_name}: {e}")
            return self._get_demo_rankings(team_name)
    
    def _get_demo_rankings(self, team_name: str) -> Dict:
        """Демо-рейтинги для тестирования"""
        # Генерируем реалистичные данные на основе имени команды
        if 'Звезда' in team_name:
            return {
                'league_position': 1,
                'recent_form': ['W', 'W', 'D', 'W', 'W'],
                'points': 45,
                'goals_for': 28,
                'goals_against': 8,
                'last_5_matches': ['3:0', '2:1', '1:1', '4:0', '2:0']
            }
        elif 'Барселона' in team_name:
            return {
                'league_position': 2,
                'recent_form': ['W', 'L', 'W', 'D', 'W'],
                'points': 42,
                'goals_for': 35,
                'goals_against': 18,
                'last_5_matches': ['3:1', '0:2', '4:0', '2:2', '1:0']
            }
        else:
            return {
                'league_position': random.randint(3, 15),
                'recent_form': random.choice([['W', 'D', 'L', 'W', 'D'], ['L', 'W', 'W', 'L', 'W']]),
                'points': random.randint(20, 40),
                'goals_for': random.randint(15, 30),
                'goals_against': random.randint(15, 30),
                'last_5_matches': ['1:0', '2:1', '0:1', '3:2', '1:1']
            }

class MatchAnalyzer:
    """Анализатор матчей по критериям TrueLiveBet"""
    
    def __init__(self):
        self.criteria = ANALYSIS_CRITERIA
    
    def analyze_match(self, match: Dict, rankings: Dict = None) -> Dict:
        """Анализирует матч по критериям TrueLiveBet"""
        try:
            sport = match.get('sport', 'football')
            analysis_result = {
                'match_id': match['id'],
                'sport': sport,
                'confidence': 0.0,
                'recommendation': 'skip',
                'reasoning': '',
                'analysis_source': 'Python',
                'rankings_data': rankings
            }
            
            # Анализируем по виду спорта
            if sport == 'football':
                result = self._analyze_football(match, rankings)
            elif sport == 'basketball':
                result = self._analyze_basketball(match, rankings)
            elif sport == 'tennis':
                result = self._analyze_tennis(match, rankings)
            else:
                result = {'confidence': 0.0, 'recommendation': 'skip', 'reasoning': 'Неподдерживаемый вид спорта'}
            
            # Обновляем результат
            analysis_result.update(result)
            
            logger.info(f"Анализ матча {match['id']}: уверенность {analysis_result['confidence']:.2f}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Ошибка при анализе матча {match.get('id', 'unknown')}: {e}")
            return {
                'match_id': match.get('id', 'unknown'),
                'confidence': 0.0,
                'recommendation': 'skip',
                'reasoning': f'Ошибка анализа: {e}',
                'analysis_source': 'Python'
            }
    
    def _analyze_football(self, match: Dict, rankings: Dict = None) -> Dict:
        """Анализ футбольного матча"""
        score = match.get('score', '0:0')
        time = int(match.get('time', 0))
        odds = match.get('odds', {})
        
        # Проверяем критерии
        confidence = 0.0
        reasoning = []
        
        # Время матча
        if self.criteria['football']['min_time'] <= time <= self.criteria['football']['max_time']:
            confidence += 0.3
            reasoning.append(f"Время матча: {time} мин")
        else:
            reasoning.append(f"Время матча: {time} мин")
        
        # Счет
        if score in self.criteria['football']['score_patterns']:
            confidence += 0.4
            reasoning.append(f"Счет {score} - выгодный паттерн")
        else:
            reasoning.append(f"Счет {score} - не выгодный паттерн")
        
        # Коэффициенты
        if '1' in odds and self.criteria['football']['min_odds'] <= odds['1'] <= self.criteria['football']['max_odds']:
            confidence += 0.2
            reasoning.append(f"Коэффициент П1: {odds['1']}")
        else:
            reasoning.append(f"Коэффициент П1: {odds.get('1', 'N/A')}")
        
        # Рейтинги команд (если доступны)
        if rankings:
            team1_pos = rankings.get('team1_position', 0)
            team2_pos = rankings.get('team2_position', 0)
            if team1_pos < team2_pos:
                confidence += 0.1
                reasoning.append(f"Позиция в лиге: {team1_pos} vs {team2_pos} (команда 1 выше)")
        
        # Определяем рекомендацию
        if confidence >= 0.7:
            recommendation = 'strong_buy'
        elif confidence >= 0.5:
            recommendation = 'buy'
        else:
            recommendation = 'skip'
        
        return {
            'confidence': min(confidence, 1.0),
            'recommendation': recommendation,
            'reasoning': ' | '.join(reasoning)
        }
    
    def _analyze_basketball(self, match: Dict, rankings: Dict = None) -> Dict:
        """Анализ баскетбольного матча"""
        score = match.get('score', '0:0')
        time = int(match.get('time', 0))
        quarter = int(match.get('quarter', 1))
        odds = match.get('odds', {})
        
        confidence = 0.0
        reasoning = []
        
        # Время четверти
        if self.criteria['basketball']['min_time'] <= time <= self.criteria['basketball']['max_time']:
            confidence += 0.3
            reasoning.append(f"Время четверти: {time} мин")
        else:
            reasoning.append(f"Время четверти: {time} мин")
        
        # Четверть
        if str(quarter) in self.criteria['basketball']['quarter_patterns']:
            confidence += 0.3
            reasoning.append(f"Четверть {quarter} - выгодная")
        else:
            reasoning.append(f"Четверть {quarter} - не выгодная")
        
        # Счет
        if score in self.criteria['basketball']['score_patterns']:
            confidence += 0.3
            reasoning.append(f"Счет {score} - выгодный паттерн")
        else:
            reasoning.append(f"Счет {score} - не выгодный паттерн")
        
        # Коэффициенты
        if '1' in odds and self.criteria['basketball']['min_odds'] <= odds['1'] <= self.criteria['basketball']['max_odds']:
            confidence += 0.1
            reasoning.append(f"Коэффициент П1: {odds['1']}")
        
        # Определяем рекомендацию
        if confidence >= 0.7:
            recommendation = 'strong_buy'
        elif confidence >= 0.5:
            recommendation = 'buy'
        else:
            recommendation = 'skip'
        
        return {
            'confidence': min(confidence, 1.0),
            'recommendation': recommendation,
            'reasoning': ' | '.join(reasoning)
        }
    
    def _analyze_tennis(self, match: Dict, rankings: Dict = None) -> Dict:
        """Анализ теннисного матча"""
        score = match.get('score', '0:0')
        sets = match.get('sets', '0:0')
        odds = match.get('odds', {})
        
        confidence = 0.0
        reasoning = []
        
        # Сеты
        if sets in self.criteria['tennis']['set_patterns']:
            confidence += 0.4
            reasoning.append(f"Сеты {sets} - выгодный паттерн")
        else:
            reasoning.append(f"Сеты {sets} - не выгодный паттерн")
        
        # Счет
        if score in self.criteria['tennis']['score_patterns']:
            confidence += 0.3
            reasoning.append(f"Счет {score} - выгодный паттерн")
        else:
            reasoning.append(f"Счет {score} - не выгодный паттерн")
        
        # Коэффициенты
        if '1' in odds and self.criteria['tennis']['min_odds'] <= odds['1'] <= self.criteria['tennis']['max_odds']:
            confidence += 0.3
            reasoning.append(f"Коэффициент П1: {odds['1']}")
        
        # Определяем рекомендацию
        if confidence >= 0.7:
            recommendation = 'strong_buy'
        elif confidence >= 0.5:
            recommendation = 'buy'
        else:
            recommendation = 'skip'
        
        return {
            'confidence': min(confidence, 1.0),
            'recommendation': recommendation,
            'reasoning': ' | '.join(reasoning)
        }

class TelegramNotifier:
    """Отправка уведомлений в Telegram"""
    
    def __init__(self):
        self.bot_token = TELEGRAM_CONFIG['bot_token']
        self.chat_id = TELEGRAM_CONFIG['chat_id']
        self.channel_id = TELEGRAM_CONFIG['channel_id']
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, message: str, chat_id: str = None) -> bool:
        """Отправляет сообщение в Telegram"""
        try:
            if not chat_id:
                chat_id = self.chat_id
            
            # Кодируем сообщение для URL
            encoded_message = urllib.parse.quote(message)
            
            # Формируем URL для отправки
            url = f"{self.base_url}/sendMessage?chat_id={chat_id}&text={encoded_message}&parse_mode=HTML"
            
            # Отправляем запрос
            with urllib.request.urlopen(url, timeout=10) as response:
                result = response.read().decode('utf-8')
                response_data = json.loads(result)
                
                if response_data.get('ok'):
                    logger.info(f"Сообщение отправлено в чат {chat_id}")
                    return True
                else:
                    logger.error(f"Ошибка отправки: {response_data}")
                    return False
                    
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")
            return False
    
    def send_to_channel(self, message: str) -> bool:
        """Отправляет сообщение в канал"""
        return self.send_message(message, self.channel_id)
    
    def format_telegram_message(self, match: Dict, analysis: Dict, claude_analysis: Dict = None) -> str:
        """Форматирует сообщение для Telegram в прежнем формате"""
        sport = match.get('sport', 'football')
        team1 = match.get('team1', 'Команда 1')
        team2 = match.get('team2', 'Команда 2')
        score = match.get('score', '0:0')
        time = match.get('time', '0')
        odds = match.get('odds', {})
        
        # Эмодзи для видов спорта
        sport_emoji = {
            'football': '⚽',
            'basketball': '🏀',
            'tennis': '🎾',
            'handball': '🤾',
            'table_tennis': '🏓'
        }.get(sport, '🏆')
        
        # Названия видов спорта на русском
        sport_names = {
            'football': 'Футбол',
            'basketball': 'Баскетбол',
            'tennis': 'Теннис',
            'handball': 'Гандбол',
            'table_tennis': 'Настольный теннис'
        }.get(sport, sport.title())
        
        # Форматируем время в зависимости от вида спорта
        if sport == 'football':
            time_info = f"{time} мин"
        elif sport == 'basketball':
            quarter = match.get('quarter', '1')
            time_info = f"Четверть {quarter}"
        elif sport == 'tennis':
            sets = match.get('sets', '0:0')
            time_info = f"Сеты: {sets}"
        else:
            time_info = f"{time}"
        
        # Определяем рекомендацию
        if analysis['recommendation'] == 'strong_buy':
            recommendation = f"Победа {team1}" if '1' in odds else f"Победа {team2}"
        elif analysis['recommendation'] == 'buy':
            recommendation = f"Победа {team1}" if '1' in odds else f"Победа {team2}"
        else:
            recommendation = "Анализ в процессе"
        
        # Формируем сообщение в прежнем формате
        message = f"🎯 <b>TrueLiveBet - Найден подходящий матч!</b>\n\n"
        message += f"{sport_emoji} <b>Вид спорта:</b> {sport_names}\n"
        message += f"🏆 <b>Матч:</b> {team1} vs {team2}\n"
        message += f"📊 <b>Счет:</b> {score}\n"
        message += f"⏰ <b>Время:</b> {time_info}\n"
        message += f"📈 <b>Уверенность:</b> {analysis['confidence']:.0%}\n\n"
        
        message += f"💡 <b>Рекомендация:</b> {recommendation}\n\n"
        
        # Добавляем обоснование от нейросети (если доступен)
        if claude_analysis and claude_analysis.get('enabled'):
            message += f"🔍 <b>Обоснование:</b>\n"
            analysis_text = claude_analysis.get('analysis_text', '')
            if analysis_text:
                # Разбиваем на предложения и делаем более читаемым
                sentences = analysis_text.split('. ')
                for sentence in sentences:
                    if sentence.strip():
                        message += f"• {sentence.strip()}\n"
            else:
                message += "• Анализ нейросети недоступен\n"
        else:
            # Если нейросеть недоступна, используем базовое обоснование
            message += f"🔍 <b>Обоснование:</b>\n"
            reasoning_parts = analysis.get('reasoning', '').split(' | ')
            if reasoning_parts and reasoning_parts[0]:
                for reason in reasoning_parts:
                    # Убираем слово "паттерн" и исправляем падежи
                    clean_reason = reason.replace('паттерн', 'ситуация').replace('Паттерн', 'Ситуация')
                    
                    # Исправляем падежи для лучшей согласованности
                    if 'Счет' in clean_reason and 'выгодный' in clean_reason:
                        clean_reason = clean_reason.replace('выгодный паттерн', 'выгодная ситуация')
                        clean_reason = clean_reason.replace('выгодный', 'выгодная')
                    elif 'Счет' in clean_reason and 'выгодная' in clean_reason:
                        clean_reason = clean_reason.replace('выгодная ситуация', 'выгодная ситуация')
                    elif 'Четверть' in clean_reason and 'выгодная' in clean_reason:
                        clean_reason = clean_reason.replace('четверть', 'четверть')
                    
                    # Дополнительные исправления падежей
                    if 'не выгодный' in clean_reason:
                        clean_reason = clean_reason.replace('не выгодный', 'не выгодная')
                    if 'не выгодная' in clean_reason:
                        clean_reason = clean_reason.replace('не выгодная', 'не выгодная')
                    
                    message += f"• {clean_reason}\n"
            else:
                message += "• Недостаточно данных для рекомендации\n"
        
        # Добавляем анализ Claude (если доступен)
        if claude_analysis and claude_analysis.get('enabled'):
            if claude_analysis.get('risks'):
                message += f"\n⚠️ <b>Риски:</b>\n"
                risks = claude_analysis['risks']
                if isinstance(risks, list):
                    for risk in risks:
                        message += f"• {risk}\n"
                else:
                    message += f"• {risks}\n"
            
            if claude_analysis.get('bet_size'):
                message += f"\n💰 <b>Размер ставки:</b> {claude_analysis['bet_size']}% от банка\n"
        
        # Добавляем время анализа по Москве
        from datetime import timezone, timedelta
        moscow_tz = timezone(timedelta(hours=3))  # UTC+3 для Москвы
        current_time = datetime.now(moscow_tz).strftime('%H:%M:%S')
        message += f"\n⏰ <i>Время: {current_time} (МСК)</i>"
        
        return message

class DatabaseManager:
    """Управление базой данных матчей"""
    
    def __init__(self):
        self.data_file = DATABASE_CONFIG['matches_file']
        self.max_history_days = DATABASE_CONFIG['max_history_days']
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Создает директорию для данных если не существует"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def save_match_analysis(self, match: Dict, analysis: Dict):
        """Сохраняет анализ матча в базу"""
        try:
            # Загружаем существующие данные
            data = self.load_matches_history()
            
            # Добавляем новый анализ
            match_record = {
                'timestamp': datetime.now().isoformat(),
                'match': match,
                'analysis': analysis
            }
            
            data.append(match_record)
            
            # Ограничиваем историю
            cutoff_date = datetime.now() - timedelta(days=self.max_history_days)
            data = [record for record in data 
                    if datetime.fromisoformat(record['timestamp']) > cutoff_date]
            
            # Сохраняем
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Анализ матча {match['id']} сохранен в базу")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении в базу: {e}")
    
    def load_matches_history(self) -> List[Dict]:
        """Загружает историю матчей из базы"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Ошибка при загрузке истории: {e}")
            return []
    
    def get_recent_matches(self, hours: int = 24) -> List[Dict]:
        """Получает матчи за последние N часов"""
        try:
            data = self.load_matches_history()
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_matches = []
            for record in data:
                record_time = datetime.fromisoformat(record['timestamp'])
                if record_time > cutoff_time:
                    recent_matches.append(record)
            
            return recent_matches
            
        except Exception as e:
            logger.error(f"Ошибка при получении недавних матчей: {e}")
            return []

class TrueLiveBetBot:
    """Основной класс TrueLiveBet Bot"""
    
    def __init__(self):
        self.parser = BetBoomParser()
        self.rankings = TransfermarktRankings()
        self.analyzer = MatchAnalyzer()
        self.notifier = TelegramNotifier()
        self.database = DatabaseManager()
        self.claude_analyzer = ClaudeAnalyzer() if CLAUDE_CONFIG['enabled'] else None
        
        # Статистика
        self.stats = {
            'matches_checked': 0,
            'notifications_sent': 0,
            'last_check': None
        }
    
    def check_matches(self):
        """Основной цикл проверки матчей"""
        try:
            logger.info("🔍 Начинаю проверку live матчей...")
            
            # Получаем live матчи с BetBoom
            matches = self.parser.get_live_matches()
            self.stats['matches_checked'] = len(matches)
            
            if not matches:
                logger.info("Live матчи не найдены")
                return
            
            # Анализируем каждый матч
            for match in matches:
                self._process_match(match)
            
            # Обновляем статистику
            self.stats['last_check'] = datetime.now()
            logger.info(f"✅ Проверка завершена. Обработано матчей: {len(matches)}")
            
        except Exception as e:
            logger.error(f"Ошибка в основном цикле: {e}")
    
    def _process_match(self, match: Dict):
        """Обрабатывает один матч"""
        try:
            # Получаем рейтинги команд (если доступны)
            rankings = {}
            if match.get('team1'):
                team1_rankings = self.rankings.get_team_rankings(match['team1'])
                rankings['team1'] = team1_rankings
            
            if match.get('team2'):
                team2_rankings = self.rankings.get_team_rankings(match['team2'])
                rankings['team2'] = team2_rankings
            
            # Анализируем матч
            analysis = self.analyzer.analyze_match(match, rankings)
            
            # Анализ Claude (если доступен)
            claude_analysis = None
            if self.claude_analyzer and CLAUDE_CONFIG['enabled']:
                claude_analysis = self.claude_analyzer.analyze_match(match, analysis)
                
                # Обновляем итоговую уверенность
                if claude_analysis.get('enabled'):
                    analysis['final_confidence'] = (analysis['confidence'] + claude_analysis.get('confidence', 0)) / 2
                    analysis['analysis_source'] = f"Claude AI + Python"
                    analysis['claude_analysis_text'] = claude_analysis.get('analysis_text', '')
                    analysis['claude_risks'] = claude_analysis.get('risks', '')
                    analysis['claude_bet_size'] = claude_analyzer.get('bet_size', '')
            
            # Сохраняем в базу
            self.database.save_match_analysis(match, analysis)
            
            # Отправляем уведомление если матч подходит
            if analysis['recommendation'] in ['buy', 'strong_buy']:
                self._send_notification(match, analysis, claude_analysis)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке матча {match.get('id', 'unknown')}: {e}")
    
    def _send_notification(self, match: Dict, analysis: Dict, claude_analysis: Dict = None):
        """Отправляет уведомление о матче"""
        try:
            # Форматируем сообщение
            message = self.notifier.format_telegram_message(match, analysis, claude_analysis)
            
            # Отправляем только в канал
            if self.notifier.send_to_channel(message):
                self.stats['notifications_sent'] += 1
                logger.info(f"Уведомление отправлено в канал для матча {match['id']}")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления: {e}")
    
    def run(self):
        """Запускает бота"""
        logger.info("🚀 TrueLiveBet Bot запущен!")
        logger.info(f"Интервал проверки: {PARSING_CONFIG['interval_minutes']} минут")
        logger.info(f"Telegram канал: {TELEGRAM_CONFIG['channel_id']}")
        
        if CLAUDE_CONFIG['enabled']:
            logger.info("🤖 Claude AI интегрирован")
        else:
            logger.info("🤖 Claude AI отключен (нужен API ключ)")
        
        try:
            while True:
                # Проверяем матчи
                self.check_matches()
                
                # Ждем следующей проверки
                interval_seconds = PARSING_CONFIG['interval_minutes'] * 60
                logger.info(f"⏰ Следующая проверка через {PARSING_CONFIG['interval_minutes']} минут")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("🛑 Бот остановлен пользователем")
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            raise

def main():
    """Главная функция"""
    try:
        # Создаем и запускаем бота
        bot = TrueLiveBetBot()
        bot.run()
        
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        raise

if __name__ == "__main__":
    main()