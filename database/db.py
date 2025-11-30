"""
Инициализация и управление базой данных SQLite
"""
import sqlite3
import aiosqlite
from typing import List, Tuple
from datetime import datetime
import config


class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self, db_path: str = None):
        """Инициализация базы данных"""
        self.db_path = db_path or config.DATABASE_PATH
    
    async def init_db(self):
        """Создание таблиц в базе данных"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    query_text TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id 
                ON search_history(user_id)
            """)
            await db.commit()
    
    async def add_search_query(self, user_id: int, query_text: str):
        """Добавление запроса в историю"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO search_history (user_id, query_text) VALUES (?, ?)",
                (user_id, query_text)
            )
            await db.commit()
    
    async def get_user_history(self, user_id: int, limit: int = 10) -> List[Tuple[str, str]]:
        """Получение истории запросов пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """SELECT query_text, timestamp 
                   FROM search_history 
                   WHERE user_id = ? 
                   ORDER BY timestamp DESC 
                   LIMIT ?""",
                (user_id, limit)
            ) as cursor:
                return await cursor.fetchall()
    
    async def clear_user_history(self, user_id: int):
        """Очистка истории запросов пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM search_history WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()
    
    async def get_history_count(self, user_id: int) -> int:
        """Получение количества запросов в истории"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM search_history WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0


# Глобальный экземпляр базы данных
db = Database()
