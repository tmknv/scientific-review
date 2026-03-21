import time
import requests

from scientific_review.config.settings import settings


class LLMClient:
    def __init__(self, model=None, temperature=None, max_tokens=None, timeout=None):
        self.model = model or settings.DEFAULT_MODEL
        self.temperature = temperature if temperature is not None else settings.TEMPERATURE
        self.max_tokens = max_tokens if max_tokens is not None else settings.MAX_TOKENS
        self.timeout = timeout if timeout is not None else settings.TIMEOUT

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            }
        )

    def generate(self, prompt):
        start = time.perf_counter()

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        response = self.session.post(
            f"{settings.OPENROUTER_BASE_URL}/chat/completions",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "text": data["choices"][0]["message"]["content"],
            "usage": data.get("usage", {}),
            "latency": round(time.perf_counter() - start, 4),
        }

    def close(self):
        self.session.close()
