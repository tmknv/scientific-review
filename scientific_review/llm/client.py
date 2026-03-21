# llm/client.py
import httpx
import time
from typing import Dict, Any

from scientific_review.config.settings import settings


class LLMClient:
    def __init__(
        self,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        timeout: float | None = None,
    ):
        self.model = model or settings.DEFAULT_MODEL
        self.temperature = temperature or settings.TEMPERATURE
        self.max_tokens = max_tokens or settings.MAX_TOKENS
        self.timeout = timeout or settings.TIMEOUT

        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"

        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
        )

    async def generate(self, prompt: str) -> Dict[str, Any]:
        start = time.perf_counter()

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        try:
            resp = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

            text = data["choices"][0]["message"]["content"]
            latency = time.perf_counter() - start

            return {
                "text": text,
                "latency": latency,
                "usage": data.get("usage", {}),
            }

        except httpx.HTTPError as e:
            raise RuntimeError(f"LLM request failed: {e}") from e

    async def close(self):
        await self.client.aclose()