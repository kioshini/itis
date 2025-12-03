"""
Утилиты для форматирования вывода информации
"""
from database.models import GameInfo
from typing import List
from datetime import datetime, timezone, timedelta
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore
import config


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
        # Форматирование даты с переводом в UTC+offset (по умолчанию +5)
        date_str = to_local_time_str(timestamp)
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


def to_local_time_str(ts: str) -> str:
    """
    Конвертирует строковый timestamp из БД (UTC) в локальное время по смещению.
    Ожидает форматы вида 'YYYY-MM-DD HH:MM:SS' или ISO 'YYYY-MM-DDTHH:MM:SS'.
    Возвращает строку 'YYYY-MM-DD HH:MM'.
    """
    if not ts:
        return ""
    try:
        clean = ts.strip().replace("Z", "")
        # fromisoformat поддерживает как ' ' так и 'T' между датой и временем
        dt = datetime.fromisoformat(clean)
    except Exception:
        # fallback для явного формата SQLite
        try:
            dt = datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            return ts[:16].replace('T', ' ')

    # Считаем, что исходное время в БД — UTC без таймзоны
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    # Пытаемся применить именованную таймзону, если доступна
    tz_name = getattr(config, "TIMEZONE_NAME", None)
    if tz_name and ZoneInfo is not None:
        try:
            local_dt = dt.astimezone(ZoneInfo(tz_name))
            return local_dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass

    # Фоллбек: используем сдвиг в часах
    offset_hours = getattr(config, "TIMEZONE_OFFSET_HOURS", 5)
    local_dt = dt + timedelta(hours=offset_hours)
    return local_dt.strftime("%Y-%m-%d %H:%M")
