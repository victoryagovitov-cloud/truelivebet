# 🤖 Настройка Telegram бота для TrueLiveBet

## 📋 Что нужно сделать

### 1. **Создать Telegram бота**
1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Придумайте имя для бота (например: "TrueLiveBet Bot")
4. Придумайте username (например: "TrueLiveBetBot")
5. Сохраните **BOT TOKEN** (выглядит как `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. **Получить Chat ID**
1. Добавьте бота в чат или группу
2. Отправьте любое сообщение в чат
3. Откройте в браузере: `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
4. Найдите `"chat":{"id":123456789}` - это ваш Chat ID

### 3. **Настроить конфигурацию**
Откройте файл `config.py` и замените:

```python
TELEGRAM_CONFIG = {
    'bot_token': '123456789:ABCdefGHIjklMNOpqrsTUVwxyz',  # Ваш токен
    'chat_id': '123456789',                                # Ваш Chat ID
    'bot_username': 'TrueLiveBetBot'                       # Username бота
}
```

## 🚀 Запуск бота

### **Вариант 1: Запуск в фоне**
```bash
python3 auto_analyzer.py &
```

### **Вариант 2: Запуск с логированием**
```bash
python3 auto_analyzer.py > bot.log 2>&1 &
```

### **Вариант 3: Запуск через screen (рекомендуется)**
```bash
screen -S truelivebet
python3 auto_analyzer.py
# Нажмите Ctrl+A, затем D для выхода из screen
# Вернуться: screen -r truelivebet
```

## 📱 Тестирование бота

### **1. Проверка подключения**
```bash
curl "https://api.telegram.org/bot<BOT_TOKEN>/getMe"
```

### **2. Отправка тестового сообщения**
```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>&text=🎯 TrueLiveBet Bot работает!"
```

### **3. Проверка логов**
```bash
tail -f truelivebet.log
```

## ⚙️ Настройки

### **Периодичность проверки**
В `config.py`:
```python
PARSING_CONFIG = {
    'interval_minutes': 30,  # Измените на нужное значение
}
```

### **Критерии анализа**
```python
ANALYSIS_CRITERIA = {
    'football': {
        'min_goal_difference': 2,      # Минимальная разница в голах
        'min_control_percentage': 60,  # Минимальный контроль мяча
        'min_time_elapsed': 60,        # Минимальное время матча
        'confidence_threshold': 75     # Порог для уведомления
    }
}
```

### **Лимиты уведомлений**
```python
NOTIFICATION_CONFIG = {
    'max_notifications_per_hour': 10,     # Максимум в час
    'notification_cooldown_minutes': 5,   # Задержка между уведомлениями
}
```

## 🔧 Устранение неполадок

### **Бот не отвечает**
1. Проверьте токен и Chat ID
2. Убедитесь, что бот добавлен в чат
3. Проверьте логи: `tail -f truelivebet.log`

### **Ошибки парсинга**
1. BetBoom может блокировать запросы
2. Измените User-Agent в `config.py`
3. Добавьте задержки между запросами

### **Слишком много уведомлений**
1. Увеличьте `confidence_threshold`
2. Уменьшите `max_notifications_per_hour`
3. Увеличьте `notification_cooldown_minutes`

## 📊 Мониторинг

### **Статус бота**
```bash
ps aux | grep auto_analyzer
```

### **Последние логи**
```bash
tail -20 truelivebet.log
```

### **База данных**
```bash
cat data/matches_history.json | python3 -m json.tool
```

## 🌟 Примеры сообщений

### **Футбольный матч:**
```
🎯 TrueLiveBet - Найден подходящий матч!

⚽ Вид спорта: ⚽ Football
🏆 Матч: Барселона vs Реал Мадрид
📊 Счет: 2:0
⏰ Время: 65'
📈 Уверенность: 80%

💡 Рекомендация: Победа Барселона

🔍 Обоснование:
• Фаворит ведет на 2 гола
• Время матча: 65 минут

🔗 Смотреть матч

⏰ Анализ: 15:30:45
```

## 🔐 Безопасность

### **Не публикуйте токен бота!**
- Токен дает полный доступ к боту
- Храните в безопасном месте
- Используйте переменные окружения в продакшене

### **Ограничения Telegram API**
- Максимум 30 сообщений в секунду
- Максимум 20 сообщений в минуту
- Размер сообщения: до 4096 символов

## 📞 Поддержка

При проблемах:
1. Проверьте логи: `truelivebet.log`
2. Убедитесь в правильности настроек
3. Проверьте подключение к интернету
4. Убедитесь, что BetBoom доступен

---

**TrueLiveBet Bot** - автоматический анализ ставок! 🎯✨