#!/usr/bin/env python3
"""
TrueLiveBet - Автоматическая отправка результатов анализа в GitHub
Автор: Виктор
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
from loguru import logger

class GitAnalysisPusher:
    """Класс для автоматической отправки результатов анализа в GitHub"""
    
    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or os.getcwd()
        self.analysis_dir = Path(self.repo_path) / "analysis"
        self.git_dir = Path(self.repo_path) / ".git"
        
    def check_git_repo(self) -> bool:
        """Проверка, что это git репозиторий"""
        if not self.git_dir.exists():
            logger.error("Не найден .git каталог. Это не git репозиторий.")
            return False
        return True
    
    def check_git_status(self) -> dict:
        """Проверка статуса git репозитория"""
        try:
            # Проверяем статус
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Проверяем текущую ветку
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            current_branch = branch_result.stdout.strip()
            
            return {
                "has_changes": bool(result.stdout.strip()),
                "changes": result.stdout.strip().split('\n') if result.stdout.strip() else [],
                "current_branch": current_branch,
                "status": "clean" if not result.stdout.strip() else "dirty"
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка проверки git статуса: {e}")
            return {"error": str(e)}
    
    def add_files(self, files: list) -> bool:
        """Добавление файлов в git"""
        try:
            for file_path in files:
                full_path = Path(self.repo_path) / file_path
                if full_path.exists():
                    subprocess.run(
                        ["git", "add", str(file_path)],
                        cwd=self.repo_path,
                        check=True
                    )
                    logger.info(f"Добавлен файл: {file_path}")
                else:
                    logger.warning(f"Файл не найден: {file_path}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка добавления файлов: {e}")
            return False
    
    def commit_changes(self, message: str) -> bool:
        """Создание коммита"""
        try:
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                check=True
            )
            logger.info(f"Создан коммит: {message}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка создания коммита: {e}")
            return False
    
    def push_to_remote(self, remote: str = "origin", branch: str = None) -> bool:
        """Отправка изменений в удаленный репозиторий"""
        try:
            if not branch:
                # Получаем текущую ветку
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                branch = result.stdout.strip()
            
            subprocess.run(
                ["git", "push", remote, branch],
                cwd=self.repo_path,
                check=True
            )
            
            logger.info(f"Изменения отправлены в {remote}/{branch}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка отправки в удаленный репозиторий: {e}")
            return False
    
    def push_analysis_results(self, analysis_files: list = None) -> bool:
        """Основной метод для отправки результатов анализа"""
        
        if not self.check_git_repo():
            return False
        
        # Проверяем статус
        status = self.check_git_status()
        if "error" in status:
            logger.error(f"Ошибка проверки статуса: {status['error']}")
            return False
        
        if status["status"] == "clean":
            logger.info("Нет изменений для коммита")
            return True
        
        # Определяем файлы для добавления
        if not analysis_files:
            analysis_files = [
                "analysis/live_analysis_results.md",
                "analysis/live_analysis_data.json"
            ]
        
        # Добавляем файлы
        if not self.add_files(analysis_files):
            return False
        
        # Создаем коммит
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"📊 Обновление анализа лайв матчей BetBoom - {timestamp}"
        
        if not self.commit_changes(commit_message):
            return False
        
        # Отправляем в удаленный репозиторий
        if not self.push_to_remote():
            return False
        
        logger.success("✅ Результаты анализа успешно отправлены в GitHub")
        return True
    
    def create_webhook_trigger(self) -> bool:
        """Создание файла-триггера для webhook"""
        try:
            trigger_file = self.analysis_dir / "webhook_trigger.json"
            
            trigger_data = {
                "trigger_id": f"webhook_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "action": "telegram_notification",
                "status": "pending",
                "files": [
                    "live_analysis_results.md",
                    "live_analysis_data.json"
                ]
            }
            
            with open(trigger_file, 'w', encoding='utf-8') as f:
                json.dump(trigger_data, f, ensure_ascii=False, indent=2)
            
            logger.info("Создан файл-триггер для webhook")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания webhook триггера: {e}")
            return False

def main():
    """Основная функция"""
    
    # Настройка логирования
    logger.add("logs/git_push_analysis.log", rotation="1 day", retention="7 days")
    
    # Создаем экземпляр класса
    pusher = GitAnalysisPusher()
    
    # Отправляем результаты анализа
    success = pusher.push_analysis_results()
    
    if success:
        # Создаем webhook триггер
        pusher.create_webhook_trigger()
        logger.success("🎯 Анализ готов к рассылке через Telegram бот!")
    else:
        logger.error("❌ Ошибка отправки результатов анализа")

if __name__ == "__main__":
    main()
