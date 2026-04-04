# scientific_review/utils/settings.p
# для получения секретов из .env

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Глобальные настройки приложения (секреты из .env)

    Attributes:
        OPENROUTER_API_KEY: API ключ OpenRouter
        model_config: Настройки парсинга данных из .env
    """

    OPENROUTER_API_KEY: str = Field(..., description="OpenRouter API key")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Возвращает объект с настройками приложения.

    Returns:
        Settings: Объект с настройками приложения
    """
    return Settings()


if __name__ == "__main__":
    settings = get_settings()
    print("OpenRouter API Key:", settings.OPENROUTER_API_KEY)
