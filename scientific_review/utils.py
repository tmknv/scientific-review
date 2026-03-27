# scientific_review/utils.py
# Утилиты: парсинг json, работа с файлами, вспомогательные функции

import yaml
import json
import re
import os
from datetime import datetime
from typing import Any, Dict, Union

from scientific_review.agents.state import State
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


def message_to_dict(msg: BaseMessage) -> dict:
    """
    Преобразует объект сообщения LLM в словарь для JSON-сериализации.

    Args:
        msg (BaseMessage): Сообщение LLM (HumanMessage, AIMessage, SystemMessage или другое)

    Returns:
        dict: Словарь с ключами:
            - "type": тип сообщения ('human', 'ai', 'system' и т.д.)
            - "content": текстовое содержимое сообщения
    """
    return {
        "type": msg.type,
        "content": msg.content,
    }


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
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
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


def print_json(state: State) -> None:
    """
    Выводит объект State в консоль в формате красиво отформатированного JSON.

    Args:
        state (State): Объект состояния агента, который нужно визуализировать

    Returns:
        None
    """
    data = state_to_dict(state)
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


def state_to_dict(state: State) -> Dict[str, Any]:
    """
    Преобразует объект State в словарь, пригодный для сериализации в JSON.

    Args:
        state (State): Объект состояния агента

    Returns:
        Dict[str, Any]: Словарь с полями State, включая сериализованные сообщения
                        Сообщения преобразуются через message_to_dict
    """
    data = state.__dict__.copy()

    data["messages"] = [message_to_dict(msg) for msg in state.messages]

    return data

def serialize_messages(messages: list) -> list[dict]:
    """
    Преобразует список LangChain сообщений (HumanMessage, AIMessage, SystemMessage)

    args:
        messages: Список сообщений в формате LangChain

    returns:
        Список словарей с ключами "role" и "content", готовых для передачи в LLM
    """
    serialized = []
    
    for m in messages:
        if isinstance(m, HumanMessage):
            role = "user"
        elif isinstance(m, AIMessage):
            role = "assistant"
        elif isinstance(m, SystemMessage):
            role = "system"
        else:
            raise ValueError(f"Unsupported message type: {type(m)}")
        
        serialized.append({
            "role": role,
            "content": m.content
        })
    
    return serialized