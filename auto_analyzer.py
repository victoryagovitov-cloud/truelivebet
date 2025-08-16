#!/usr/bin/env python3
"""
TrueLiveBet - Автоматический анализатор матчей
Мониторит BetBoom каждые 30 минут и отправляет уведомления в Telegram
"""

import json
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import urllib.parse
import re
from dataclasses import dataclass, asdict
import os

# Импортируем конфигурацию
from config import (
    TELEGRAM_CONFIG, PARSING_CONFIG, ANALYSIS_CRITERIA,
    DATA_SOURCES, LOGGING_CONFIG, DATABASE_CONFIG, NOTIFICATION_CONFIG
)

@dataclass
class Match:
    """Класс для хранения информации о матче"""
    id: str
    sport_type: str
    team1: str
    team2: str
    score: str
    time_elapsed: str
    league: str
    odds: Dict[str, float]
    match_url: str
    last_updated: datetime
    confidence: int = 0
    recommendation: str = ""
    reasoning: List[str] = None
    
    def __post_init__(self):
        if self.reasoning is None:
            self.reasoning = []

@dataclass
class AnalysisResult:
    """Результат анализа матча"""
    match: Match
    confidence: int
    recommendation: str
    reasoning: List[str]
    should_notify: bool
    analysis_time: datetime

