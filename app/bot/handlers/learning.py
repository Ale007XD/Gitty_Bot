"""
Обработчики обучающего процесса
"""
import re
from aiogram import types, Router
from loguru import logger

# Исправляем импорты
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_service import UserService
from services.gemini_service import GeminiService
from services.guitar_service import GuitarService
from models.user_context import Achievement, LearningModule

router = Router()

@router.message()
async def handle_text_message(message: types.Message, user_service: UserService,
                             gemini_service: GeminiService, guitar_service: GuitarService):
    """Обработчик текстовых сообщений"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_message = message.text

    try:
        # Получаем контекст пользователя
        user_context = await user_service.get_user_context(user_id, chat_id)

        # Обработка специальных команд
        special_response = await _handle_special_commands(
            message, user_context, user_service, guitar_service
        )
        if special_response:
            return

        # Обработка запросов аккордов
        chord_response = await _handle_chord_request(
            message, user_context, user_service, guitar_service
        )
        if chord_response:
            return

        # Обработка имени пользователя
        name_response = await _handle_name_input(
            message, user_context, user_service
        )
        if name_response:
            return

        # Получаем ответ от Gemini
        response = await gemini_service.generate_response(user_message, user_context.__dict__)

        # Проверяем на новые достижения после ответа Gemini
        await _check_achievements(user_context, user_service, user_message, response)

        # Отправляем ответ
        await message.answer(response)

        # Сохраняем обновленный контекст
        await user_service.save_user_context(user_context)

    except Exception as e:
        logger.error(f"Ошибка обработки сообщения от пользователя {user_id}: {e}")
        await message.answer("Упс! У меня произошла техническая проблема 🤖 Попробуй еще раз!")

async def _handle_special_commands(message: types.Message, user_context, 
                                 user_service: UserService, guitar_service: GuitarService) -> bool:
    """Обработка специальных команд в тексте"""
    text = message.text.lower()

    # Команда показать струны
    if "струн" in text and any(word in text for word in ["покажи", "расскажи", "объясни", "схема"]):
        try:
            strings_info = guitar_service.get_strings_info()
            await message.answer(strings_info, parse_mode="Markdown")
            await user_service.add_achievement(message.from_user.id, Achievement.STRINGS_MEMORIZED)
            return True
        except Exception as e:
            logger.error(f"Ошибка получения информации о струнах: {e}")

    # Команда показать части гитары
    if "части" in text and "гитар" in text:
        try:
            parts_info = guitar_service.get_guitar_parts_info()
            await message.answer(parts_info, parse_mode="Markdown")
            await user_service.add_achievement(message.from_user.id, Achievement.GUITAR_PARTS_LEARNED)
            return True
        except Exception as e:
            logger.error(f"Ошибка получения информации о частях гитары: {e}")

    # Команда показать правильную посадку
    if any(word in text for word in ["посадка", "сидеть", "держать гитару"]):
        try:
            posture_tips = guitar_service.get_posture_tips()
            await message.answer(posture_tips, parse_mode="Markdown")
            return True
        except Exception as e:
            logger.error(f"Ошибка получения советов по посадке: {e}")

    return False

async def _handle_chord_request(message: types.Message, user_context, 
                              user_service: UserService, guitar_service: GuitarService) -> bool:
    """Обработка запросов аккордов"""
    text = message.text.upper()

    # Проверяем, является ли сообщение запросом аккорда
    available_chords = guitar_service.get_available_chords()

    for chord in available_chords:
        if chord.upper() in text or chord.lower() in message.text.lower():
            try:
                # Получаем информацию об аккорде
                chord_info = guitar_service.get_chord_info(chord)
                if chord_info:
                    # Получаем диаграмму
                    diagram = guitar_service.get_chord_diagram(chord)

                    response = f"""🎸 **{chord_info['name']}**

📊 **Сложность:** {chord_info['difficulty']}
💡 **Описание:** {chord_info['description']}

**Диаграмма:**
```
{diagram}
```

Попробуй поставить этот аккорд и расскажи, как получается! 🎵"""

                    await message.answer(response, parse_mode="Markdown")

                    # Отмечаем изучение аккорда
                    await user_service.learn_chord(message.from_user.id, chord)

                    return True

            except Exception as e:
                logger.error(f"Ошибка обработки аккорда {chord}: {e}")
                await message.answer(f"Извини, не смог показать аккорд {chord} 😔")
                return True

    return False

async def _handle_name_input(message: types.Message, user_context, user_service: UserService) -> bool:
    """Обработка ввода имени пользователя"""
    text = message.text.strip()

    # Если у пользователя еще нет имени и это похоже на ввод имени
    if (not user_context.progress.user_name and 
        user_context.progress.current_module == LearningModule.INTRODUCTION and
        len(text.split()) <= 3 and  # Имя обычно не больше 3 слов
        not any(word in text.lower() for word in ["привет", "здравствуй", "как дела", "что", "где", "когда", "почему"])):

        # Простая проверка на то, что это может быть имя
        if re.match(r'^[а-яёА-ЯЁa-zA-Z\s-]+$', text) and len(text) > 1:
            name = text.title()  # Делаем первую букву заглавной
            await user_service.set_user_name(message.from_user.id, name)

            response = f"""Очень приятно познакомиться, {name}! 🎸✨

Теперь давай изучим основы гитары! Сначала важно понять, из каких частей состоит наш инструмент.

Напиши '/parts' или 'покажи части гитары' и я покажу тебе схему! 📚"""

            await message.answer(response)
            return True

    return False

async def _check_achievements(user_context, user_service: UserService, user_message: str, bot_response: str):
    """Проверка и добавление достижений"""
    user_id = user_context.user_id
    text_lower = (user_message + " " + bot_response).lower()

    # Достижение за изучение частей гитары
    if any(word in text_lower for word in ["дека", "гриф", "струн", "головка"]):
        await user_service.add_achievement(user_id, Achievement.GUITAR_PARTS_LEARNED)

    # Достижение за первую песню
    if "кузнечик" in text_lower or ("песн" in text_lower and "трав" in text_lower):
        await user_service.add_achievement(user_id, Achievement.FIRST_SONG_PLAYED)

    # Проверка на освоение аккордов
    if "am" in text_lower and any(word in text_lower for word in ["получается", "освоил", "выучил", "умею"]):
        await user_service.add_achievement(user_id, Achievement.AM_CHORD_MASTERED)

    if (" e " in text_lower or "ми мажор" in text_lower) and any(word in text_lower for word in ["получается", "освоил", "выучил", "умею"]):
        await user_service.add_achievement(user_id, Achievement.E_CHORD_MASTERED)

def _get_achievement_message(achievement: Achievement) -> str:
    """Получить сообщение о достижении"""
    messages = {
        Achievement.FIRST_MEETING: "🎉 Добро пожаловать в мир гитары!",
        Achievement.GUITAR_PARTS_LEARNED: "✨ Отлично! Ты изучил части гитары!",
        Achievement.STRINGS_MEMORIZED: "🎸 Превосходно! Ты запомнил струны!",
        Achievement.AM_CHORD_MASTERED: "🏆 Поздравляю! Аккорд Am освоен!",
        Achievement.E_CHORD_MASTERED: "🌟 Браво! Аккорд E покорен!",
        Achievement.FIRST_SONG_PLAYED: "🎵 Невероятно! Первая песня сыграна!",
        Achievement.WEEK_STREAK: "🔥 Неделя занятий - это успех!"
    }
    return messages.get(achievement, f"🎉 Новое достижение: {achievement.value}!")
