# scientific_review/client.py
# Асинхронный клиент OpenRouter для всех агентов и baseline

import aiohttp
from typing import Dict, Any
import json

from scientific_review.config import OPENROUTER_API_KEY


class Client:
    """
    Асинхронный клиент OpenRouter

    Атрибуты:
        api_key: API ключ OpenRouter
        model: Модель по умолчанию
        base_url: URL OpenRouter API
        timeout: Таймаут запроса в секундах
    """

    def __init__(
        self,
        model: str = "nvidia/nemotron-3-nano-30b-a3b:free",
        base_url: str = "https://openrouter.ai/api/v1/chat/completions",
        timeout: int = 60,
    ):
        self.api_key = OPENROUTER_API_KEY
        self.model = model
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
            self.session = None

    async def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Асинхронно отправляет запрос в OpenRouter и возвращает результат.

        Args:
            prompt: Строка запроса

        Returns:
            Dict[str, Any]: Распарсенный результат нейронки
        """
        if not self.session:
            raise RuntimeError("client session не инициализирован")

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            async with self.session.post(self.base_url, json=payload, headers=headers) as response:
                data = await response.json()

                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

                return content

        except Exception as e:
            return {"error": str(e)}
