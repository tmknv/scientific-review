# scientific_review/utils/load_prompts.py
# загрузка промптов из prompts.yaml

# scientific_review/load_prompts.py

import yaml
from functools import lru_cache
from typing import Dict, Any


# @lru_cache()
def get_prompts(path: str = "scientific_review/prompts.yaml") -> Dict[str, Any]:
    """
    Загружает prompts.yaml (кэшируется)

    Args:
        path: путь к yaml

    Returns:
        Словарь с промптами
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# def build_prompt(name: str, **kwargs) -> str:
#     """
#     Собирает prompt из system + user с подстановкой переменных.

#     Args:
#         name: имя промпта
#         **kwargs: переменные ({text}, {scores}, ...)

#     Returns:
#         Готовый промпт
#     """
#     prompts = get_prompts()

#     if name not in prompts:
#         raise ValueError(f"Prompt '{name}' не найден")

#     prompt_data = prompts[name]

#     system_prompt = prompt_data.get("system_prompt", "")
#     user_prompt = prompt_data.get("user_prompt", "")

#     prompt = system_prompt + "\n" + user_prompt

#     for key, value in kwargs.items():
#         prompt = prompt.replace(f"{{{key}}}", str(value))

#     return prompt

def get_prompt_parts(name: str, **kwargs) -> tuple[str, str]:
    """Возвращает system_prompt и user_prompt отдельно, с подстановкой переменных.
    
     Args:
        name: имя промпта
        **kwargs: переменные ({text}, {scores}, ...)

    Returns:
        Кортеж (system_prompt, user_prompt)
    """
    
    prompts = get_prompts()

    if name not in prompts:
        raise ValueError(f"Prompt '{name}' не найден")

    prompt_data = prompts[name]

    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "")

    for key, value in kwargs.items():
        system_prompt = system_prompt.replace(f"{{{key}}}", str(value))
        user_prompt = user_prompt.replace(f"{{{key}}}", str(value))

    return system_prompt, user_prompt


def build_prompt(name: str, **kwargs) -> str:
    """Собирает полный prompt из system + user с подстановкой переменных.
     Args:
        name: имя промпта
        **kwargs: переменные ({text}, {scores}, ...)
    Returns:
        prompt: полный промпт
    """
    system_prompt, user_prompt = get_prompt_parts(name, **kwargs)
    return system_prompt + "\n" + user_prompt
