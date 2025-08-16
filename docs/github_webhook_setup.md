# 🔗 Настройка GitHub Webhook для TrueLiveBet

## 📋 Обзор

Этот документ описывает настройку автоматической системы, которая:
1. Анализирует лайв матчи на BetBoom
2. Отправляет результаты в GitHub репозиторий
3. Запускает webhook для автоматической рассылки через Telegram бот

## 🚀 Быстрый старт

### 1. Настройка GitHub репозитория

```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/truelivebet.git
cd truelivebet

# Убедитесь, что у вас есть права на push
git remote -v
```

### 2. Настройка GitHub Webhook

1. Перейдите в ваш GitHub репозиторий
2. Нажмите **Settings** → **Webhooks**
3. Нажмите **Add webhook**
4. Заполните поля:
   - **Payload URL**: `https://your-domain.com/webhook/github`
   - **Content type**: `application/json`
   - **Secret**: Создайте секретный ключ
   - **Events**: Выберите `Just the push event`

### 3. Настройка сервера для webhook

Создайте файл `webhook_server.py`:

```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import subprocess
import json

app = Flask(__name__)

WEBHOOK_SECRET = "your_webhook_secret_here"
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
TELEGRAM_CHANNEL_ID = "@truelivebet"

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    # Проверяем подпись
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Парсим payload
    payload = request.json
    
    # Проверяем, что это push в main ветку
    if payload.get('ref') == 'refs/heads/main':
        # Запускаем телеграм бот
        send_telegram_notification()
        
        return jsonify({'status': 'success'}), 200
    
    return jsonify({'status': 'ignored'}), 200

def verify_signature(data, signature):
    if not signature:
        return False
    
    expected_signature = 'sha256=' + hmac.new(
        WEBHOOK_SECRET.encode(),
        data,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

def send_telegram_notification():
    """Запуск телеграм бота для рассылки"""
    try:
        # Запускаем скрипт телеграм бота
        subprocess.run([
            'python', 'automation/telegram_bot.py',
            '--mode', 'notify',
            '--source', 'github_webhook'
        ], check=True)
        
        print("Telegram notification sent successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"Error sending telegram notification: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 🔧 Детальная настройка

### Структура файлов

```
truelivebet/
├── analysis/
│   ├── live_analysis_results.md      # Результаты анализа в markdown
│   ├── live_analysis_data.json      # Данные для бота в JSON
│   └── webhook_trigger.json         # Триггер для webhook
├── automation/
│   ├── git_push_analysis.py         # Скрипт отправки в GitHub
│   ├── telegram_bot.py              # Telegram бот
│   └── main.py                      # Основной скрипт
└── docs/
    └── github_webhook_setup.md      # Этот файл
```

### Автоматизация процесса

1. **Анализ матчей** → `live_analysis_results.md` + `live_analysis_data.json`
2. **Git push** → `git_push_analysis.py`
3. **GitHub webhook** → Запуск сервера
4. **Telegram рассылка** → `telegram_bot.py`

## 📱 Настройка Telegram бота

### 1. Создание бота

1. Напишите [@BotFather](https://t.me/botfather) в Telegram
2. Создайте нового бота: `/newbot`
3. Получите токен бота

### 2. Настройка канала

1. Создайте канал в Telegram
2. Добавьте бота как администратора
3. Получите ID канала (начинается с `@` или `-`)

### 3. Обновление конфигурации

```python
# config.py
TELEGRAM_BOT_TOKEN = "your_bot_token_here"
TELEGRAM_CHANNEL_ID = "@your_channel_name"
```

## 🚀 Запуск системы

### 1. Ручной запуск

```bash
# Анализ матчей
python automation/main.py

# Отправка в GitHub
python automation/git_push_analysis.py

# Запуск webhook сервера
python webhook_server.py
```

### 2. Автоматический запуск (cron)

```bash
# Добавьте в crontab
*/30 * * * * cd /path/to/truelivebet && python automation/main.py
*/30 * * * * cd /path/to/truelivebet && python automation/git_push_analysis.py
```

### 3. Системный сервис

Создайте файл `/etc/systemd/system/truelivebet-webhook.service`:

```ini
[Unit]
Description=TrueLiveBet Webhook Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/truelivebet
ExecStart=/usr/bin/python3 webhook_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl enable truelivebet-webhook
sudo systemctl start truelivebet-webhook
```

## 🔍 Мониторинг и логи

### Логи системы

```bash
# Просмотр логов
tail -f logs/git_push_analysis.log
tail -f logs/telegram_bot.log

# Системные логи
sudo journalctl -u truelivebet-webhook -f
```

### Проверка статуса

```bash
# Проверка webhook
curl -X POST https://your-domain.com/webhook/github \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'

# Проверка git статуса
git status
git log --oneline -5
```

## 🛠️ Устранение неполадок

### Частые проблемы

1. **Webhook не срабатывает**
   - Проверьте URL в GitHub
   - Убедитесь, что сервер доступен из интернета
   - Проверьте логи сервера

2. **Git push не работает**
   - Проверьте права доступа к репозиторию
   - Убедитесь, что SSH ключи настроены
   - Проверьте статус git: `git status`

3. **Telegram бот не отправляет сообщения**
   - Проверьте токен бота
   - Убедитесь, что бот добавлен в канал
   - Проверьте права бота в канале

### Отладка

```bash
# Включение подробного логирования
export LOG_LEVEL=DEBUG

# Тестовый запуск
python -m automation.git_push_analysis --test
python -m automation.telegram_bot --test
```

## 📞 Поддержка

Если у вас возникли проблемы:

1. Проверьте логи системы
2. Убедитесь, что все зависимости установлены
3. Проверьте настройки конфигурации
4. Создайте issue в GitHub репозитории

## 🔄 Обновления

Для обновления системы:

```bash
git pull origin main
pip install -r requirements.txt
sudo systemctl restart truelivebet-webhook
```

---

*Документ создан для TrueLiveBet v1.0*
*Последнее обновление: 17 августа 2025*
