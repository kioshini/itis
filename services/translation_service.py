"""
Сервис для перевода текстов
"""
import aiohttp
from typing import Optional


class TranslationService:
    """Класс для перевода текстов с английского на русский"""
    
    def __init__(self):
        # Используем бесплатный API MyMemory (лимит 1000 слов в день)
        self.api_url = "https://api.mymemory.translated.net/get"
    
    async def translate_to_russian(self, text: str) -> str:
        """
        Перевод текста с английского на русский
        
        Args:
            text: Текст для перевода
            
        Returns:
            Переведенный текст или оригинал в случае ошибки
        """
        if not text or len(text.strip()) == 0:
            return text
        
        # Если текст слишком длинный, переводим по частям
        if len(text) > 500:
            return await self._translate_long_text(text)
        
        try:
            params = {
                "q": text,
                "langpair": "en|ru"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.api_url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        translated = data.get('responseData', {}).get('translatedText', text)
                        return translated if translated else text
                    else:
                        print(f"Ошибка перевода: {response.status}")
                        return text
                        
        except Exception as e:
            print(f"Ошибка при переводе текста: {e}")
            return text
    
    async def _translate_long_text(self, text: str) -> str:
        """Перевод длинного текста по частям"""
        # Разбиваем текст на предложения
        sentences = text.split('. ')
        translated_sentences = []
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < 400:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    translated = await self.translate_to_russian(current_chunk.strip())
                    translated_sentences.append(translated)
                current_chunk = sentence + ". "
        
        # Переводим последний chunk
        if current_chunk:
            translated = await self.translate_to_russian(current_chunk.strip())
            translated_sentences.append(translated)
        
        return " ".join(translated_sentences)


# Глобальный экземпляр сервиса
translation_service = TranslationService()
