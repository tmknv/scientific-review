# scientific_review/client.py
# Асинхронный клиент OpenRouter для всех агентов и baseline

import aiohttp
from typing import List, Dict

from scientific_review.utils.params import get_params
from scientific_review.utils.settings import get_settings
from scientific_review.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)
params = get_params()
settings = get_settings()


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
        base_url: str = params["openrouter"]["base_url"],
        timeout: int = params["openrouter"]["timeout"],
    ):
        self.api_key = settings.OPENROUTER_API_KEY
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
            logger.debug(f"Отправка запроса в OpenRouter | model={model}")

            async with self.session.post(self.base_url, json=payload, headers=headers) as response:
                text = await response.text()
                status = response.status

                logger.debug(f"Response status: {status}")

                if status != 200:
                    logger.error(f"HTTP ERROR {status}: {text}")
                    return ""

                try:
                    data = await response.json()
                except Exception:
                    logger.error(f"Не удалось распарсить JSON. Raw response: {text}")
                    return ""

                if "error" in data:
                    logger.error(f"OpenRouter API error: {data['error']}")
                    return ""

                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not content:
                    logger.warning(f"Пустой ответ от модели. Raw: {data}")

                return content

        except aiohttp.ClientError as e:
            logger.error(f"Запрос не удался (ClientError): {e}")
            return ""

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return ""
