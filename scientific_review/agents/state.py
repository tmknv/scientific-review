# scientific_review/agents/state.py
# общий short-term memory state мультиагентной системы

from dataclasses import dataclass, field
from typing import Annotated, Dict, List, Any
import operator

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


def last_value(old: Any, new: Any) -> Any:
    return new


def merge_dicts(old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """
    Объединяет два словаря

    Args:
        old: Старое состояние
        new: Новые данные

    Returns:
        Dict[str, Any]: Объединенный словарь
    """
    return {**old, **new}


@dataclass
class State:
    """
    Short-term memory мультиагентной системы рецензирования.

    State используется как единая разделяемая память между агентами.
    Каждый агент читает и модифицирует state, тем самым формируя
    накопленное представление о статье и процессе её анализа.

    Attributes:
        text: Текст научной статьи

        messages: История сообщений (контекст LLM)
            Используется для передачи промежуточных рассуждений между агентами.

        scores: Словарь оценок по критериям
            Пример: {"novelty": 7.0, "readability": 5.0}

        reasons: Объяснения оценок по каждому критерию
            Пример: {"novelty": "...", "readability": "..."}

        draft_review: Черновой текст рецензии
        final_review: Финальный текст рецензии
        verdict: Итоговое решение (accept / revise / reject)

        agents_outputs: Лог всех действий агентов
            Используется для анализа, дебага и сохранения артефактов
            Пример: {"novelty": {"score": 5, "reason": "..."}, "scientificity": {...}}

        metadata: Служебная информация:
            - время работы агентов
            - ошибки
            - дополнительная диагностика
    """
    # вход
    text: Annotated[str, last_value] = ""
 
    # short-term memory
    messages: Annotated[List[BaseMessage], add_messages] = field(default_factory=list)

    # структурированная память
    scores: Annotated[Dict[str, float], merge_dicts] = field(default_factory=dict)
    reasons: Annotated[Dict[str, str], merge_dicts] = field(default_factory=dict)

    # текстовые результаты
    draft_review: Annotated[str, operator.add] = ""
    final_review: Annotated[str, operator.add] = ""
    verdict: Annotated[str, operator.add] = ""

    # лог системы
    agents_outputs: Annotated[Dict[str, Dict[str, Any]], merge_dicts] = field(default_factory=dict)

    # служебные данные
    metadata: Annotated[Dict[str, Any], merge_dicts] = field(default_factory=dict)
