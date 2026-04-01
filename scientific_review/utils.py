# scientific_review/utils.py
# Утилиты: парсинг json, работа с файлами, вспомогательные функции

import yaml
import json
import re
import os
from datetime import datetime
from typing import Any, Dict, Union, List

from scientific_review.agents.state import State
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


with open("scientific_review/prompts.yaml", "r", encoding="utf-8") as f:
    PROMPTS: Dict[str, Any] = yaml.safe_load(f)

def build_prompt(name: str, **kwargs) -> str:
    """
    Собирает prompt из system + user с подстановкой переменных.

    Args:
        name: Имя промпта
        **kwargs: Переменные ({text}, {scores}, ...)

    Returns:
        str: Готовый prompt
    """
    if name not in PROMPTS:
        raise ValueError(f"Prompt '{name}' не найден")

    prompt_data = PROMPTS[name]

    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "")

    prompt = system_prompt + "\n" + user_prompt

    for key, value in kwargs.items():
        prompt = prompt.replace(f"{{{key}}}", str(value))

    return prompt


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

    try:
        return json.loads(text)
    except Exception as e:
        print(f"Ошибка парсинга JSON: {e}")

    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception as e:
            print(f"Ошибка парсинга JSON после регулярного выражения: {e}")

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
        Полный путь к созданному файлу
    """
    os.makedirs(folder, exist_ok=True)

    name = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".json"
    path = os.path.join(folder, name)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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


# def extract_scores(result: Dict[str, Any]) -> List[float]:
#     """
#     Извлекает оценки в фиксированном порядке.

#     Args:
#         result: Результат работы пайплайна в виде словаря

#     Returns:
#         Список оценок: [novelty, scientificity, readability, complexity]
#     """
#     scores = result.get("scores", {})

#     return [
#         scores.get("novelty", -1),
#         scores.get("scientificity", -1),
#         scores.get("readability", -1),
#         scores.get("complexity", -1),
#     ]
def extract_scores(result: Union[Dict[str, Any], State]) -> List[float]:
    """
    Извлекает оценки в фиксированном порядке.

    Args:
        result: State или словарь с ключом "scores"

    Returns:
        Список оценок: [novelty, scientificity, readability, complexity]
    """
    # Получаем словарь оценок
    if isinstance(result, State):
        scores = result.scores
    elif isinstance(result, dict):
        scores = result.get("scores", {})
    else:
        raise TypeError(f"Unexpected result type: {type(result)}")

    # Возвращаем список оценок в нужном порядке, -1 если отсутствует
    return [
        scores.get("novelty", -1),
        scores.get("scientificity", -1),
        scores.get("readability", -1),
        scores.get("complexity", -1),
    ]

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
