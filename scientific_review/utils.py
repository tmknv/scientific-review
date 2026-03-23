# утилиты: парсинг json, работа с файлами, вспомогательные функции

import json
import re


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
