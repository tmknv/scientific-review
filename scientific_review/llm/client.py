import time
import requests

from scientific_review.config.settings import settings


class LLMClient:
    def __init__(self, model=None, temperature=0.3, max_tokens=1200):
        self.model = model or settings.DEFAULT_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens

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
            timeout=settings.TIMEOUT,
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
