# 🤖 TrueLiveBet - Автоматизация

**Автоматический сбор данных с BetBoom, AI-анализ и отправка в Telegram**

## 🎯 Что это дает

✅ **Автоматический сбор** live матчей с BetBoom  
✅ **AI-анализ** по нашим правилам TrueLiveBet  
✅ **Telegram бот** для рассылки анализов  
✅ **Работа 24/7** без вмешательства человека  
✅ **Обход защиты** BetBoom через Playwright  

## 🏗️ Архитектура системы

```
BetBoom → Playwright Scraper → AI Analyzer → Telegram Bot
    ↓              ↓              ↓            ↓
Live матчи → Обработка данных → Анализ → Отправка пользователям
```

## 📁 Структура модуля

```
automation/
├── README.md              # Эта документация
├── requirements.txt       # Зависимости Python
├── main.py               # Главный модуль запуска
├── betboom_scraper.py    # Скрапер BetBoom
├── ai_analyzer.py        # AI анализатор матчей
├── telegram_bot.py       # Telegram бот
└── logs/                 # Папка для логов
```

## 🚀 Быстрый старт

### **Шаг 1: Установка зависимостей**

```bash
pip install -r requirements.txt
```

### **Шаг 2: Настройка переменных окружения**

Создайте файл `.env` в папке `automation/`:

```env
# Telegram Bot Token (обязательно)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# AI API ключи (опционально)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Тестовый чат ID
TEST_CHAT_ID=123456789
```

### **Шаг 3: Запуск системы**

```bash
python main.py
```

## 🔧 Компоненты системы

### **1. BetBoom Scraper (`betboom_scraper.py`)**

- **Технология**: Playwright (обход защиты)
- **Функции**: Сбор live матчей, коэффициентов, статистики
- **Особенности**: Автоматическое управление браузером

```python
from betboom_scraper import BetBoomScraper

scraper = BetBoomScraper()
await scraper.start_browser()
matches = await scraper.get_live_matches()
```

### **2. AI Analyzer (`ai_analyzer.py`)**

- **Модели**: OpenAI GPT-4, Anthropic Claude
- **Правила**: Наша система TrueLiveBet
- **Результат**: Категории 💀🎯⭐👍 с обоснованием

```python
from ai_analyzer import AIAnalyzer

analyzer = AIAnalyzer(openai_api_key="your_key")
result = await analyzer.analyze_match(match_data)
```

### **3. Telegram Bot (`telegram_bot.py`)**

- **Команды**: /start, /help, /analyze, /live, /stats
- **Функции**: Отправка анализов, интерактивные кнопки
- **Форматирование**: По нашим шаблонам TrueLiveBet

## ⚙️ Конфигурация

### **Основные параметры**

```python
config = {
    'cycle_interval': 300,        # Интервал анализа (5 мин)
    'openai_api_key': '...',      # OpenAI API ключ
    'anthropic_api_key': '...',   # Anthropic API ключ
    'telegram_token': '...',      # Telegram Bot Token
    'test_chat_id': 123456789     # Тестовый чат ID
}
```

### **Переменные окружения**

| Переменная | Описание | Обязательно |
|------------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Токен Telegram бота | ✅ |
| `OPENAI_API_KEY` | OpenAI API ключ | ❌ |
| `ANTHROPIC_API_KEY` | Anthropic API ключ | ❌ |
| `TEST_CHAT_ID` | ID тестового чата | ❌ |

## 📊 Логирование

Система ведет подробные логи:

- **`logs/automation.log`** - общие логи автоматизации
- **`logs/betboom_scraper.log`** - логи скрапера
- **`logs/main.log`** - логи главного модуля

## 🔄 Цикл работы

1. **Сбор данных** (каждые 5 минут)
2. **AI-анализ** всех live матчей
3. **Фильтрация** по критериям (≥75% уверенности)
4. **Отправка** в Telegram активным пользователям

## 🛡️ Безопасность

- **Обход защиты**: Playwright с настройками браузера
- **User-Agent**: Реалистичные заголовки
- **Задержки**: Анти-детект механизмы
- **Логирование**: Отслеживание ошибок

## 🚨 Ограничения

- **BetBoom защита**: Может потребовать настройки
- **API лимиты**: OpenAI/Anthropic имеют ограничения
- **Telegram**: Лимиты на отправку сообщений
- **Ресурсы**: Требует стабильный интернет

## 🆘 Устранение неполадок

### **Проблема: Не собираются данные с BetBoom**

**Решение:**
1. Проверьте интернет соединение
2. Обновите селекторы в `betboom_scraper.py`
3. Измените `headless=False` для отладки

### **Проблема: AI анализ не работает**

**Решение:**
1. Проверьте API ключи
2. Убедитесь в наличии средств на счете
3. Проверьте лимиты API

### **Проблема: Telegram бот не отвечает**

**Решение:**
1. Проверьте токен бота
2. Убедитесь, что бот не заблокирован
3. Проверьте права бота

## 📈 Мониторинг

### **Статистика в реальном времени**

```python
status = automation.get_status()
print(f"Статус: {status['status']}")
print(f"Матчей проанализировано: {status['stats']['matches_analyzed']}")
print(f"Анализов отправлено: {status['stats']['analyses_sent']}")
```

### **Команды бота для мониторинга**

- `/stats` - статистика бота
- `/about` - информация о проекте
- `/help` - справка по командам

## 🔮 Развитие

### **Планируемые улучшения**

- [ ] Веб-интерфейс для мониторинга
- [ ] База данных для хранения анализов
- [ ] Уведомления о критических ошибках
- [ ] Интеграция с другими букмекерами
- [ ] Машинное обучение на основе результатов

### **Вклад в проект**

Присоединяйтесь к разработке! Создавайте Issues и Pull Requests на GitHub.

## 📞 Поддержка

- **Разработчик**: Виктор Яговитов
- **GitHub**: [victoryagovitov-cloud/truelivebet](https://github.com/victoryagovitov-cloud/truelivebet)
- **Telegram**: @victor_yagovitov

---

**TrueLiveBet - Честный анализ без вилок и договорняков!** 🎯
