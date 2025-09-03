# 🚀 TrueLiveBet Agent - Файлы для скачивания

## 📦 Что включено в архив:

### 🎯 Основные файлы агента:
- **sports_analyzer/** - Полная система анализа спортивных событий
- **send_to_telegram*.py** - Различные отправители в Telegram
- **smart_telegram_sender.py** - Умный отправитель
- **telegram_config.py** - Конфигурация Telegram
- **auto_*.py** - Автоматические скрипты
- ***.bat** - Батники для Windows
- ***.json** - Конфигурационные файлы
- **requirements_telegram.txt** - Зависимости

### 📊 Рекомендации и анализы:
- **recommendations/** - Папка с готовыми рекомендациями
- **analysis/** - Папка с результатами анализов

### 📁 Готовые архивы:
- **truelivebet_agent_files.tar.gz** (99K) - основные файлы агента
- **truelivebet_recommendations.tar.gz** (16K) - рекомендации и анализы  
- **truelivebet_agent_complete.tar.gz** (117K) - полный архив

## 🚀 Как запустить агента:

### 1. Установка зависимостей:
```bash
cd sports_analyzer
pip3 install -r requirements.txt
```

### 2. Одноразовый анализ:
```bash
cd sports_analyzer
python3 start_analyzer.py --mode once
```

### 3. Отправка в Telegram:
```bash
python3 send_to_telegram_smart.py
```

### 4. Автоматический режим (Windows):
```bash
start_auto_analysis.bat
```

## ⚙️ Настройка:

1. **Telegram токен**: Обновите `telegram_config.py`
2. **Claude API**: Настройте API ключ в `sports_analyzer/config/`
3. **Канал**: Укажите ваш Telegram канал

## 📱 Статус системы:

- ✅ **Агент работает** - успешно анализирует live матчи
- ✅ **Telegram интеграция** - отправляет в канал @truelivebet
- ✅ **Последнее сообщение** - ID: 422 успешно отправлено
- ⚠️ **Claude API** - нужно настроить API ключ

## 🎯 Виды спорта:

- ⚽ **Футбол** - анализ live матчей
- 🎾 **Теннис** - анализ по сетам и геймам
- 🏓 **Настольный теннис** - анализ по сетам
- 🤾 **Гандбол** - анализ прямых побед и тоталов

## 📞 Поддержка:

Все файлы готовы к использованию. Агент полностью функционален и готов к работе!

---
**Дата создания архива:** 03.09.2025, 21:19 МСК
**Статус:** ✅ Готов к использованию