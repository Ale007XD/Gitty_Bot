"""
Главный файл Telegram-бота "Гитти" - гитарного наставника для детей
"""
import asyncio
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

# Загружаем переменные окружения
load_dotenv()

# Добавляем путь к модулям проекта
sys.path.append(str(Path(__file__).parent))

from utils.config import BotConfig
from services.user_service import UserService
from services.gemini_service import GeminiService
from services.guitar_service import GuitarService
from handlers import start, learning

class GittiBotApp:
    """Главный класс приложения бота Гитти"""

    def __init__(self):
        self.config = None
        self.bot = None
        self.dp = None
        self.user_service = None
        self.gemini_service = None
        self.guitar_service = None

        # Инициализация
        self._load_config()
        self._setup_logging()

    def _load_config(self):
        """Загрузка конфигурации"""
        try:
            self.config = BotConfig.from_env()
            logger.info("Конфигурация загружена успешно")
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            raise

    def _setup_logging(self):
        """Настройка системы логирования"""
        # Отключаем стандартное логирование aiogram
        logging.getLogger("aiogram").setLevel(logging.WARNING)
        logging.getLogger("aiogram.event").setLevel(logging.WARNING)

        # Удаляем стандартный обработчик loguru
        logger.remove()

        log_level = getattr(self.config, 'log_level', 'INFO')

        # Консольный вывод
        logger.add(
            sys.stdout,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
            colorize=True
        )

        # Создаем директорию для логов
        Path("logs").mkdir(exist_ok=True)

        # Файловое логирование
        logger.add(
            "logs/gitti_bot.log",
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} - {message}",
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            encoding="utf-8"
        )

        logger.info("Система логирования настроена")

    async def _setup_services(self):
        """Настройка сервисов"""
        logger.info("Инициализация сервисов...")

        # Создаем необходимые директории
        Path("logs").mkdir(exist_ok=True)
        Path("user_data").mkdir(exist_ok=True)

        try:
            # Инициализация сервисов
            self.user_service = UserService("user_data")
            self.gemini_service = GeminiService(self.config.gemini_api_key, self.config.gemini_region)
            self.guitar_service = GuitarService()

            logger.info("Все сервисы инициализированы успешно")

        except Exception as e:
            logger.error(f"Ошибка инициализации сервисов: {e}")
            raise

    async def _setup_bot(self):
        """Настройка бота и диспетчера"""
        logger.info("Настройка бота...")

        try:
            # Создаем бота
            self.bot = Bot(
                token=self.config.telegram_token,
                default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
            )

            # Создаем диспетчер
            self.dp = Dispatcher()

            # Регистрируем middleware для передачи сервисов
            @self.dp.message.middleware()
            async def services_middleware(handler, event, data):
                data['user_service'] = self.user_service
                data['gemini_service'] = self.gemini_service
                data['guitar_service'] = self.guitar_service
                return await handler(event, data)

            # Подключаем роутеры
            self.dp.include_router(start.router)
            self.dp.include_router(learning.router)

            logger.info("Бот настроен успешно")

        except Exception as e:
            logger.error(f"Ошибка настройки бота: {e}")
            raise

    async def start_polling(self):
        """Запуск бота в режиме polling"""
        logger.info("Запуск бота Гитти...")

        try:
            await self._setup_services()
            await self._setup_bot()

            # Получаем информацию о боте
            bot_info = await self.bot.get_me()
            logger.success(f"🎸 Бот @{bot_info.username} успешно запущен!")
            logger.info(f"Bot ID: {bot_info.id}")
            logger.info(f"Bot Name: {bot_info.first_name}")

            # Запускаем polling
            await self.dp.start_polling(self.bot, skip_updates=True)

        except Exception as e:
            logger.error(f"Критическая ошибка при запуске бота: {e}")
            raise
        finally:
            await self.stop()

    async def stop(self):
        """Остановка бота"""
        logger.info("Остановка бота...")

        try:
            if self.dp:
                await self.dp.stop_polling()

            if self.bot:
                session = getattr(self.bot, 'session', None)
                if session:
                    await session.close()

            logger.info("Бот остановлен корректно")

        except Exception as e:
            logger.error(f"Ошибка при остановке бота: {e}")

async def main():
    """Главная функция запуска"""
    logger.info("🎸 Запуск Telegram-бота Гитти...")

    app = GittiBotApp()

    try:
        await app.start_polling()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки (Ctrl+C)")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        return 1

    return 0

if __name__ == "__main__":
    # Настройка asyncio для Windows
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # Запуск приложения
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Программа прервана пользователем")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        sys.exit(1)
