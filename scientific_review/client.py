# единый клиент для работы с openrouter (используется в baseline, агентах и judge)

import requests
from scientific_review.config import OPENROUTER_API_KEY


class Client:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY

    def generate(self, prompt, model = "nvidia/nemotron-3-nano-30b-a3b:free"):
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
            },
            timeout=60,
        )

        try:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception:
            print("ошибочка от опенроутер:", response.text)
            return ""
