"""
Конфигурационный модуль для загрузки переменных окружения
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()


class Config:
    """Класс конфигурации приложения"""
    
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # OpenRouter API
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")
    
    # RAWG API
    RAWG_API_KEY: str = os.getenv("RAWG_API_KEY", "")
    RAWG_API_URL: str = "https://api.rawg.io/api"
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "bot_database.db")
    
    @classmethod
    def validate(cls) -> None:
        """Валидация обязательных переменных окружения"""
        required_vars = {
            "BOT_TOKEN": cls.BOT_TOKEN,
            "OPENROUTER_API_KEY": cls.OPENROUTER_API_KEY,
            "RAWG_API_KEY": cls.RAWG_API_KEY,
        }
        
        missing = [name for name, value in required_vars.items() if not value]
        if missing:
            raise ValueError(
                f"Отсутствуют обязательные переменные окружения: {', '.join(missing)}\n"
                f"Проверьте файл .env"
            )


# Валидация конфигурации при импорте
Config.validate()

# Для обратной совместимости
BOT_TOKEN = Config.BOT_TOKEN
OPENROUTER_API_KEY = Config.OPENROUTER_API_KEY
OPENROUTER_API_URL = Config.OPENROUTER_API_URL
OPENROUTER_MODEL = Config.OPENROUTER_MODEL
RAWG_API_KEY = Config.RAWG_API_KEY
RAWG_API_URL = Config.RAWG_API_URL
DATABASE_PATH = Config.DATABASE_PATH