class BetBoomParser:
    """Парсер для BetBoom"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DATA_SOURCES['betboom']['headers'])
        self.base_url = DATA_SOURCES['betboom']['base_url']
    
    def get_live_matches(self) -> List[Match]:
        """Получает список live матчей с BetBoom"""
        try:
            logging.info("Получаю live матчи с BetBoom...")
            
            # Пробуем получить live матчи
            live_url = f"{self.base_url}/live"
            response = self.session.get(live_url, timeout=PARSING_CONFIG['timeout_seconds'])
            
            if response.status_code != 200:
                logging.warning(f"Ошибка получения live матчей: {response.status_code}")
                return []
            
            # Парсим HTML для извлечения матчей
            matches = self._parse_live_matches_html(response.text)
            logging.info(f"Найдено {len(matches)} live матчей")
            
            return matches
            
        except Exception as e:
            logging.error(f"Ошибка при получении live матчей: {e}")
            return []
    
    def _parse_live_matches_html(self, html_content: str) -> List[Match]:
        """Парсит HTML для извлечения информации о матчах"""
        matches = []
        
        try:
            # Простой парсинг по регулярным выражениям
            # В реальном проекте лучше использовать BeautifulSoup
            
            # Ищем блоки с матчами (это упрощенная версия)
            match_pattern = r'<div[^>]*class="[^"]*match[^"]*"[^>]*>(.*?)</div>'
            match_blocks = re.findall(match_pattern, html_content, re.DOTALL)
            
            for block in match_blocks[:PARSING_CONFIG['max_matches_per_check']]:
                match = self._extract_match_from_block(block)
                if match:
                    matches.append(match)
            
        except Exception as e:
            logging.error(f"Ошибка парсинга HTML: {e}")
        
        return matches
    
    def _extract_match_from_block(self, block: str) -> Optional[Match]:
        """Извлекает информацию о матче из HTML блока"""
        try:
            # Упрощенное извлечение данных
            # В реальном проекте нужен более сложный парсинг
            
            # Извлекаем команды
            team1_match = re.search(r'<span[^>]*class="[^"]*team1[^"]*"[^>]*>(.*?)</span>', block)
            team2_match = re.search(r'<span[^>]*class="[^"]*team2[^"]*"[^>]*>(.*?)</span>', block)
            
            if not team1_match or not team2_match:
                return None
            
            team1 = team1_match.group(1).strip()
            team2 = team2_match.group(1).strip()
            
            # Извлекаем счет
            score_match = re.search(r'<span[^>]*class="[^"]*score[^"]*"[^>]*>(.*?)</span>', block)
            score = score_match.group(1).strip() if score_match else "0:0"
            
            # Извлекаем время
            time_match = re.search(r'<span[^>]*class="[^"]*time[^"]*"[^>]*>(.*?)</span>', block)
            time_elapsed = time_match.group(1).strip() if time_match else "0'"
            
            # Определяем вид спорта (упрощенно)
            sport_type = self._detect_sport_type(block)
            
            # Создаем объект матча
            match = Match(
                id=f"{team1}_{team2}_{int(time.time())}",
                sport_type=sport_type,
                team1=team1,
                team2=team2,
                score=score,
                time_elapsed=time_elapsed,
                league="Неизвестно",
                odds={},
                match_url=f"{self.base_url}/live",
                last_updated=datetime.now()
            )
            
            return match
            
        except Exception as e:
            logging.error(f"Ошибка извлечения матча: {e}")
            return None
    
    def _detect_sport_type(self, block: str) -> str:
        """Определяет вид спорта по HTML блоку"""
        block_lower = block.lower()
        
        if 'футбол' in block_lower or 'football' in block_lower:
            return 'football'
        elif 'теннис' in block_lower or 'tennis' in block_lower:
            return 'tennis'
        elif 'баскетбол' in block_lower or 'basketball' in block_lower:
            return 'basketball'
        elif 'гандбол' in block_lower or 'handball' in block_lower:
            return 'handball'
        else:
            return 'unknown'

class MatchAnalyzer:
    """Анализатор матчей по критериям TrueLiveBet"""
    
    def __init__(self):
        self.criteria = ANALYSIS_CRITERIA
    
    def analyze_match(self, match: Match) -> AnalysisResult:
        """Анализирует матч по критериям"""
        try:
            if match.sport_type == 'football':
                return self._analyze_football(match)
            elif match.sport_type == 'tennis':
                return self._analyze_tennis(match)
            elif match.sport_type == 'basketball':
                return self._analyze_basketball(match)
            elif match.sport_type == 'handball':
                return self._analyze_handball(match)
            else:
                return self._create_empty_result(match)
                
        except Exception as e:
            logging.error(f"Ошибка анализа матча {match.id}: {e}")
            return self._create_empty_result(match)
    
    def _analyze_football(self, match: Match) -> AnalysisResult:
        """Анализ футбольного матча"""
        try:
            # Парсим счет
            home_score, away_score = map(int, match.score.split(':'))
            goal_difference = abs(home_score - away_score)
            
            # Парсим время
            time_minutes = self._parse_time(match.time_elapsed)
            
            confidence = 0
            recommendation = ""
            reasoning = []
            
            # Проверяем критерии
            if (goal_difference >= self.criteria['football']['min_goal_difference'] and
                time_minutes >= self.criteria['football']['min_time_elapsed']):
                
                favorite = match.team1 if home_score > away_score else match.team2
                confidence = 80
                recommendation = f"Победа {favorite}"
                reasoning.append(f"Фаворит ведет на {goal_difference} гола")
                reasoning.append(f"Время матча: {time_minutes} минут")
            
            should_notify = confidence >= self.criteria['football']['confidence_threshold']
            
            return AnalysisResult(
                match=match,
                confidence=confidence,
                recommendation=recommendation,
                reasoning=reasoning,
                should_notify=should_notify,
                analysis_time=datetime.now()
            )
            
        except Exception as e:
            logging.error(f"Ошибка анализа футбола: {e}")
            return self._create_empty_result(match)
    
    def _analyze_tennis(self, match: Match) -> AnalysisResult:
        """Анализ теннисного матча"""
        # Упрощенный анализ для демонстрации
        confidence = 0
        recommendation = ""
        reasoning = []
        
        # Здесь должна быть логика анализа тенниса
        # Пока возвращаем пустой результат
        
        return AnalysisResult(
            match=match,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning,
            should_notify=False,
            analysis_time=datetime.now()
        )
    
    def _analyze_basketball(self, match: Match) -> AnalysisResult:
        """Анализ баскетбольного матча"""
        try:
            # Парсим счет
            home_score, away_score = map(int, match.score.split(':'))
            point_difference = abs(home_score - away_score)
            
            confidence = 0
            recommendation = ""
            reasoning = []
            
            # Проверяем критерии
            if point_difference >= self.criteria['basketball']['min_point_difference']:
                favorite = match.team1 if home_score > away_score else match.team2
                confidence = 70
                recommendation = f"Победа {favorite}"
                reasoning.append(f"Отрыв {point_difference} очков")
            
            should_notify = confidence >= self.criteria['basketball']['confidence_threshold']
            
            return AnalysisResult(
                match=match,
                confidence=confidence,
                recommendation=recommendation,
                reasoning=reasoning,
                should_notify=should_notify,
                analysis_time=datetime.now()
            )
            
        except Exception as e:
            logging.error(f"Ошибка анализа баскетбола: {e}")
            return self._create_empty_result(match)
    
    def _analyze_handball(self, match: Match) -> AnalysisResult:
        """Анализ гандбольного матча"""
        try:
            # Парсим счет
            home_score, away_score = map(int, match.score.split(':'))
            goal_difference = abs(home_score - away_score)
            
            # Парсим время
            time_minutes = self._parse_time(match.time_elapsed)
            
            confidence = 0
            recommendation = ""
            reasoning = []
            
            # Проверяем критерии
            if (goal_difference >= self.criteria['handball']['min_goal_difference'] and
                time_minutes >= self.criteria['handball']['min_time_elapsed']):
                
                favorite = match.team1 if home_score > away_score else match.team2
                confidence = 75
                recommendation = f"Победа {favorite}"
                reasoning.append(f"Отрыв {goal_difference} голов")
                reasoning.append(f"Время матча: {time_minutes} минут")
            
            should_notify = confidence >= self.criteria['handball']['confidence_threshold']
            
            return AnalysisResult(
                match=match,
                confidence=confidence,
                recommendation=recommendation,
                reasoning=reasoning,
                should_notify=should_notify,
                analysis_time=datetime.now()
            )
            
        except Exception as e:
            logging.error(f"Ошибка анализа гандбола: {e}")
            return self._create_empty_result(match)
    
    def _parse_time(self, time_str: str) -> int:
        """Парсит время матча в минуты"""
        try:
            # Убираем все кроме цифр
            time_digits = re.sub(r'[^\d]', '', time_str)
            return int(time_digits) if time_digits else 0
        except:
            return 0
    
    def _create_empty_result(self, match: Match) -> AnalysisResult:
        """Создает пустой результат анализа"""
        return AnalysisResult(
            match=match,
            confidence=0,
            recommendation="",
            reasoning=[],
            should_notify=False,
            analysis_time=datetime.now()
        )

class TelegramNotifier:
    """Отправляет уведомления в Telegram"""
    
    def __init__(self):
        self.bot_token = TELEGRAM_CONFIG['bot_token']
        self.chat_id = TELEGRAM_CONFIG['chat_id']
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Проверяем настройки
        if self.bot_token == 'YOUR_BOT_TOKEN_HERE':
            logging.warning("Telegram bot token не настроен!")
    
    def send_notification(self, analysis_result: AnalysisResult) -> bool:
        """Отправляет уведомление о найденном матче"""
        try:
            if not self.bot_token or self.bot_token == 'YOUR_BOT_TOKEN_HERE':
                logging.warning("Telegram bot не настроен, пропускаю уведомление")
                return False
            
            message = self._format_message(analysis_result)
            
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                logging.info(f"Уведомление отправлено для матча {analysis_result.match.id}")
                return True
            else:
                logging.error(f"Ошибка отправки уведомления: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"Ошибка отправки уведомления: {e}")
            return False
    
    def _format_message(self, analysis_result: AnalysisResult) -> str:
        """Форматирует сообщение для Telegram"""
        match = analysis_result.match
        
        message = f"""
