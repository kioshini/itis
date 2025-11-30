"""
Главный файл запуска Telegram-бота для поиска игр
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
from database.db import db
from handlers import start, help, info, history, search


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def on_startup():
    """Действия при запуске бота"""
    logger.info("Инициализация базы данных...")
    await db.init_db()
    logger.info("База данных инициализирована!")
    logger.info("Бот запущен и готов к работе!")


async def on_shutdown():
    """Действия при остановке бота"""
    logger.info("Бот остановлен.")


async def main():
    """Главная функция запуска бота"""
    
    # Создание бота и диспетчера
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация обработчиков
    dp.include_router(start.router)
    dp.include_router(search.router)
    dp.include_router(history.router)
    dp.include_router(help.router)
    dp.include_router(info.router)
    
    # Регистрация функций запуска/остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Удаление вебхука (для работы через polling)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запуск бота
    try:
        logger.info("Запуск бота...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем (Ctrl+C)")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
