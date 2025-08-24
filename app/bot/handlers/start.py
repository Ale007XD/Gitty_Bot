"""
Обработчики команды /start и начального взаимодействия
"""
from aiogram import types, Router
from aiogram.filters import Command
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

@router.message(Command("start"))
async def cmd_start(message: types.Message, user_service: UserService, 
                   gemini_service: GeminiService, guitar_service: GuitarService):
    """Обработчик команды /start"""
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id

        # Получаем контекст пользователя
        user_context = await user_service.get_user_context(user_id, chat_id)

        # Проверяем, новый ли это пользователь
        is_new_user = user_context.progress.session_count == 0

        if is_new_user:
            # Добавляем достижение за первое знакомство
            await user_service.add_achievement(user_id, Achievement.FIRST_MEETING)

            # Приветственное сообщение
            welcome_text = """🎸 Привет! Меня зовут Гитти! 🤖

Я твой персональный робот-наставник по игре на гитаре! ✨

Я помогу тебе:
• 🎯 Изучить части гитары
• 🎵 Выучить первые аккорды  
• 🎶 Сыграть твою первую песню
• 🏆 Получать крутые достижения

А как тебя зовут? 😊"""

            await message.answer(welcome_text)

        else:
            # Приветствие для возвращающегося пользователя
            user_name = user_context.progress.user_name or "друг"
            current_module = user_context.progress.current_module.name

            welcome_back_text = f"""🎸 С возвращением, {user_name}! 

Рад снова тебя видеть! ✨

Твой прогресс:
• 📚 Текущий модуль: {current_module}
• 🎸 Изученных аккордов: {len(user_context.progress.learned_chords)}
• 🏆 Достижений: {len(user_context.progress.achievements)}
• 📊 Занятий проведено: {user_context.progress.session_count}

Готов продолжить изучение гитары? 🎵"""

            await message.answer(welcome_back_text)

        # Обновляем сессию
        await user_service.save_user_context(user_context)

    except Exception as e:
        logger.error(f"Ошибка в cmd_start: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз 🤖")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = """🎸 **Команды Гитти:**

/start - Начать обучение
/progress - Мой прогресс  
/chords - Показать аккорды
/song - Текст первой песни
/exercises - Упражнения для практики
/achievements - Мои достижения
/parts - Части гитары
/strings - Названия струн
/posture - Правильная посадка
/help - Эта справка

💡 Просто пиши мне сообщения, и я буду учить тебя играть на гитаре! 

Помни: изучение гитары - это путешествие, а не гонка! 🎵✨"""

    await message.answer(help_text, parse_mode="Markdown")

