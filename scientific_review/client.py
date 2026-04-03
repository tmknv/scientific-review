# scientific_review/client.py
# Асинхронный клиент OpenRouter для всех агентов и baseline

import aiohttp
from typing import List, Dict

from scientific_review.config import OPENROUTER_API_KEY
from scientific_review.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class Client:
    """
    Асинхронный клиент OpenRouter

    Atributes:
        api_key: API ключ OpenRouter
        base_url: URL OpenRouter API
        timeout: Таймаут запроса в секундах
    """

    def __init__(
        self,
        base_url: str = "https://openrouter.ai/api/v1/chat/completions",
        timeout: int = 60,
    ):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: aiohttp.ClientSession | None = None

    # для async with Client() as client
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
            self.session = None

    async def generate(self, messages: List[Dict], model: str) -> str:
        """
        Асинхронно отправляет запрос в OpenRouter и возвращает результат.

        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}]
            model: Модель 

        Returns:
            Результат нейронки
        """
        if not self.session:
            raise RuntimeError("Client session не инициализирован")

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": model,
            "messages": messages,
        }

        try:
            logger.info(f"Отправка запроса в OpenRouter: модель={model}")
            async with self.session.post(self.base_url, json=payload, headers=headers) as response:
                logger.info(f"Получен ответ от OpenRouter: модель={model}")

                # text = await response.text()

                # print("STATUS:", response.status)
                # print("RAW RESPONSE:", text)

                data = await response.json()

                # print("PARSED RESPONSE:", data)
                
                if "error" in data:
                    logger.error(f"API ERROR: {response.status} - {data['error']}")
                    return ""

                return data.get("choices", [{}])[0].get("message", {}).get("content", "")


        except Exception as e:
            logger.error(f"REQUEST FAILED: {e}")
            return ""
