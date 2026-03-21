import os
import time
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class LLMClient:
    def __init__(
        self,
        model="qwen/qwen3-4b",
        temperature=0.3,
        max_tokens=1500,
        timeout=60,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    def generate(self, prompt: str):
        start = time.time()

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            timeout=self.timeout,
        )

        latency = time.time() - start

        if response.status_code != 200:
            raise RuntimeError(f"LLM error: {response.text}")

        data = response.json()
        text = data["choices"][0]["message"]["content"]

        usage = data.get("usage", {})

        return {
            "text": text,
            "latency": latency,
            "usage": usage,
        }