# scientific_review/utils.py
# Утилиты: парсинг json, работа с файлами, вспомогательные функции

import yaml
import json
import re
import os
from datetime import datetime
from typing import Any, Dict, Union

from scientific_review.agents.state import State


def extract_json(text: str) -> Dict[str, Any]:
    """
    Извлекает и парсит json из текстового ответа LLM.

    Сначала пытается распарсить текст целиком. Если не выходит, ищет 
    первое вхождение текста между фигурными скобками {}.

    Args:
        text: Строка от нейронки

    Returns:
        Словарь с данными из JSON. 
        Пустой словарь {}, если парсинг не удался
    """

    try:
        return json.loads(text)
    except:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass

    return {}


def save_json(data: Union[Dict[str, Any], list], folder: str) -> str:
    """
    Сохраняет словарь в json с уникальным именем на основе времени.

    Создает папку, если она не существует. Имя файла включает микросекунды,
    чтобы избежать коллизий при быстрой записи.

    Args:
        data: Словарь или список для сохранения
        folder: Путь к директории, в которую нужно сохранить файл

    Returns:
        path: Полный путь к созданному файлу
    """
    os.makedirs(folder, exist_ok=True)

    name = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".json"
    path = os.path.join(folder, name)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return path


def final_score(state: State) -> float:
    """Вычисляет среднее арифметическое всех оценок в объекте состояния.

    Args:
        state: Объект состояния агента

    Returns:
        Средний балл, округленный до 2 знаков после запятой
        Возвращает -1.0, если список оценок пуст
    """
    scores = state.scores

    if not scores:
        return -1.0

    final_score_val = sum(scores.values()) / len(scores)
    return round(final_score_val, 2)


def print_json(obj: Any) -> None:
    """
    Выводит объект в консоль в формате красиво отформатированного json.

    Args:
        obj: Объект, который нужно визуализировать
    """
    if hasattr(obj, "__dict__"):
        data = obj.__dict__
    else:
        data = obj
    formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
    print(formatted_json)


def load_prompts() -> Dict[str, str]:
    """
    Загружает шаблоны промптов из YAML-файла конфигурации.

    Returns:
        Словарь, где ключи - названия, а значения - текст промптов

    Raises:
        FileNotFoundError: Если файл 'scientific_review/prompts.yaml' не найден
    """
    with open("scientific_review/prompts.yaml", "r") as f:
        PROMPTS = yaml.safe_load(f)
    return PROMPTS