🎯 <b>TrueLiveBet - Найден подходящий матч!</b>

⚽ <b>Вид спорта:</b> {self._get_sport_emoji(match.sport_type)} {match.sport_type.title()}
🏆 <b>Матч:</b> {match.team1} vs {match.team2}
📊 <b>Счет:</b> {match.score}
⏰ <b>Время:</b> {match.time_elapsed}
📈 <b>Уверенность:</b> {analysis_result.confidence}%

💡 <b>Рекомендация:</b> {analysis_result.recommendation or 'Анализ в процессе'}

🔍 <b>Обоснование:</b>
"""
        
        for reason in analysis_result.reasoning:
            message += f"• {reason}\n"
        
        if NOTIFICATION_CONFIG['include_match_url']:
            message += f"\n🔗 <a href='{match.match_url}'>Смотреть матч</a>"
        
        message += f"\n\n⏰ <i>Анализ: {analysis_result.analysis_time.strftime('%H:%M:%S')}</i>"
        
        return message
    
    def _get_sport_emoji(self, sport_type: str) -> str:
        """Возвращает эмодзи для вида спорта"""
        emojis = {
            'football': '⚽',
            'tennis': '🎾',
            'basketball': '🏀',
            'handball': '🤾',
            'tabletennis': '🏓'
        }
        return emojis.get(sport_type, '🏆')

class DatabaseManager:
    """Управляет базой данных матчей"""
    
    def __init__(self):
        self.db_path = DATABASE_CONFIG['file_path']
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Создает директорию для данных если её нет"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def save_match(self, match: Match, analysis_result: AnalysisResult):
        """Сохраняет матч и результат анализа"""
        try:
            data = self._load_data()
            
            match_data = {
                'match': asdict(match),
                'analysis': {
                    'confidence': analysis_result.confidence,
                    'recommendation': analysis_result.recommendation,
                    'reasoning': analysis_result.reasoning,
                    'should_notify': analysis_result.should_notify,
                    'analysis_time': analysis_result.analysis_time.isoformat()
                },
                'saved_at': datetime.now().isoformat()
            }
            
            # Обновляем существующий матч или добавляем новый
            data['matches'][match.id] = match_data
            
            self._save_data(data)
            logging.info(f"Матч {match.id} сохранен в базу данных")
            
        except Exception as e:
            logging.error(f"Ошибка сохранения матча: {e}")
    
    def _load_data(self) -> Dict:
        """Загружает данные из файла"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {'matches': {}, 'last_update': datetime.now().isoformat()}
        except Exception as e:
            logging.error(f"Ошибка загрузки данных: {e}")
            return {'matches': {}, 'last_update': datetime.now().isoformat()}
    
    def _save_data(self, data: Dict):
        """Сохраняет данные в файл"""
        try:
            data['last_update'] = datetime.now().isoformat()
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Ошибка сохранения данных: {e}")

