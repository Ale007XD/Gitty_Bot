"""
Сервис для работы с Google Gemini AI
Исправленная версия для Telegram-бота Гитти
"""
import asyncio
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from loguru import logger


class GeminiService:
    """Сервис для работы с Google Gemini AI для обучения игре на гитаре"""
    
    def __init__(self, api_key: str):
        """
        Инициализация сервиса Gemini
        
        Args:
            api_key: API ключ для Google Gemini
        """
        self.api_key = api_key
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Инициализация клиента Gemini"""
        try:
            # Настройка API ключа
            genai.configure(api_key=self.api_key)
            
            # Создание модели
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Настройки генерации
            self.generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                top_k=40,
                top_p=0.95,
                max_output_tokens=1000,
            )
            
            # Настройки безопасности для детского контента
            self.safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_LOW_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
            
            logger.info("🤖 Google Gemini успешно инициализирован")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Gemini: {e}")
            raise
    
    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Генерация ответа с помощью Gemini
        
        Args:
            prompt: Текст запроса от пользователя
            context: Дополнительный контекст (уровень, прогресс)
            
        Returns:
            Сгенерированный ответ от AI-наставника
        """
        try:
            # Формируем полный промпт с контекстом
            full_prompt = self._build_guitar_prompt(prompt, context)
            
            logger.info(f"🎸 Генерация ответа Gemini для: {prompt[:50]}...")
            
            # Генерируем ответ асинхронно
            response = await asyncio.to_thread(
                self._generate_content_sync,
                full_prompt
            )
            
            if response and response.text:
                answer = response.text.strip()
                logger.info(f"✅ Ответ Gemini сгенерирован: {len(answer)} символов")
                return answer
            else:
                logger.warning("⚠️ Gemini вернул пустой ответ")
                return self._get_fallback_response(prompt)
                
        except Exception as e:
            logger.error(f"❌ Ошибка генерации ответа Gemini: {e}")
            return self._get_error_response()
    
    def _generate_content_sync(self, prompt: str):
        """Синхронная генерация контента"""
        return self.model.generate_content(
            prompt,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
    
    def _build_guitar_prompt(self, user_prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Построение специализированного промпта для гитарного обучения
        
        Args:
            user_prompt: Запрос пользователя
            context: Контекст пользователя (уровень, прогресс)
            
        Returns:
            Полный промпт для модели
        """
        # Базовый системный промпт
        system_prompt = """🎸 Ты - Гитти, дружелюбный AI-наставник по игре на гитаре для детей 7-12 лет.

ТВОЯ РОЛЬ:
- Обучать основам игры на гитаре понятно и интересно
- Мотивировать и поддерживать юных музыкантов
- Использовать простой, детский язык
- Быть терпеливым и ободряющим
- Делать обучение похожим на игру

СТИЛЬ ОБЩЕНИЯ:
- Дружелюбный и позитивный тон
- Используй эмодзи: 🎸🎵🎶🌟✨🎯
- Короткие предложения (1-2 строки)
- Игровые аналогии и примеры
- Подходящий для детского возраста контент

СТРУКТУРА ОТВЕТА:
1. Дружелюбное приветствие
2. Основная информация простым языком
3. Практический совет или упражнение
4. Мотивация и поддержка

БЕЗОПАСНОСТЬ:
- Только музыкальный контент
- Безопасные для детей советы
- Позитивная атмосфера обучения"""

        # Добавляем контекст пользователя
        if context:
            user_level = context.get('level', 'новичок')
            user_age = context.get('age', '8')
            progress = context.get('progress', {})
            
            context_info = f"""

ИНФОРМАЦИЯ ОБ УЧЕНИКЕ:
- Возраст: {user_age} лет
- Уровень: {user_level}
- Прогресс: {progress}
- Адаптируй сложность под этот уровень!"""
            
            system_prompt += context_info
        
        # Собираем финальный промпт
        full_prompt = f"""{system_prompt}

ЗАПРОС УЧЕНИКА: {user_prompt}

ТВОЙ ОТВЕТ (на русском, для ребенка, с эмодзи):"""
        
        return full_prompt
    
    def _get_fallback_response(self, original_prompt: str) -> str:
        """Запасной ответ если AI не отвечает"""
        return """🎸 Привет! Я временно не могу ответить на этот вопрос, но давай попробуем что-то другое!

Можешь спросить меня:
🎵 Как настроить гитару?
🎶 Какой аккорд изучить первым?
🌟 Как правильно держать гитару?

Я всегда готов помочь тебе в обучении! ✨"""
    
    def _get_error_response(self) -> str:
        """Ответ при ошибке"""
        return """🎸 Ой! У меня маленькая техническая проблема, но я скоро исправлю её!

А пока можешь:
🎵 Потренироваться держать гитару правильно
🎶 Послушать любимую песню
🌟 Подготовить вопросы для меня

Скоро я снова буду готов помочь! ✨"""
    
    async def generate_lesson_content(self, lesson_type: str, user_level: str = "начинающий") -> Dict[str, Any]:
        """
        Генерация контента урока
        
        Args:
            lesson_type: Тип урока (аккорды, бой, песня и т.д.)
            user_level: Уровень пользователя
            
        Returns:
            Структурированный контент урока
        """
        try:
            prompt = f"""Создай урок по теме '{lesson_type}' для {user_level}го уровня.
            
Структура:
1. Название урока
2. Цель урока
3. Пошаговые инструкции (3-5 шагов)
4. Практическое упражнение
5. Мотивационное сообщение

Для детей 7-12 лет, простой язык, с эмодзи."""
            
            response_text = await self.generate_response(prompt)
            
            return {
                "type": lesson_type,
                "level": user_level,
                "content": response_text,
                "created_at": "now"
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации урока: {e}")
            return {
                "type": lesson_type,
                "level": user_level,
                "content": "Урок временно недоступен",
                "created_at": "now"
            }
    
    async def get_practice_feedback(self, user_input: str, exercise_type: str) -> str:
        """
        Получение обратной связи по практическому упражнению
        
        Args:
            user_input: Описание выполнения упражнения пользователем
            exercise_type: Тип упражнения
            
        Returns:
            Обратная связь от AI-наставника
        """
        prompt = f"""Пользователь выполняет упражнение '{exercise_type}' и говорит: "{user_input}"

Дай обратную связь:
1. Похвала за усилия
2. Конкретный совет по улучшению
3. Мотивация продолжать

Для ребенка, позитивно, с эмодзи."""
        
        return await self.generate_response(prompt)
    
    def health_check(self) -> bool:
        """
        Проверка работоспособности сервиса
        
        Returns:
            True если сервис работает
        """
        try:
            return self.model is not None and self.api_key is not None
        except Exception as e:
            logger.error(f"❌ Ошибка health check Gemini: {e}")
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """Информация о сервисе"""
        return {
            "service": "Google Gemini AI",
            "model": "gemini-1.5-flash",
            "status": "active" if self.health_check() else "error",
            "features": [
                "Генерация ответов",
                "Создание уроков",
                "Обратная связь",
                "Детская безопасность"
            ]
        }


# Функция-фабрика для создания сервиса
def create_gemini_service(api_key: str) -> GeminiService:
    """
    Создание экземпляра GeminiService
    
    Args:
        api_key: API ключ Google Gemini
        
    Returns:
        Настроенный экземпляр GeminiService
    """
    if not api_key:
        raise ValueError("API ключ Google Gemini не может быть пустым")
    
    return GeminiService(api_key)
