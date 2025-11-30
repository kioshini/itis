"""
Сервис для работы с OpenRouter API (интеграция с нейросетью)
"""
import aiohttp
import json
import re
from typing import List, Optional
import config


class AIService:
    """Класс для работы с OpenRouter API"""
    
    def __init__(self):
        self.api_url = config.OPENROUTER_API_URL
        self.api_key = config.OPENROUTER_API_KEY
        self.model = config.OPENROUTER_MODEL
    
    async def get_game_recommendations(self, user_query: str) -> Optional[List[str]]:
        """
        Получение рекомендаций игр от нейросети
        
        Args:
            user_query: Описание игры от пользователя
            
        Returns:
            Список названий игр (3-5 штук) или None в случае ошибки
        """
        
        # Формирование промпта для нейросети
        system_prompt = """Ты - эксперт по видеоиграм. Твоя задача - рекомендовать игры на основе описания пользователя.

ВАЖНО:
1. Верни ТОЛЬКО названия игр на английском языке
2. Количество игр: от 3 до 5
3. Формат ответа: каждая игра с новой строки, без нумерации
4. Указывай только официальные названия игр
5. Не добавляй никаких пояснений, только названия

Пример правильного ответа:
The Witcher 3: Wild Hunt
Red Dead Redemption 2
God of War"""

        user_prompt = f"""Пользователь описывает игру, которую он ищет:
"{user_query}"

Порекомендуй 3-5 подходящих игр."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com",  # Необходимо для OpenRouter
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        
                        # Парсинг ответа - извлечение названий игр
                        games = [
                            line.strip() 
                            for line in content.strip().split('\n') 
                            if line.strip() and not line.strip().startswith('#')
                        ]
                        
                        # Очистка от нумерации (1., 2., и т.д.)
                        games = [
                            game.split('.', 1)[-1].strip() if '.' in game[:3] else game
                            for game in games
                        ]
                        
                        # Ограничение до 5 игр
                    else:
                        error_text = await response.text()
                        print(f"Ошибка OpenRouter API: {response.status} - {error_text}")
                        # Используем запасной метод при ошибке
                        return await self._fallback_search(user_query)
                        
        except aiohttp.ClientError as e:
            print(f"Ошибка при запросе к OpenRouter: {e}")
            # Используем запасной метод при ошибке
            return await self._fallback_search(user_query)
        except Exception as e:
            print(f"Неожиданная ошибка в AIService: {e}")
            # Используем запасной метод при ошибке
            return await self._fallback_search(user_query)
    
    async def _fallback_search(self, user_query: str) -> Optional[List[str]]:
        """
        Запасной метод поиска без AI - извлекаем ключевые слова и ищем в RAWG
        
        Args:
            user_query: Описание от пользователя
            
        Returns:
            Список названий игр или None
        """
        print("Используем запасной метод поиска без AI...")
        
        # Извлекаем ключевые слова (жанры, типы игр)
        keywords_map = {
            'rpg': 'RPG',
            'рпг': 'RPG',
            'шутер': 'shooter',
            'shooter': 'shooter',
            'стратег': 'strategy',
            'strategy': 'strategy',
            'космос': 'space',
            'space': 'space',
            'строительств': 'building',
            'building': 'building',
            'выживан': 'survival',
            'survival': 'survival',
            'открыт': 'open world',
            'open world': 'open world',
            'приключен': 'adventure',
            'adventure': 'adventure',
            'симулятор': 'simulation',
            'simulation': 'simulation',
            'гонк': 'racing',
            'racing': 'racing',
            'спорт': 'sports',
            'sports': 'sports'
        }
        
        # Поиск ключевых слов в запросе
        query_lower = user_query.lower()
        found_keywords = []
        
        for key, value in keywords_map.items():
            if key in query_lower:
                if value not in found_keywords:
                    found_keywords.append(value)
        
        # Формируем поисковый запрос
        search_query = ' '.join(found_keywords[:3]) if found_keywords else user_query[:50]
        
        # Ищем игры напрямую в RAWG API
        try:
            params = {
                "key": config.RAWG_API_KEY,
                "search": search_query,
                "page_size": 5,
                "ordering": "-rating"  # Сортировка по рейтингу
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{config.RAWG_API_URL}/games",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        games = [game['name'] for game in data.get('results', [])[:5]]
                        print(f"Найдено игр через запасной метод: {len(games)}")
                        return games if games else None
                    else:
                        print(f"Ошибка RAWG API: {response.status}")
                        return None
        except Exception as e:
            print(f"Ошибка в запасном методе поиска: {e}")
            return None


# Глобальный экземпляр сервиса
ai_service = AIService()
