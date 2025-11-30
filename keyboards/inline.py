"""
Inline клавиатуры для бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню с основными командами"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Поиск игр", callback_data="search")],
        [InlineKeyboardButton(text="📚 История запросов", callback_data="history")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
        [InlineKeyboardButton(text="ℹ️ О проекте", callback_data="info")]
    ])
    return keyboard


def get_history_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для управления историей"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑️ Очистить историю", callback_data="clear_history")],
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")]
    ])
    return keyboard


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")]
    ])
    return keyboard


def get_confirm_clear_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения очистки истории"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, очистить", callback_data="confirm_clear"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="history")
        ]
    ])
    return keyboard
