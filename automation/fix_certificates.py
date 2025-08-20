#!/usr/bin/env python3
"""
TrueLiveBet - Исправление проблем с сертификатами
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Выполнение команды с описанием"""
    print(f"\n🔧 {description}...")
    print(f"   Команда: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Успешно: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Ошибка: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   💥 Исключение: {e}")
        return False

def fix_certificates():
    """Исправление проблем с сертификатами"""
    print("🚀 TrueLiveBet - Исправление сертификатов")
    print("=" * 50)
    
    # Список команд для исправления
    fixes = [
        {
            'command': 'pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org certifi --upgrade',
            'description': 'Обновление certifi'
        },
        {
            'command': 'pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org requests[security]',
            'description': 'Установка безопасных requests'
        },
        {
            'command': 'pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org urllib3',
            'description': 'Установка urllib3'
        }
    ]
    
    success_count = 0
    for fix in fixes:
        if run_command(fix['command'], fix['description']):
            success_count += 1
    
    print(f"\n📊 Результат: {success_count}/{len(fixes)} исправлений выполнено")
    return success_count == len(fixes)

def install_dependencies():
    """Установка всех зависимостей"""
    print("\n📦 Установка зависимостей TrueLiveBet...")
    print("=" * 50)
    
    # Основные зависимости
    dependencies = [
        'playwright',
        'selenium', 
        'requests',
        'beautifulsoup4',
        'fastapi',
        'uvicorn',
        'pydantic',
        'pandas',
        'numpy',
        'schedule',
        'apscheduler',
        'pyyaml'
    ]
    
    success_count = 0
    for dep in dependencies:
        command = f'pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org {dep}'
        if run_command(command, f'Установка {dep}'):
            success_count += 1
    
    print(f"\n📊 Зависимости: {success_count}/{len(dependencies)} установлено")
    return success_count == len(dependencies)

def test_system():
    """Тестирование системы после исправления"""
    print("\n🧪 Тестирование системы...")
    print("=" * 50)
    
    # Тест 1: Проверка pip
    if run_command('pip --version', 'Проверка pip'):
        print("   ✅ pip работает корректно")
    else:
        print("   ❌ Проблемы с pip")
        return False
    
    # Тест 2: Проверка установленных пакетов
    if run_command('pip list | findstr "certifi"', 'Проверка certifi'):
        print("   ✅ certifi установлен")
    else:
        print("   ❌ certifi не найден")
        return False
    
    # Тест 3: Тест импортов
    try:
        import config
        print("   ✅ Конфигурация загружается")
    except Exception as e:
        print(f"   ❌ Ошибка конфигурации: {e}")
        return False
    
    try:
        from telegram_bot import TrueLiveBetBot
        print("   ✅ Telegram бот импортируется")
    except Exception as e:
        print(f"   ❌ Ошибка импорта бота: {e}")
        return False
    
    return True

def main():
    """Главная функция"""
    print("🎯 TrueLiveBet - Комплексное исправление системы")
    print("=" * 60)
    
    # Шаг 1: Исправление сертификатов
    if not fix_certificates():
        print("\n❌ Не удалось исправить сертификаты")
        return False
    
    # Шаг 2: Установка зависимостей
    if not install_dependencies():
        print("\n❌ Не удалось установить зависимости")
        return False
    
    # Шаг 3: Тестирование
    if not test_system():
        print("\n❌ Система не прошла тестирование")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ВСЕ ПРОБЛЕМЫ ИСПРАВЛЕНЫ!")
    print("\n📱 Теперь можно:")
    print("1. Протестировать бота: python test_bot.py")
    print("2. Запустить систему: python main.py")
    print("3. Или запустить тестовую версию: python test_system.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Система готова к работе!")
        else:
            print("\n❌ Есть проблемы, требующие ручного исправления")
    except KeyboardInterrupt:
        print("\n⏹️ Исправление прервано пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
