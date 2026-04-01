# scientific_review/config.py
# загрузка .env, конфигурации

import os

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODELS = {
    "baseline": "qwen/qwen3.6-plus-preview:free",
    "agent": "nvidia/nemotron-3-nano-30b-a3b:free",
    "judge": "nvidia/nemotron-3-nano-30b-a3b:free",
}
