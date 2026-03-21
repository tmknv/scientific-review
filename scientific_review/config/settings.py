from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "qwen/qwen3-4b")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", 0.3))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", 1500))
    TIMEOUT: int = int(os.getenv("TIMEOUT", 60))

settings = Settings()

if not settings.OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set")