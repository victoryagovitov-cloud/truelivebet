#!/usr/bin/env python3
"""
TrueLiveBet - Telegram бот для отправки анализов
Автор: Виктор
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from loguru import logger
from ai_analyzer import AnalysisResult

class TrueLiveBetBot:
    """Telegram бот для TrueLiveBet"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        
        # Статистика бота
        self.stats = {
            'users': set(),
            'analyses_sent': 0,
            'start_time': datetime.now()
        }
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        
        # Основные команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("about", self.about_command))
        
        # Команды анализа
        self.application.add_handler(CommandHandler("analyze", self.analyze_command))
        self.application.add_handler(CommandHandler("live", self.live_command))
        
        # Обработка нажатий на кнопки
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Обработка текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user
        self.stats['users'].add(user.id)
        
        welcome_text = f"""
🎯 **Добро пожаловать в TrueLiveBet!**

Привет, {user.first_name}! Я - ваш AI-помощник для анализа лайв-ставок.

🏆 **Что я умею:**
• Анализировать live матчи с BetBoom
• Использовать нашу систему TrueLiveBet
• Давать рекомендации с обоснованием
• Отслеживать статистику успешности

🚀 **Команды:**
/analyze - Анализ конкретного матча
/live - Текущие live матчи
/stats - Статистика бота
/help - Справка по командам
/about - О проекте

💡 **Наша миссия:** Честный анализ без вилок и договорняков!

Начните с команды /live для просмотра текущих матчей.
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Live матчи", callback_data="live_matches")],
            [InlineKeyboardButton("🎯 Анализ", callback_data="analyze")],
            [InlineKeyboardButton("📚 Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        help_text = """
📚 **Справка по командам TrueLiveBet:**

🎯 **Основные команды:**
/start - Запуск бота
/help - Эта справка
/about - О проекте TrueLiveBet

📊 **Анализ матчей:**
/analyze - Анализ конкретного матча
/live - Просмотр live матчей
/stats - Статистика бота

💡 **Как использовать:**
1. Используйте /live для просмотра текущих матчей
2. Выберите интересующий матч
3. Получите AI-анализ по нашим правилам
4. Принимайте обоснованные решения

🏆 **Наша система анализа:**
• Строгий анализ (💀🎯⭐👍)
• Проверенная статистика
• Честные рекомендации
• Без вилок и договорняков

❓ **Вопросы?** Обращайтесь к @victor_yagovitov
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /about"""
        about_text = """
🏆 **TrueLiveBet - Честный канал лайв-ставок**

🎯 **Наша миссия:**
Создать прозрачное сообщество вокруг честного беттинга, где каждый подписчик получает качественный анализ и может принимать обоснованные решения.

✅ **Что мы предлагаем:**
• Строгий анализ по системе
• Простой анализ с вероятностью ~80%
• Реальные данные (scores24.live, 4Score.ru, Transfermarkt)
• Образование и банкролл-менеджмент
• Сообщество единомышленников

🚫 **Что мы НЕ делаем:**
• Вилки и договорняки
• Реферальные ссылки
• Прогнозы на будущее
• Политические/религиозные обсуждения

🏈 **Виды спорта:**
⚽ Футбол, 🎾 Теннис, 🏀 Баскетбол, 🤾 Гандбол, 🏓 Настольный теннис

👨‍💻 **Разработчик:** Виктор Яговитов
🌐 **GitHub:** https://github.com/victoryagovitov-cloud/truelivebet

💡 **Принцип:** Качество анализа важнее быстрой прибыли!
        """
        
        await update.message.reply_text(about_text, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /stats"""
        uptime = datetime.now() - self.stats['start_time']
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        
        stats_text = f"""
📊 **Статистика TrueLiveBet Bot:**

👥 **Пользователи:** {len(self.stats['users'])}
📈 **Анализов отправлено:** {self.stats['analyses_sent']}
⏱ **Время работы:** {hours}ч {minutes}м
🕐 **Запущен:** {self.stats['start_time'].strftime('%d.%m.%Y %H:%M')}

🎯 **Статус:** Активен и готов к работе!
        """
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    async def live_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /live - показать live матчи"""
        # Здесь будет интеграция с BetBoom скрапером
        live_text = """
📊 **Live матчи (обновление...)**

🔄 **Получаю данные с BetBoom...**
⏳ Пожалуйста, подождите...

