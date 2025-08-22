"""
Конфигурация бота Гитти
Обновленная версия с проверкой API ключей
"""
import os
from typing import Optional
from pydantic import BaseModel, Field, validator
from loguru import logger


class BotConfig(BaseModel):
    """Конфигурация Telegram-бота"""
    
    # Telegram Bot
    telegram_token: str = Field(..., min_length=10, description="Токен Telegram бота")
    
    # Google Gemini AI
    gemini_api_key: str = Field(..., min_length=10, description="API ключ Google Gemini")
    
    # Логирование
    log_level: str = Field(default="INFO", description="Уровень логирования")
    debug: bool = Field(default=False, description="Режим отладки")
    
    # Пути к файлам
    user_data_path: str = Field(default="/app/user_data", description="Путь к данным пользователей")
    logs_path: str = Field(default="/app/logs", description="Путь к логам")
    
    # Настройки бота
    max_message_length: int = Field(default=4000, description="Максимальная длина сообщения")
    rate_limit_per_minute: int = Field(default=30, description="Лимит сообщений в минуту")
    
    @validator('telegram_token')
    def validate_telegram_token(cls, v):
        """Валидация токена Telegram"""
        if not v or len(v) < 40:
            raise ValueError("Некорректный токен Telegram бота")
        if not v.count(':') == 1:
            raise ValueError("Неправильный формат токена Telegram")
        return v
    
    @validator('gemini_api_key')
    def validate_gemini_api_key(cls, v):
        """Валидация API ключа Gemini"""
        if not v or len(v) < 20:
            raise ValueError("Некорректный API ключ Google Gemini")
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Валидация уровня логирования"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Уровень логирования должен быть одним из: {valid_levels}")
        return v.upper()
    
    @classmethod
    def from_env(cls) -> 'BotConfig':
        """
        Создание конфигурации из переменных окружения
        
        Returns:
            Экземпляр BotConfig
        """
        try:
            config = cls(
                telegram_token=os.getenv('TELEGRAM_BOT_TOKEN', ''),
                gemini_api_key=os.getenv('GEMINI_API_KEY', ''),
                log_level=os.getenv('LOG_LEVEL', 'INFO'),
                debug=os.getenv('DEBUG', 'false').lower() == 'true',
                user_data_path=os.getenv('USER_DATA_PATH', '/app/user_data'),
                logs_path=os.getenv('LOGS_PATH', '/app/logs'),
                max_message_length=int(os.getenv('MAX_MESSAGE_LENGTH', '4000')),
                rate_limit_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', '30'))
            )
            
            logger.info("✅ Конфигурация успешно загружена из переменных окружения")
            return config
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфигурации: {e}")
            raise ValueError(f"Не удалось загрузить конфигурацию: {e}")
    
    def validate_config(self) -> bool:
        """
        Проверка корректности конфигурации
        
        Returns:
            True если конфигурация валидна
        """
        try:
            # Проверяем обязательные поля
            if not self.telegram_token:
                logger.error("❌ Отсутствует TELEGRAM_BOT_TOKEN")
                return False
                
            if not self.gemini_api_key:
                logger.error("❌ Отсутствует GEMINI_API_KEY")
                return False
            
            logger.info("✅ Конфигурация прошла валидацию")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка валидации конфигурации: {e}")
            return False
    
    def get_config_info(self) -> dict:
        """Получение информации о конфигурации (без секретных данных)"""
        return {
            "log_level": self.log_level,
            "debug": self.debug,
            "user_data_path": self.user_data_path,
            "logs_path": self.logs_path,
            "max_message_length": self.max_message_length,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "telegram_token": "***скрыто***",
            "gemini_api_key": "***скрыто***"
        }
