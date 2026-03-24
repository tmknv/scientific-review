# утилиты: парсинг json, работа с файлами, вспомогательные функции

import json
import re
import os
from datetime import datetime


def extract_json(text):
    """
    пытается вытащить json из ответа llm
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


def save_json(data, folder):
    """
    сохраняем json
    """
    os.makedirs(folder, exist_ok=True)

    name = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".json"
    path = os.path.join(folder, name)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return path


def final_score(state) -> float:
    scores = state.scores

    if not scores:
        return -1

    final_score = sum(scores.values()) / len(scores)
    return round(final_score, 2)

def print_json(obj):
    """
    Красиво печатает объект, который можно преобразовать в словарь.
    """
    if hasattr(obj, "__dict__"):
        data = obj.__dict__
    else:
        data = obj
    formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
    print(formatted_json)
