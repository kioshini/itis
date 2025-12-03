"""
Сервис для работы с OpenRouter API (интеграция с нейросетью)
Работает ТОЛЬКО с AI, без RAWG API
"""
import aiohttp
import json
import re
from typing import List, Optional, Dict, Any
import config


class AIService:
    """Класс для работы с OpenRouter API"""
    
    def __init__(self):
        self.api_url = config.OPENROUTER_API_URL
        self.api_key = config.OPENROUTER_API_KEY
        self.model = config.OPENROUTER_MODEL
    
    async def get_game_recommendations_with_details(self, user_query: str) -> Optional[List[Dict[str, Any]]]:
        """
        Получение подробных рекомендаций игр от нейросети
        
        Args:
            user_query: Описание игры от пользователя
            
        Returns:
            Список словарей с информацией об играх или None в случае ошибки
        """
        
        # Формирование промпта для нейросети
        system_prompt = """Ты - эксперт по видеоиграм. Твоя задача - рекомендовать игры и предоставить детальную информацию о них на русском языке.

ВАЖНО:
1. Порекомендуй от 3 до 5 подходящих игр
2. Для каждой игры предоставь: название, жанры, платформы, год выпуска, рейтинг (примерный из 5), краткое описание (2-3 предложения)
3. Формат ответа - JSON массив объектов
4. ВСЕ описания и информация должны быть НА РУССКОМ ЯЗЫКЕ
5. Название игры на английском, остальное на русском

Пример правильного ответа:
[
  {
    "name": "The Witcher 3: Wild Hunt",
    "genres": "RPG, Приключения, Открытый мир",
    "platforms": "PC, PlayStation, Xbox, Nintendo Switch",
    "released": "2015",
    "rating": 4.8,
    "description": "Эпическая ролевая игра с открытым миром о ведьмаке Геральте из Ривии. Путешествуйте по огромному фантазийному миру, сражайтесь с монстрами и принимайте решения, влияющие на судьбу персонажей. Игра славится глубоким сюжетом и проработанными квестами."
  }
]"""

        user_prompt = f"""Пользователь описывает игру, которую он ищет:
"{user_query}"

Порекомендуй 3-5 подходящих игр с подробной информацией в формате JSON. Все описания на русском языке!"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
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
                        
                        # Извлечение JSON из ответа
                        try:
                            # Ищем JSON в ответе (может быть обернут в markdown)
                            json_match = re.search(r'\[.*\]', content, re.DOTALL)
                            if json_match:
                                json_str = json_match.group(0)
                                games = json.loads(json_str)
                                print(f"✅ Получено {len(games)} игр от AI")
                                return games
                            else:
                                print("❌ JSON не найден в ответе AI")
                                print(f"Ответ AI: {content[:300]}...")
                                return None
                        except json.JSONDecodeError as e:
                            print(f"❌ Ошибка парсинга JSON: {e}")
                            print(f"Ответ AI: {content[:300]}...")
                            return None
                    else:
                        error_text = await response.text()
                        print(f"❌ Ошибка OpenRouter API: {response.status} - {error_text}")
                        if response.status == 401:
                            print("⚠️ API ключ OpenRouter недействителен.")
                            print("📝 Получите новый ключ на: https://openrouter.ai/")
                        elif response.status == 402:
                            print("⚠️ Недостаточно кредитов на аккаунте OpenRouter.")
                            print("💳 Пополните баланс на: https://openrouter.ai/settings/credits")
                        return None
                        
        except aiohttp.ClientError as e:
            print(f"❌ Ошибка при запросе к OpenRouter: {e}")
            return None
        except Exception as e:
            print(f"❌ Неожиданная ошибка в AIService: {e}")
            return None


# Глобальный экземпляр сервиса
ai_service = AIService()
