# 🎯 TrueLiveBet - Анализ лайв матчей BetBoom

## 📊 Что это?

TrueLiveBet - это автоматическая система анализа лайв матчей на сайте BetBoom с возможностью автоматической отправки результатов в GitHub и рассылки через Telegram бот.

## 🚀 Основные возможности

- **🔍 Анализ лайв матчей** в реальном времени
- **📊 Категоризация ставок** по уровню риска
- **🤖 AI анализ** с использованием OpenAI/Anthropic
- **📱 Telegram интеграция** для рассылки прогнозов
- **🔄 Автоматическая синхронизация** с GitHub
- **🔔 Webhook система** для автоматических уведомлений

## 📁 Структура проекта

```
truelivebet/
├── analysis/                          # Результаты анализа
│   ├── live_analysis_results.md      # Анализ в markdown
│   ├── live_analysis_data.json      # Данные для бота
│   └── webhook_trigger.json         # Триггер для webhook
├── automation/                        # Автоматизация
│   ├── betboom_scraper.py           # Скрапер BetBoom
│   ├── ai_analyzer.py               # AI анализатор
│   ├── telegram_bot.py              # Telegram бот
│   ├── git_push_analysis.py         # Автоматическая отправка в GitHub
│   └── main.py                      # Основной скрипт
├── docs/                             # Документация
│   └── github_webhook_setup.md      # Настройка webhook
├── logs/                             # Логи системы
└── strategies/                       # Стратегии ставок
```

## 🎯 Категории ставок

- **💀 >95%** - Мертвые (требуют строгого анализа)
- **🎯 85–95%** - Идеальные
- **⭐ 80–85%** - Отличные  
- **👍 75–80%** - Хорошие

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка конфигурации

Отредактируйте `automation/config.py`:
```python
TELEGRAM_BOT_TOKEN = "ваш_токен_бота"
TELEGRAM_CHANNEL_ID = "@ваш_канал"
```

### 3. Запуск анализа

```bash
# Анализ лайв матчей
python automation/main.py

# Автоматическая отправка в GitHub
python automation/git_push_analysis.py
```

## 🔗 GitHub Webhook настройка

Для автоматической рассылки через Telegram бот:

1. **Настройте webhook** в GitHub репозитории
2. **Запустите webhook сервер** (см. `docs/github_webhook_setup.md`)
3. **Настройте Telegram бота** для автоматических уведомлений

## 📱 Telegram бот

Бот автоматически:
- 📊 Отправляет результаты анализа
- 🎯 Уведомляет о новых рекомендациях
- ⚠️ Предупреждает о высокорисковых ставках
- 🔄 Обновляет информацию каждые 30 минут

## 🔧 Автоматизация

### Cron задачи

```bash
# Анализ каждые 30 минут
*/30 * * * * cd /path/to/truelivebet && python automation/main.py

# Отправка в GitHub каждые 30 минут
*/30 * * * * cd /path/to/truelivebet && python automation/git_push_analysis.py
```

### Системный сервис

```bash
sudo systemctl enable truelivebet-webhook
sudo systemctl start truelivebet-webhook
```

## 📊 Последний анализ

**Время**: 17 августа 2025, 15:00 МСК  
**Всего матчей**: 132+  
**Статус**: ✅ Анализ завершен и отправлен в GitHub

### 🏆 Лучшие ставки

- **🎯 Ахмат vs Крылья Советов** - Победа Ахмата (1:0, 1Т)
- **⭐ Манчестер Сити** - Победа над Вулверхэмптоном (0:3, 2Т)

## 🛠️ Устранение неполадок

### Логи системы

```bash
tail -f logs/git_push_analysis.log
tail -f logs/telegram_bot.log
```

### Проверка статуса

```bash
git status
git log --oneline -5
```

## 📞 Поддержка

- 📧 Создайте issue в GitHub репозитории
- 📖 Изучите документацию в папке `docs/`
- 🔍 Проверьте логи в папке `logs/`

## 🔄 Обновления

```bash
git pull origin main
pip install -r requirements.txt
sudo systemctl restart truelivebet-webhook
```

## 📄 Лицензия

Проект разработан для образовательных целей. Используйте на свой страх и риск.

---

*Разработано с ❤️ для TrueLiveBet*  
*Версия: 1.0*  
*Последнее обновление: 17 августа 2025*
