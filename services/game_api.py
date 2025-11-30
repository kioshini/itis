"""
Сервис для работы с RAWG API (база данных видеоигр)
"""
import aiohttp
from typing import Optional, Dict, Any
import re
import config
from database.models import GameInfo
from services.translation_service import translation_service


class GameAPIService:
    """Класс для работы с RAWG API"""
    
    # Словарь для перевода жанров
    GENRE_TRANSLATIONS = {
        "Action": "Экшен",
        "Adventure": "Приключения",
        "RPG": "RPG",
        "Strategy": "Стратегия",
        "Shooter": "Шутер",
        "Puzzle": "Головоломка",
        "Racing": "Гонки",
        "Sports": "Спорт",
        "Simulation": "Симулятор",
        "Platformer": "Платформер",
        "Fighting": "Файтинг",
        "Arcade": "Аркада",
        "Indie": "Инди",
        "Casual": "Казуальная",
        "Family": "Семейная",
        "Board Games": "Настольные игры",
        "Educational": "Образовательная",
        "Card": "Карточная"
    }
    
    # Словарь для перевода платформ
    PLATFORM_TRANSLATIONS = {
        "PC": "ПК",
        "PlayStation": "PlayStation",
        "Xbox": "Xbox",
        "Nintendo Switch": "Nintendo Switch",
        "iOS": "iOS",
        "Android": "Android",
        "macOS": "macOS",
        "Linux": "Linux"
    }
    
    def __init__(self):
        self.api_url = config.RAWG_API_URL
        self.api_key = config.RAWG_API_KEY
    
    def _translate_text(self, text: str, translations_dict: dict) -> str:
        """Перевод текста используя словарь"""
        for eng, rus in translations_dict.items():
            text = text.replace(eng, rus)
        return text
    
    async def search_game(self, game_name: str) -> Optional[GameInfo]:
        """
        Поиск информации об игре по названию
        
        Args:
            game_name: Название игры
            
        Returns:
            Объект GameInfo с информацией об игре или None
        """
        params = {
            "key": self.api_key,
            "search": game_name,
            "page_size": 1
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Поиск игры
                async with session.get(
                    f"{self.api_url}/games",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        print(f"Ошибка RAWG API при поиске: {response.status}")
                        return None
                    
                    data = await response.json()
                    
                    if not data.get('results'):
                        return None
                    
                    game_data = data['results'][0]
                    game_id = game_data['id']
                
                # Получение детальной информации
                async with session.get(
                    f"{self.api_url}/games/{game_id}",
                    params={"key": self.api_key},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        # Возвращаем базовую информацию, если детали недоступны
                        return self._parse_basic_game_info(game_data)
                    detailed_data = await response.json()
                    return await self._parse_game_info(detailed_data)
                    return self._parse_game_info(detailed_data)
                    
        except aiohttp.ClientError as e:
            print(f"Ошибка при запросе к RAWG API: {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка в GameAPIService: {e}")
            return None
    
    def _parse_basic_game_info(self, data: Dict[str, Any]) -> GameInfo:
        """Парсинг базовой информации об игре"""
        platforms = ", ".join([p['platform']['name'] for p in data.get('platforms', [])[:5]])
        genres = ", ".join([g['name'] for g in data.get('genres', [])[:3]])
        
        return GameInfo(
            name=data.get('name', 'Неизвестно'),
            rating=data.get('rating'),
            released=data.get('released'),
            platforms=platforms or None,
            genres=genres or None,
            background_image=data.get('background_image')
        )
    
    async def _parse_game_info(self, data: Dict[str, Any]) -> GameInfo:
        """Парсинг полной информации об игре"""
        platforms = ", ".join([p['platform']['name'] for p in data.get('platforms', [])[:5]])
        genres = ", ".join([g['name'] for g in data.get('genres', [])[:3]])
        
        # Перевод жанров и платформ
        genres = self._translate_text(genres, self.GENRE_TRANSLATIONS)
        platforms = self._translate_text(platforms, self.PLATFORM_TRANSLATIONS)
        
        # Очистка HTML из описания
        description = data.get('description_raw') or data.get('description', '')
        if description:
            # Удаление HTML-тегов
            description = re.sub(r'<[^>]+>', '', description)
            # Ограничение длины
            if len(description) > 500:
                description = description[:497] + "..."
            
            # Перевод описания на русский
            description = await translation_service.translate_to_russian(description)
        
        return GameInfo(
            name=data.get('name', 'Неизвестно'),
            rating=data.get('rating'),
            released=data.get('released'),
            platforms=platforms or None,
            genres=genres or None,
            description=description or None,
            background_image=data.get('background_image')
        )


# Глобальный экземпляр сервиса
game_api_service = GameAPIService()
