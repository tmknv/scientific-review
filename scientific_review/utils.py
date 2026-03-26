# утилиты: парсинг json, работа с файлами, вспомогательные функции

import yaml
import json
import re
import os
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

def message_to_dict(msg: BaseMessage) -> dict:
    """Преобразует LLM-сообщение в словарь для JSON."""
    return {
        "type": msg.type,       # 'human', 'ai', 'system' и т.д.
        "content": msg.content,
    }

def extract_json(text):
    """
    пытается вытащить json из ответа llm
    """

    try:
        return json.loads(text)
    except Exception as e:
        print(f"Error occurred while parsing JSON: {e}")

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception as e:
            print(f"Error occurred while parsing JSON from regex match: {e}")

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

def print_json(state):
    """Безопасный вывод State в формате JSON."""
    data = state_to_dict(state)
    formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
    print(formatted_json)

def load_prompts():
    with open("scientific_review/prompts.yaml", "r") as f:
        PROMPTS = yaml.safe_load(f)
    return PROMPTS

def state_to_dict(state) -> dict:
    """Преобразует объект State в словарь, сериализуемый в JSON."""
    data = state.__dict__.copy()

    # Сериализуем сообщения
    data["messages"] = [message_to_dict(msg) for msg in state.messages]

    # Можно добавить обработку других нестандартных полей, если потребуется
    return data