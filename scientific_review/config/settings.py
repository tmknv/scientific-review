from dotenv import load_dotenv
import os
import yaml

load_dotenv()

class Settings:
    OPENROUTER_API_KEY: str | None = os.getenv("OPENROUTER_API_KEY")
    TG_TOKEN: str | None = os.getenv("TG_TOKEN")

    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "qwen/qwen3-4b")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", 0.3))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", 1500))
    TIMEOUT: int = int(os.getenv("TIMEOUT", 60))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        
settings = Settings()

with open("scientific_review/config/models.yaml", "r", encoding="utf-8") as f:
    MODELS = yaml.safe_load(f) or {}
