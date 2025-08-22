"""
Сервис для управления пользователями и их контекстом
"""
import asyncio
import pickle
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger

# Исправляем импорты
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user_context import UserContext, UserProgress, LearningModule, Achievement

class UserService:
    """Сервис для управления пользователями"""

    def __init__(self, storage_path: str = "user_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.users_cache: Dict[int, UserContext] = {}
        self._lock = asyncio.Lock()

    async def get_user_context(self, user_id: int, chat_id: int) -> UserContext:
        """Получить контекст пользователя"""
        async with self._lock:
            if user_id in self.users_cache:
                return self.users_cache[user_id]

            # Загружаем из файла
            context = await self._load_user_context(user_id, chat_id)
            self.users_cache[user_id] = context
            return context

    async def save_user_context(self, user_context: UserContext):
        """Сохранить контекст пользователя"""
        async with self._lock:
            self.users_cache[user_context.user_id] = user_context
            await self._save_user_context(user_context)

    async def _load_user_context(self, user_id: int, chat_id: int) -> UserContext:
        """Загрузить контекст пользователя из файла"""
        user_file = self.storage_path / f"user_{user_id}.pkl"

        try:
            if user_file.exists():
                def load_data():
                    with open(user_file, 'rb') as f:
                        return pickle.load(f)

                context = await asyncio.to_thread(load_data)
                logger.info(f"Загружен контекст пользователя {user_id}")
                return context
        except Exception as e:
            logger.error(f"Ошибка загрузки контекста пользователя {user_id}: {e}")

        # Создаем новый контекст
        context = UserContext(user_id=user_id, chat_id=chat_id)
        logger.info(f"Создан новый контекст для пользователя {user_id}")
        return context

    async def _save_user_context(self, user_context: UserContext):
        """Сохранить контекст пользователя в файл"""
        user_file = self.storage_path / f"user_{user_context.user_id}.pkl"

        try:
            def save_data():
                with open(user_file, 'wb') as f:
                    pickle.dump(user_context, f)

            await asyncio.to_thread(save_data)
            logger.debug(f"Контекст пользователя {user_context.user_id} сохранен")
        except Exception as e:
            logger.error(f"Ошибка сохранения контекста пользователя {user_context.user_id}: {e}")

    async def update_user_progress(self, user_id: int, **kwargs) -> UserContext:
        """Обновить прогресс пользователя"""
        context = await self.get_user_context(user_id, 0)

        # Обновляем поля прогресса
        for key, value in kwargs.items():
            if hasattr(context.progress, key):
                setattr(context.progress, key, value)

        context.progress.session_count += 1
        context.progress.last_session_date = datetime.now()

        await self.save_user_context(context)
        return context

    async def add_achievement(self, user_id: int, achievement: Achievement) -> bool:
        """Добавить достижение пользователю"""
        context = await self.get_user_context(user_id, 0)

        if context.progress.add_achievement(achievement):
            await self.save_user_context(context)
            logger.info(f"Пользователь {user_id} получил достижение {achievement.value}")
            return True

        return False

    async def complete_module(self, user_id: int, module: LearningModule) -> bool:
        """Завершить модуль обучения"""
        context = await self.get_user_context(user_id, 0)

        if context.progress.complete_module(module):
            # Переходим к следующему модулю
            next_module_value = module.value + 1
            for next_module in LearningModule:
                if next_module.value == next_module_value:
                    context.progress.current_module = next_module
                    break

            await self.save_user_context(context)
            logger.info(f"Пользователь {user_id} завершил модуль {module.name}")
            return True

        return False

    async def learn_chord(self, user_id: int, chord: str) -> bool:
        """Изучить новый аккорд"""
        context = await self.get_user_context(user_id, 0)

        if context.progress.learn_chord(chord):
            # Проверяем достижения за аккорды
            chord_upper = chord.upper()
            if chord_upper == "AM":
                await self.add_achievement(user_id, Achievement.AM_CHORD_MASTERED)
            elif chord_upper == "E":
                await self.add_achievement(user_id, Achievement.E_CHORD_MASTERED)

            await self.save_user_context(context)
            logger.info(f"Пользователь {user_id} изучил аккорд {chord}")
            return True

        return False

    async def set_user_name(self, user_id: int, name: str):
        """Установить имя пользователя"""
        context = await self.get_user_context(user_id, 0)
        context.progress.user_name = name.strip()
        await self.save_user_context(context)
        logger.info(f"Установлено имя пользователя {user_id}: {name}")

    async def get_user_stats(self, user_id: int) -> Dict:
        """Получить статистику пользователя"""
        context = await self.get_user_context(user_id, 0)

        return {
            "user_name": context.progress.user_name,
            "current_module": context.progress.current_module.name,
            "completed_modules": len(context.progress.completed_modules),
            "achievements": len(context.progress.achievements),
            "learned_chords": len(context.progress.learned_chords),
            "session_count": context.progress.session_count,
            "last_session": context.progress.last_session_date.isoformat() if context.progress.last_session_date else None
        }

    async def cleanup_old_users(self, days: int = 30) -> int:
        """Очистить данные неактивных пользователей"""
        cutoff_date = datetime.now() - timedelta(days=days)
        removed_count = 0

        try:
            for user_file in self.storage_path.glob("user_*.pkl"):
                if user_file.stat().st_mtime < cutoff_date.timestamp():
                    user_file.unlink()
                    removed_count += 1
        except Exception as e:
            logger.error(f"Ошибка при очистке файлов: {e}")

        logger.info(f"Удалено {removed_count} неактивных пользователей")
        return removed_count
