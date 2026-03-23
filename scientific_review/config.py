# загрузка .env, конфигурации

import os
import yaml
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

with open("scientific_review/prompts.yaml", "r") as f:
    PROMPTS = yaml.safe_load(f)
