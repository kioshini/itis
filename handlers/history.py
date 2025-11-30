"""
Обработчик команды /history
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from keyboards.inline import get_history_keyboard, get_confirm_clear_keyboard, get_back_keyboard
from database.db import db
from utils.formatters import format_history

router = Router()


@router.message(Command("history"))
async def cmd_history(message: Message):
    """Обработка команды /history"""
    user_id = message.from_user.id
    
    # Получение истории из базы данных
    history_items = await db.get_user_history(user_id, limit=15)
    history_text = format_history(history_items)
    
    # Показываем кнопки только если есть история
    if history_items:
        keyboard = get_history_keyboard()
    else:
        keyboard = get_back_keyboard()
    
    await message.answer(
        text=history_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "history")
async def callback_history(callback: CallbackQuery):
    """Обработка callback для истории"""
    user_id = callback.from_user.id
    
    # Получение истории из базы данных
    history_items = await db.get_user_history(user_id, limit=15)
    history_text = format_history(history_items)
    
    # Показываем кнопки только если есть история
    if history_items:
        keyboard = get_history_keyboard()
    else:
        keyboard = get_back_keyboard()
    
    await callback.message.edit_text(
        text=history_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "clear_history")
async def callback_clear_history(callback: CallbackQuery):
    """Запрос подтверждения очистки истории"""
    confirm_text = """
⚠️ <b>Подтверждение действия</b>

Вы уверены, что хотите очистить всю историю запросов?
Это действие нельзя отменить.
"""
    
    await callback.message.edit_text(
        text=confirm_text,
        reply_markup=get_confirm_clear_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_clear")
async def callback_confirm_clear(callback: CallbackQuery):
    """Подтверждение очистки истории"""
    user_id = callback.from_user.id
    
    # Очистка истории
    await db.clear_user_history(user_id)
    
    success_text = """
✅ <b>История успешно очищена!</b>

Ваша история запросов была полностью удалена.
"""
    
    await callback.message.edit_text(
        text=success_text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer("История очищена ✅")