class TrueLiveBetBot:
    """Основной класс бота TrueLiveBet"""
    
    def __init__(self):
        self.setup_logging()
        
        self.parser = BetBoomParser()
        self.analyzer = MatchAnalyzer()
        self.notifier = TelegramNotifier()
        self.database = DatabaseManager()
        
        self.last_check_time = None
        self.notification_count = 0
        self.last_notification_time = None
    
    def setup_logging(self):
        """Настраивает логирование"""
        logging.basicConfig(
            level=getattr(logging, LOGGING_CONFIG['level']),
            format=LOGGING_CONFIG['format'],
            handlers=[
                logging.FileHandler(LOGGING_CONFIG['file'], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def run(self):
        """Запускает основной цикл бота"""
        logging.info("🎯 TrueLiveBet Bot запущен!")
        logging.info(f"⏰ Периодичность проверки: {PARSING_CONFIG['interval_minutes']} минут")
        
        try:
            while True:
                self.check_matches()
                
                # Ждем до следующей проверки
                wait_time = PARSING_CONFIG['interval_minutes'] * 60
                logging.info(f"⏳ Следующая проверка через {PARSING_CONFIG['interval_minutes']} минут")
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            logging.info("🛑 Бот остановлен пользователем")
        except Exception as e:
            logging.error(f"❌ Критическая ошибка: {e}")
            raise
    
    def check_matches(self):
        """Проверяет матчи и анализирует их"""
        try:
            logging.info("🔍 Начинаю проверку матчей...")
            
            # Получаем live матчи
            matches = self.parser.get_live_matches()
            
            if not matches:
                logging.info("📭 Live матчи не найдены")
                return
            
            # Анализируем каждый матч
            for match in matches:
                try:
                    analysis_result = self.analyzer.analyze_match(match)
                    
                    # Сохраняем в базу данных
                    self.database.save_match(match, analysis_result)
                    
                    # Отправляем уведомление если нужно
                    if analysis_result.should_notify:
                        if self._can_send_notification():
                            success = self.notifier.send_notification(analysis_result)
                            if success:
                                self.notification_count += 1
                                self.last_notification_time = datetime.now()
                        else:
                            logging.info(f"⏰ Уведомление для матча {match.id} отложено (лимит)")
                    
                except Exception as e:
                    logging.error(f"Ошибка анализа матча {match.id}: {e}")
                    continue
            
            self.last_check_time = datetime.now()
            logging.info(f"✅ Проверка завершена. Проанализировано {len(matches)} матчей")
            
        except Exception as e:
            logging.error(f"Ошибка проверки матчей: {e}")
    
    def _can_send_notification(self) -> bool:
        """Проверяет, можно ли отправить уведомление"""
        now = datetime.now()
        
        # Проверяем лимит в час
        if self.last_notification_time:
            time_since_last = now - self.last_notification_time
            if time_since_last.total_seconds() < NOTIFICATION_CONFIG['notification_cooldown_minutes'] * 60:
                return False
        
        # Проверяем общий лимит в час
        if self.notification_count >= NOTIFICATION_CONFIG['max_notifications_per_hour']:
            # Сбрасываем счетчик если прошел час
            if self.last_notification_time:
                time_since_last = now - self.last_notification_time
                if time_since_last.total_seconds() >= 3600:  # 1 час
                    self.notification_count = 0
                    return True
            return False
        
        return True

if __name__ == "__main__":
    bot = TrueLiveBetBot()
    bot.run()