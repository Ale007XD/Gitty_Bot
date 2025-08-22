"""
Сервис для работы с Google Gemini API
"""
import asyncio
from typing import List, Dict, Optional
import google.genai as genai
from loguru import logger

# Исправляем импорты моделей
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user_context import UserContext
from utils.config import GITTI_SYSTEM_PROMPT

class GeminiService:
    """Сервис для работы с Gemini API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self.model_name = "gemini-2.0-flash-exp"
        self._initialize_client()

    def _initialize_client(self):
        """Инициализация клиента Gemini"""
        try:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
            logger.info("Gemini client инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации Gemini: {e}")
            raise

    async def get_response(self, user_context: UserContext, user_message: str) -> str:
        """
        Получить ответ от Gemini с учетом контекста пользователя
        """
        try:
            # Формируем системный промпт с учетом прогресса
            system_prompt = self._build_system_prompt(user_context)

            # Получаем историю разговора
            history = user_context.get_gemini_history()

            # Формируем полный промпт
            full_prompt = f"{system_prompt}\n\nПользователь: {user_message}"

            # Отправляем запрос к Gemini
            response = await self._make_gemini_request(full_prompt)

            # Сохраняем сообщения в контекст
            user_context.add_message("user", user_message)
            user_context.add_message("model", response)

            return response

        except Exception as e:
            logger.error(f"Ошибка при работе с Gemini API: {e}")
            return "Прости, у меня временные технические проблемы 🤖 Попробуй еще раз через минутку!"

    def _build_system_prompt(self, user_context: UserContext) -> str:
        """Построить системный промпт с учетом прогресса пользователя"""
        progress_info = f"""

# ТЕКУЩИЙ ПРОГРЕСС УЧЕНИКА:
- Имя: {user_context.progress.user_name or "не указано"}
- Текущий модуль: {user_context.progress.current_module.name}
- Завершенные модули: {[m.name for m in user_context.progress.completed_modules]}
- Изученные аккорды: {user_context.progress.learned_chords}
- Достижения: {[a.value for a in user_context.progress.achievements]}
- Количество занятий: {user_context.progress.session_count}
        """

        return GITTI_SYSTEM_PROMPT + progress_info

    async def _make_gemini_request(self, prompt: str) -> str:
        """Сделать запрос к Gemini API"""
        try:
            # Используем asyncio.to_thread для синхронного API
            def sync_generate():
                response = self.client.generate_content(prompt)
                return response.text if response.text else ""

            response_text = await asyncio.to_thread(sync_generate)

            if not response_text:
                return "Извини, я не смог сформулировать ответ. Попробуй переформулировать вопрос 🤖"

            return response_text

        except Exception as e:
            logger.error(f"Ошибка запроса к Gemini: {e}")
            raise

    def get_achievement_message(self, achievement_name: str) -> str:
        """Получить сообщение о достижении"""
        achievement_messages = {
            "first_meeting": "🎉 Добро пожаловать в мир гитары! Ты получил достижение 'Первое знакомство'!",
            "guitar_parts": "✨ Отлично! Ты изучил части гитары! Получено достижение 'Знаток инструмента'!",
            "strings_memorized": "🎸 Превосходно! Ты запомнил названия струн! Достижение 'Мастер струн' твое!",
            "am_chord": "🏆 Поздравляю! Ты освоил аккорд Am! Получено достижение 'Повелитель аккорда Am'!",
            "e_chord": "🌟 Браво! Аккорд E теперь тебе подвластен! Достижение 'Мастер аккорда E'!",
            "first_song": "🎵 Невероятно! Ты сыграл свою первую песню! Достижение 'Первая мелодия'!",
            "week_streak": "🔥 Фантастика! Неделя занятий без пропусков! Достижение 'Стальная дисциплина'!"
        }

        return achievement_messages.get(achievement_name, f"🎉 Поздравляю с новым достижением: {achievement_name}!")
