"""
Информация о версии Telegram-бота "Гитти"
"""

__version__ = "1.0.0"
__build__ = "20240822"
__author__ = "Gitti Bot Team"
__email__ = "support@gitti-bot.com"
__description__ = "Telegram-бот для обучения детей игре на гитаре"

# История версий
VERSION_HISTORY = {
    "1.0.0": {
        "date": "2024-08-22",
        "changes": [
            "Первый релиз",
            "4 модуля обучения",
            "Система достижений", 
            "Интеграция с Google Gemini",
            "Docker контейнеризация",
            "CI/CD через GitHub Actions"
        ]
    }
}

def get_version_info() -> dict:
    """Получить информацию о версии"""
    return {
        "version": __version__,
        "build": __build__,
        "author": __author__,
        "description": __description__
    }
