"""
Обработчик команды /search - основная функциональность бота
"""
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from keyboards.inline import get_back_keyboard
from database.db import db
from services.ai_service import ai_service

router = Router()


class SearchStates(StatesGroup):
    """Состояния для процесса поиска"""
    waiting_for_query = State()


@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    """Обработка команды /search"""
    search_prompt = """
🔍 <b>Поиск игр по описанию</b>

Опишите игру, которую вы ищете. Будьте максимально конкретны!

<b>Примеры хороших запросов:</b>
• "Ищу RPG с открытым миром, драконами и магией"
• "Хочу шутер от первого лица про вторую мировую войну"
• "Нужна стратегия про космос с элементами строительства базы"
• "Игра как The Witcher, но про самураев в Японии"

Просто отправьте сообщение с вашим описанием!
Для отмены введите /cancel
"""
    
    await message.answer(
        text=search_prompt,
        parse_mode="HTML"
    )
    
    await state.set_state(SearchStates.waiting_for_query)


@router.callback_query(F.data == "search")
async def callback_search(callback: CallbackQuery, state: FSMContext):
    """Обработка callback для поиска"""
    search_prompt = """
🔍 <b>Поиск игр по описанию</b>

Опишите игру, которую вы ищете. Будьте максимально конкретны!

<b>Примеры хороших запросов:</b>
• "Ищу RPG с открытым миром, драконами и магией"
• "Хочу шутер от первого лица про вторую мировую войну"
• "Нужна стратегия про космос с элементами строительства базы"
• "Игра как The Witcher, но про самураев в Японии"

Просто отправьте сообщение с вашим описанием!
Для отмены введите /cancel
"""
    
    await callback.message.edit_text(
        text=search_prompt,
        parse_mode="HTML"
    )
    
    await state.set_state(SearchStates.waiting_for_query)
    await callback.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Отмена текущего действия"""
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer("Нечего отменять.")
        return
    
    await state.clear()
    await message.answer(
        "❌ Действие отменено.",
        reply_markup=get_back_keyboard()
    )


@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext):
    """Обработка запроса пользователя"""
    user_query = message.text.strip()
    user_id = message.from_user.id
    
    # Проверка длины запроса
    if len(user_query) < 10:
        await message.answer(
            "⚠️ Запрос слишком короткий. Пожалуйста, опишите игру подробнее (минимум 10 символов)."
        )
        return
    
    if len(user_query) > 500:
        await message.answer(
            "⚠️ Запрос слишком длинный. Пожалуйста, сократите описание (максимум 500 символов)."
        )
        return
    
    # Отправка сообщения о начале обработки
    processing_msg = await message.answer("⏳ Анализирую ваш запрос и ищу подходящие игры... Подождите немного.")
    
    try:
        # Получение детальных рекомендаций от AI
        games_info = await ai_service.get_game_recommendations_with_details(user_query)
        
        if not games_info:
            await processing_msg.edit_text(
                "😔 Не удалось получить рекомендации.\n\n"
                "Возможные причины:\n"
                "• Неправильный API ключ OpenRouter\n"
                "• Недостаточно кредитов на балансе\n"
                "• Проблемы с подключением\n\n"
                "Проверьте настройки и попробуйте позже.",
                reply_markup=get_back_keyboard()
            )
            await state.clear()
            return
        
        # Форматирование результатов
        result_text = "🎮 <b>Рекомендации для вас:</b>\n\n"
        
        for i, game in enumerate(games_info, 1):
            result_text += f"<b>{i}. {game.get('name', 'Неизвестно')}</b>\n"
            
            if game.get('rating'):
                stars = "⭐" * int(float(game['rating']))
                result_text += f"🎮 Рейтинг: {game['rating']}/5 {stars}\n"
            
            if game.get('released'):
                result_text += f"📅 Год выпуска: {game['released']}\n"
            
            if game.get('genres'):
                result_text += f"🎯 Жанры: {game['genres']}\n"
            
            if game.get('platforms'):
                result_text += f"💻 Платформы: {game['platforms']}\n"
            
            if game.get('description'):
                result_text += f"\n📝 <i>{game['description']}</i>\n"
            
            result_text += "\n" + "─" * 30 + "\n\n"
        
        # Отправка результатов
        await processing_msg.edit_text(
            text=result_text,
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        
        # Сохранение в историю
        await db.add_search_query(user_id, user_query)
        
    except Exception as e:
        print(f"❌ Ошибка при обработке запроса: {e}")
        await processing_msg.edit_text(
            "😔 Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже.",
            reply_markup=get_back_keyboard()
        )
    finally:
        await state.clear()
