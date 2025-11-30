"""
Утилиты для форматирования вывода информации
"""
from database.models import GameInfo
from typing import List


def format_game_info(game: GameInfo, index: int) -> str:
    """
    Форматирование информации об одной игре
    
    Args:
        game: Объект с информацией об игре
        index: Номер игры в списке
        
    Returns:
        Отформатированная строка с информацией
    """
    result = f"<b>{index}. {game.name}</b>\n"
    
    if game.rating:
        # Эмодзи для рейтинга
        stars = "⭐" * int(game.rating)
        result += f"🎮 Рейтинг: {game.rating}/5 {stars}\n"
    
    if game.released:
        result += f"📅 Дата выхода: {game.released}\n"
    
    if game.genres:
        result += f"🎯 Жанры: {game.genres}\n"
    
    if game.platforms:
        result += f"💻 Платформы: {game.platforms}\n"
    
    if game.description:
        result += f"\n📝 <i>{game.description}</i>\n"
    
    return result


def format_games_list(games: List[GameInfo]) -> str:
    """
    Форматирование списка игр
    
    Args:
        games: Список игр
        
    Returns:
        Отформатированная строка со всеми играми
    """
    if not games:
        return "К сожалению, игры не найдены. 😔"
    
    result = "🎮 <b>Найденные игры:</b>\n\n"
    
    for i, game in enumerate(games, 1):
        result += format_game_info(game, i)
        result += "\n" + "─" * 30 + "\n\n"
    
    return result


def format_history(history_items: List[tuple]) -> str:
    """
    Форматирование истории запросов
    
    Args:
        history_items: Список кортежей (query_text, timestamp)
        
    Returns:
        Отформатированная строка с историей
    """
    if not history_items:
        return "📭 История запросов пуста."
    
    result = "📚 <b>Ваша история запросов:</b>\n\n"
    
    for i, (query, timestamp) in enumerate(history_items, 1):
        # Форматирование даты
        date_str = timestamp[:16].replace('T', ' ')  # Убираем секунды
        result += f"{i}. <i>{query}</i>\n   🕐 {date_str}\n\n"
    
    return result


def escape_html(text: str) -> str:
    """
    Экранирование HTML символов
    
    Args:
        text: Исходный текст
        
    Returns:
        Текст с экранированными HTML символами
    """
    if not text:
        return ""
    
    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;"
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text
