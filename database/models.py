"""
Модели данных для работы с базой данных
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SearchQuery:
    """Модель запроса в истории поиска"""
    id: Optional[int] = None
    user_id: int = 0
    query_text: str = ""
    timestamp: Optional[datetime] = None
    
    def __str__(self):
        return f"Query(user={self.user_id}, text='{self.query_text[:30]}...', time={self.timestamp})"


@dataclass
class GameInfo:
    """Модель информации об игре"""
    name: str
    rating: Optional[float] = None
    released: Optional[str] = None
    platforms: Optional[str] = None
    genres: Optional[str] = None
    description: Optional[str] = None
    background_image: Optional[str] = None
    
    def __str__(self):
        return f"Game(name='{self.name}', rating={self.rating})"
