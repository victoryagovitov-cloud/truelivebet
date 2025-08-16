#!/usr/bin/env python3
"""
TrueLiveBet - Публикация прогнозов в Telegram канал
Автор: Виктор
"""

import asyncio
from datetime import datetime
from typing import List, Dict
from loguru import logger
from ai_analyzer import AnalysisResult

class ChannelPublisher:
    """Публикация прогнозов в Telegram канал"""
    
    def __init__(self, bot, channel_id: str):
        self.bot = bot
        self.channel_id = channel_id
        self.published_count = 0
        
    async def publish_analysis(self, analysis: AnalysisResult) -> bool:
        """Публикация анализа в канал"""
        try:
            # Форматируем сообщение для канала
            message = self._format_channel_message(analysis)
            
            # Публикуем в канал
            await self.bot.application.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode='Markdown'
            )
            
            self.published_count += 1
            logger.info(f"✅ Анализ опубликован в канал {self.channel_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка публикации в канал: {e}")
            return False
    
    async def publish_batch(self, analyses: List[AnalysisResult]) -> Dict[str, int]:
        """Пакетная публикация анализов"""
        results = {
            'success': 0,
            'failed': 0,
            'total': len(analyses)
        }
        
        for analysis in analyses:
            try:
                success = await self.publish_analysis(analysis)
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                
                # Небольшая задержка между публикациями
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"Ошибка публикации анализа: {e}")
                results['failed'] += 1
                continue
        
        logger.info(f"📊 Пакетная публикация завершена: {results}")
        return results
    
    def _format_channel_message(self, analysis: AnalysisResult) -> str:
        """Форматирование сообщения для канала"""
        
        # Определяем категорию и название
        category_emoji = analysis.category
        category_name = {
            "💀": "МЕРТВЫЕ (>95%)",
            "🎯": "ИДЕАЛЬНЫЕ (85-95%)", 
            "⭐": "ОТЛИЧНЫЕ (80-85%)",
            "👍": "ХОРОШИЕ (75-80%)"
        }.get(analysis.category, "АНАЛИЗ")
        
        # Форматируем время
        try:
            timestamp = datetime.fromisoformat(analysis.timestamp)
            time_str = timestamp.strftime("%H:%M")
        except:
            time_str = "сейчас"
        
        message = f"""
{category_emoji} **{category_name}** | {time_str}

🎯 **Рекомендация:** {analysis.recommendation}
📊 **Уверенность:** {analysis.confidence:.1f}%
⚠️ **Риск:** {analysis.risk_level}

💡 **Обоснование:**
{analysis.reasoning}

🏆 **TrueLiveBet - честный анализ!**
        """
        
        return message.strip()
    
    async def publish_summary(self, analyses: List[AnalysisResult]) -> bool:
        """Публикация сводки по всем анализам"""
        try:
            if not analyses:
                return False
            
            # Группируем по категориям
            categories = {}
            for analysis in analyses:
                cat = analysis.category
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(analysis)
            
            # Формируем сводку
            summary = f"""
📊 **СВОДКА АНАЛИЗОВ | {datetime.now().strftime('%H:%M')}**

🎯 **Всего проанализировано:** {len(analyses)} матчей
"""
            
            for cat, cat_analyses in categories.items():
                cat_name = {
                    "💀": "МЕРТВЫЕ",
                    "🎯": "ИДЕАЛЬНЫЕ", 
                    "⭐": "ОТЛИЧНЫЕ",
                    "👍": "ХОРОШИЕ"
                }.get(cat, "ДРУГИЕ")
                
                summary += f"\n{cat} **{cat_name}:** {len(cat_analyses)}"
            
            summary += f"""

📈 **Успешно опубликовано:** {self.published_count}
⏰ **Время:** {datetime.now().strftime('%H:%M')}

🏆 **TrueLiveBet - честный анализ!**
            """
            
            # Публикуем сводку
            await self.bot.application.bot.send_message(
                chat_id=self.channel_id,
                text=summary.strip(),
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Сводка опубликована в канал {self.channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка публикации сводки: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Получение статистики публикаций"""
        return {
            'channel_id': self.channel_id,
            'published_count': self.published_count,
            'last_published': datetime.now().isoformat()
        }

# Пример использования
async def test_publisher():
    """Тестирование издателя"""
    from config import TELEGRAM_CHANNEL_ID
    
    print(f"📢 Тестирование издателя канала: {TELEGRAM_CHANNEL_ID}")
    
    # Создаем тестовый анализ
    test_analysis = AnalysisResult(
        match_id="test_match",
        confidence=85.5,
        recommendation="Ставить на победу команды 1",
        reasoning="Команда 1 ведет 2:0, контроль мяча 65%, удары 8:2",
        risk_level="средний",
        category="🎯",
        timestamp=datetime.now().isoformat()
    )
    
    print(f"✅ Тестовый анализ создан: {test_analysis.category} - {test_analysis.confidence:.1f}%")
    
    # Здесь можно протестировать форматирование
    publisher = ChannelPublisher(None, TELEGRAM_CHANNEL_ID)
    message = publisher._format_channel_message(test_analysis)
    
    print("\n📝 Пример сообщения для канала:")
    print("=" * 50)
    print(message)
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_publisher())