@router.message(Command("progress"))
async def cmd_progress(message: types.Message, user_service: UserService):
    """Показать прогресс пользователя"""
    try:
        user_id = message.from_user.id
        stats = await user_service.get_user_stats(user_id)

        progress_text = f"""📊 **Твой прогресс:**

👤 **Имя:** {stats['user_name'] or 'Не указано'}
📚 **Текущий модуль:** {stats['current_module']}
✅ **Завершенных модулей:** {stats['completed_modules']}/4
🎸 **Изученных аккордов:** {stats['learned_chords']}
🏆 **Достижений:** {stats['achievements']}
📈 **Всего занятий:** {stats['session_count']}

{_get_progress_emoji(stats['completed_modules'])} Так держать! 🎵"""

        await message.answer(progress_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка в cmd_progress: {e}")
        await message.answer("Не удалось получить прогресс. Попробуйте еще раз.")

def _get_progress_emoji(completed_modules: int) -> str:
    """Получить эмодзи прогресса"""
    if completed_modules == 0:
        return "🌱"
    elif completed_modules == 1:
        return "🌿"
    elif completed_modules == 2:
        return "🌳"
    elif completed_modules >= 3:
        return "🏆"
    return "🎸"

@router.message(Command("chords"))
async def cmd_chords(message: types.Message, guitar_service: GuitarService):
    """Показать доступные аккорды"""
    try:
        chords = guitar_service.get_available_chords()
        
        if not chords:
            await message.answer("Ошибка при получении списка аккордов.")
            return

        chords_text = "🎸 **Доступные аккорды:**\n\n"
        for chord in chords:
            chord_info = guitar_service.get_chord_info(chord)
            if chord_info:  # Дополнительная проверка
                chords_text += f"• **{chord}** - {chord_info['name']} ({chord_info['difficulty']})\n"

        chords_text += "\n💡 Напиши название аккорда, и я покажу тебе диаграмму!"

        await message.answer(chords_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка в cmd_chords: {e}")
        await message.answer("Ошибка при получении списка аккордов.")

@router.message(Command("song"))
async def cmd_song(message: types.Message, guitar_service: GuitarService):
    """Показать текст первой песни"""
    try:
        song_text = guitar_service.get_learning_song_text()
        await message.answer(song_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка в cmd_song: {e}")
        await message.answer("Ошибка при получении текста песни.")

@router.message(Command("exercises"))
async def cmd_exercises(message: types.Message, guitar_service: GuitarService):
    """Показать упражнения для практики"""
    try:
        exercises = guitar_service.generate_practice_exercises()

        exercises_text = "💪 **Упражнения для практики:**\n\n"
        exercises_text += "\n\n".join(exercises)
        exercises_text += "\n\n🎯 Выбери любое упражнение и начинай практиковаться!"

        await message.answer(exercises_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка в cmd_exercises: {e}")
        await message.answer("Ошибка при получении упражнений.")

@router.message(Command("achievements"))
async def cmd_achievements(message: types.Message, user_service: UserService):
    """Показать достижения пользователя"""
    try:
        user_id = message.from_user.id
        user_context = await user_service.get_user_context(user_id, 0)

        if not user_context.progress.achievements:
            await message.answer("🏆 У тебя пока нет достижений. Продолжай заниматься, и они обязательно появятся! ✨")
            return

        achievements_text = "🏆 **Твои достижения:**\n\n"

        achievement_names = {
            "first_meeting": "🎉 Первое знакомство",
            "guitar_parts": "✨ Знаток инструмента", 
            "strings_memorized": "🎸 Мастер струн",
            "am_chord": "🏆 Повелитель аккорда Am",
            "e_chord": "🌟 Мастер аккорда E",
            "first_song": "🎵 Первая мелодия",
            "week_streak": "🔥 Стальная дисциплина"
        }

        for achievement in user_context.progress.achievements:
            name = achievement_names.get(achievement.value, achievement.value)
            achievements_text += f"• {name}\n"

        achievements_text += f"\n✨ Всего достижений: {len(user_context.progress.achievements)}"

        await message.answer(achievements_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка в cmd_achievements: {e}")
        await message.answer("Ошибка при получении достижений.")

@router.message(Command("parts"))
async def cmd_parts(message: types.Message, guitar_service: GuitarService):
    """Показать части гитары"""
    try:
        parts_info = guitar_service.get_guitar_parts_info()
        await message.answer(parts_info, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка в cmd_parts: {e}")
        await message.answer("Ошибка при получении информации о частях гитары.")

@router.message(Command("strings"))
async def cmd_strings(message: types.Message, guitar_service: GuitarService):
    """Показать информацию о струнах"""
    try:
        strings_info = guitar_service.get_strings_info()
        await message.answer(strings_info, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка в cmd_strings: {e}")
        await message.answer("Ошибка при получении информации о струнах.")

@router.message(Command("posture"))
async def cmd_posture(message: types.Message, guitar_service: GuitarService):
    """Показать советы по правильной посадке"""
    try:
        posture_tips = guitar_service.get_posture_tips()
        await message.answer(posture_tips, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка в cmd_posture: {e}")
        await message.answer("Ошибка при получении советов по посадке.")
