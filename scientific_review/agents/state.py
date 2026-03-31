# scientific_review/agents/state.py
# общий short-term memory state мультиагентной системы

from dataclasses import dataclass, field
from typing import Annotated, Dict, List, Any
import operator

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


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

        novelty_agent: Внутреннее состояние агента новизны
        scientificity_agent: Внутреннее состояние агента научности
        readability_agent: Внутреннее состояние агента читаемости
        complexity_agent: Внутреннее состояние агента сложности

        review_agent: Состояние агента чернового ревью
        final_review_agent: Состояние финального агента

        draft_review: Черновой текст рецензии
        final_review: Финальный текст рецензии
        verdict: Итоговое решение (accept / revise / reject)

        agents_outputs: Лог всех действий агентов
            Используется для анализа, дебага и сохранения артефактов
            Пример: [{"agent": "novelty", "raw_output": "...", "parsed_score": 5, "reason": "..."}]

        metadata: Служебная информация:
            - время работы агентов
            - ошибки
            - дополнительная диагностика
    """

    # вход
    text: Annotated[list[str], operator.add]
 
    # short-term memory
    messages: Annotated[List[BaseMessage], add_messages] = field(default_factory=list)

    # структурированная память
    scores: Annotated[Dict[str, float], merge_dicts] = field(default_factory=dict)
    reasons: Annotated[Dict[str, str], merge_dicts] = field(default_factory=dict)

    # память отдельных агентов
    novelty_agent: Dict[str, Any] = field(default_factory=dict)
    scientificity_agent: Dict[str, Any] = field(default_factory=dict)
    readability_agent: Dict[str, Any] = field(default_factory=dict)
    complexity_agent: Dict[str, Any] = field(default_factory=dict)

    raw_review_agent: Dict[str, Any] = field(default_factory=dict)
    final_review_agent: Dict[str, Any] = field(default_factory=dict)

    # текстовые результаты
    draft_review: str = ""
    final_review: str = ""
    verdict: str = ""

    # лог системы
    agents_outputs: Annotated[List[Dict[str, Any]], operator.add] = field(default_factory=list)

    # служебные данные
    metadata: Annotated[Dict[str, Any], merge_dicts] = field(default_factory=dict)
