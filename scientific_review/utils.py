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

    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return path
