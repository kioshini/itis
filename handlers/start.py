"""
Обработчик команды /start
"""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from keyboards.inline import get_main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработка команды /start"""
    welcome_text = """
👋 <b>Добро пожаловать в бота для поиска игр!</b>

Я помогу вам найти идеальную игру по вашему описанию! 
Просто опишите, что вы хотите, и я подберу 3-5 подходящих игр.

<b>Доступные команды:</b>
🔍 /search - поиск игр по описанию
📚 /history - история ваших запросов
❓ /help - подробная справка
ℹ️ /info - информация о проекте

Используйте кнопки ниже для быстрого доступа:
"""
    
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Возврат в главное меню"""
    welcome_text = """
👋 <b>Главное меню</b>

Выберите действие из списка ниже:
"""
    
    await callback.message.edit_text(
        text=welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