💡 **Пока что используйте команду /analyze для анализа конкретных матчей.**
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить", callback_data="refresh_live")],
            [InlineKeyboardButton("🎯 Анализ", callback_data="analyze")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(live_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /analyze - анализ матча"""
        analyze_text = """
🎯 **Анализ матча TrueLiveBet**

📝 **Введите данные матча в формате:**
```
Спорт: Футбол
Команда 1: Барселона
Команда 2: Реал Мадрид
Счет: 2:0
Время: 75'
```

💡 **Или используйте кнопки ниже для выбора:**
        """
        
        keyboard = [
            [InlineKeyboardButton("⚽ Футбол", callback_data="sport_football")],
            [InlineKeyboardButton("🎾 Теннис", callback_data="sport_tennis")],
            [InlineKeyboardButton("🏀 Баскетбол", callback_data="sport_basketball")],
            [InlineKeyboardButton("🤾 Гандбол", callback_data="sport_handball")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(analyze_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "live_matches":
            await self.live_command(update, context)
        elif query.data == "analyze":
            await self.analyze_command(update, context)
        elif query.data == "help":
            await self.help_command(update, context)
        elif query.data == "refresh_live":
            await query.edit_message_text("🔄 Обновляю live матчи...")
            # Здесь будет логика обновления
        elif query.data.startswith("sport_"):
            sport = query.data.replace("sport_", "")
            await self.handle_sport_selection(query, sport)
    
    async def handle_sport_selection(self, query, sport: str):
        """Обработка выбора вида спорта"""
        sport_names = {
            "football": "⚽ Футбол",
            "tennis": "🎾 Теннис", 
            "basketball": "🏀 Баскетбол",
            "handball": "🤾 Гандбол"
        }
        
        sport_name = sport_names.get(sport, sport)
        
        text = f"""
{sport_name} - Выберите действие:

🎯 **Анализ live матча**
📊 **Просмотр статистики**
📈 **История встреч**
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 Live анализ", callback_data=f"analyze_{sport}")],
            [InlineKeyboardButton("📊 Статистика", callback_data=f"stats_{sport}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="analyze")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text
        
        # Простая логика анализа текста
        if "анализ" in text.lower() or "анализируй" in text.lower():
            await update.message.reply_text("🎯 Для анализа матча используйте команду /analyze")
        elif "помощь" in text.lower() or "help" in text.lower():
            await self.help_command(update, context)
        else:
            await update.message.reply_text("💡 Используйте команду /help для получения справки")
    
    async def send_analysis(self, chat_id: int, analysis: AnalysisResult):
        """Отправка результата анализа"""
        try:
            # Форматируем сообщение по нашим шаблонам
            message = self._format_analysis_message(analysis)
            
            # Отправляем сообщение
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
            # Обновляем статистику
            self.stats['analyses_sent'] += 1
            
            logger.info(f"Анализ отправлен в чат {chat_id}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки анализа: {e}")
    
    def _format_analysis_message(self, analysis: AnalysisResult) -> str:
        """Форматирование сообщения анализа по нашим шаблонам"""
        
        # Определяем категорию
        category_emoji = analysis.category
        category_name = {
            "💀": "МЕРТВЫЕ (>95%)",
            "🎯": "ИДЕАЛЬНЫЕ (85-95%)", 
            "⭐": "ОТЛИЧНЫЕ (80-85%)",
            "👍": "ХОРОШИЕ (75-80%)"
        }.get(analysis.category, "АНАЛИЗ")
        
        message = f"""
{category_emoji} **{category_name}**

🎯 **Рекомендация:** {analysis.recommendation}
📊 **Уверенность:** {analysis.confidence:.1f}%
⚠️ **Риск:** {analysis.risk_level}

💡 **Обоснование:**
{analysis.reasoning}

⏰ **Время анализа:** {analysis.timestamp}
🏆 **TrueLiveBet - честный анализ!**
        """
        
        return message
    
    async def start_bot(self):
        """Запуск бота"""
        try:
            logger.info("Запуск TrueLiveBet Telegram бота...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            logger.info("Бот запущен успешно!")
            
            # Держим бота запущенным
            await self.application.updater.idle()
            
        except Exception as e:
            logger.error(f"Ошибка запуска бота: {e}")
            raise
    
    async def stop_bot(self):
        """Остановка бота"""
        try:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Бот остановлен")
        except Exception as e:
            logger.error(f"Ошибка остановки бота: {e}")

# Пример использования
async def main():
    """Основная функция"""
    # Замените на свой токен
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    
    bot = TrueLiveBetBot(TOKEN)
    
    try:
        await bot.start_bot()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    finally:
        await bot.stop_bot()

if __name__ == "__main__":
    asyncio.run(main())
