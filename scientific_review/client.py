# scientific_review/client.py
# Асинхронный клиент OpenRouter для всех агентов и baseline

import asyncio
from collections import deque
import time
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
        semaphore: asyncio.Semaphore = asyncio.Semaphore(3),
        rpm_limit: int = 15,
    ):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.semaphore = semaphore
        self.session: aiohttp.ClientSession | None = None

        self.rpm_limit = rpm_limit
        self._requests = deque()
        self._rl_lock = asyncio.Lock()

    # для async with Client() as client
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
            self.session = None

    async def _acquire_rate_limit(self):
        """
        Ограничение: rpm_limit запросов за 60 секунд
        """
        async with self._rl_lock:
            now = time.time()

            # удаляем старые запросы (>60 сек)
            while self._requests and now - self._requests[0] > 60:
                self._requests.popleft()

            # если лимит достигнут — ждём
            if len(self._requests) >= self.rpm_limit:
                sleep_time = 60 - (now - self._requests[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

                # пересчёт после сна
                now = time.time()
                while self._requests and now - self._requests[0] > 60:
                    self._requests.popleft()

            self._requests.append(time.time())


    async def generate(self, messages: List[Dict], model: str, temperature: float = 0.4) -> str:
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
            "temperature": temperature
        }

        try:
            logger.debug(f"Отправка запроса в OpenRouter | model={model}")

            await self._acquire_rate_limit()

            async with self.semaphore:
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
