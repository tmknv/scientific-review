import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
        self.OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen/qwen3-4b:free")
        self.TIMEOUT = int(os.getenv("TIMEOUT", "60"))

settings = Settings()
