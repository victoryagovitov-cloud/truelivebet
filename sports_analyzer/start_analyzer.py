#!/usr/bin/env python3
"""
Скрипт запуска анализатора спортивных событий
Может работать в режиме планировщика или одноразового анализа
"""

import sys
import os
import argparse
import asyncio

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import SportsAnalyzer


def main():
    parser = argparse.ArgumentParser(description='TrueLiveBet Sports Analyzer')
    parser.add_argument('--mode', choices=['schedule', 'once'], default='schedule',
                       help='Режим работы: schedule (циклический) или once (одноразовый)')
    parser.add_argument('--test', action='store_true',
                       help='Тестовый режим (не отправляет в Telegram)')
    
    args = parser.parse_args()
    
    analyzer = SportsAnalyzer()
    
    if args.mode == 'once':
        print("Запуск одноразового анализа...")
        asyncio.run(analyzer.run_analysis_cycle())
        print("Анализ завершен")
    else:
        print("Запуск планировщика (цикл 50 минут)...")
        print("Для остановки нажмите Ctrl+C")
        try:
            analyzer.start_scheduler()
        except KeyboardInterrupt:
            print("\nАнализатор остановлен пользователем")


if __name__ == "__main__":
    main()