# scientific_review/utils.py
# Утилиты: парсинг json, работа с файлами, вспомогательные функции

import json
import re
import os
from datetime import datetime
from typing import Any, Dict, Union, List, Tuple
from functools import lru_cache

from scientific_review.utils.params import get_params

from scientific_review.agents.state import State
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

params = get_params()


def extract_json(text: str) -> Dict[str, Any]:
    """
    Извлекает и парсит json из текстового ответа LLM.

    Сначала пытается распарсить текст целиком. Если не выходит, ищет 
    первое вхождение текста между фигурными скобками {}.

    Args:
        text: Строка от нейронки

    Returns:
        Словарь с данными из json или пустой словарь, если парсинг не удался.
    """

    if not text:
        return {}

    try:
        return json.loads(text)
    except:
        pass

    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        candidate = match.group()

        try:
            return json.loads(candidate)
        except:
            try:
                return json.loads(candidate.replace("'", '"'))
            except:
                pass

    return {}


def serialize(obj):
    # langchain messages
    if isinstance(obj, BaseMessage):
        return {
            "type": obj.type,
            "content": obj.content
        }

    # State / любые объекты
    if hasattr(obj, "__dict__"):
        return {k: serialize(v) for k, v in obj.__dict__.items()}

    # list
    if isinstance(obj, list):
        return [serialize(x) for x in obj]

    # dict
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}

    return obj


def save_json(data: Union[Dict[str, Any], list], folder: str) -> str:
    """
    Сохраняет словарь в json с уникальным именем на основе времени.

    Создает папку, если она не существует. Имя файла включает микросекунды,
    чтобы избежать коллизий при быстрой записи.

    Args:
        data: Словарь или список для сохранения
        folder: Путь к директории, в которую нужно сохранить файл

    Returns:
        Полный путь к созданному файлу
    """
    os.makedirs(folder, exist_ok=True)

    name = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".json"
    path = os.path.join(folder, name)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(serialize(data), f, indent=2, ensure_ascii=False)

    return path


def final_score(state: State) -> float:
    """
    Вычисляет среднее арифметическое всех оценок в объекте состояния.

    Args:
        state: Объект состояния агента

    Returns:
        Средний балл, округленный до 2 знаков после запятой. Возвращает -1.0, если список оценок пуст
    """
    scores = state.scores

    if not scores:
        return -1.0

    final_score_val = sum(scores.values()) / len(scores)

    return round(final_score_val, 2)


def print_json(state: State) -> None:
    """
    Выводит объект State в консоль в формате красиво отформатированного json.

    Args:
        state: Объект состояния агента, который нужно визуализировать
    """
    data = state_to_dict(state)
    formatted_json = json.dumps(data, indent=4, ensure_ascii=False)

    print(formatted_json)


def message_to_dict(msg: BaseMessage) -> Dict[str, Any]:
    """
    Преобразует объект сообщения LLM в словарь для json-формата.

    Args:
        msg: Сообщение LLM

    Returns:
        Словарь с ключами 'type' (msg.type) и 'content' (msg.content)
    """
    return {
        "type": msg.type,
        "content": msg.content,
    }


def state_to_dict(state: State) -> Dict[str, Any]:
    """
    Преобразует объект State в словарь, пригодный для сохранения в в json.
    Использует message_to_dict для преобразования сообщений.

    Args:
        state: Объект состояния агента

    Returns:
        Словарь с данными из State, готовый для json-формата
    """
    if isinstance(state, dict):
        data = state.copy()
        if "messages" in data:
            data["messages"] = [message_to_dict(msg) for msg in data["messages"]]
    else:
        data = state.__dict__.copy()
        data["messages"] = [message_to_dict(msg) for msg in getattr(state, "messages", [])]

    return data


def extract_scores(result: Union[Dict[str, Any], State]) -> List[float]:
    """
    Извлекает оценки в фиксированном порядке.

    Args:
        result: State или словарь с ключом "scores"

    Returns:
        Список оценок: [novelty, scientificity, readability, complexity]
    """
    # получаем словарь оценок
    if isinstance(result, State):
        scores = result.scores
    elif isinstance(result, dict):
        scores = result.get("scores", {})
    else:
        raise TypeError(f"Unexpected result type: {type(result)}")

    order = params["criteria"]["order"]
    # возвращаем список оценок в нужном порядке, -1 если отсутствует
    return [scores.get(key, -1) for key in order]


def serialize_messages(messages: List) -> List[Dict]:
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


@lru_cache()
def load_dataset(path: str) -> Tuple[List[str], List[List[float]]]:
    """
    Загружает датасет PeerRead.

    Args:    
        path: Путь к файлу с датасетом

    Returns:
        texts: Список текстов из датасета
        human_scores: Список списков human-оценок для каждого текста
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = []
    human_scores = []
    order = params["criteria"]["order"]

    for item in data:
        texts.append(item["text"])

        scores = item["scores"]

        human_scores.append([
            float(scores.get(key, -1)) for key in order
        ])

    return texts, human_scores
