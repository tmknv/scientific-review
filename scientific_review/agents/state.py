# scientific_review/agents/state.py
# общий state (short-term memory), через который взаимодействуют все агенты

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class State:
    """
    общая память мультиагентной системы

    агенты читают и записывают данные в этот объект,
    используя как свою ячейку, так и общие поля

    Attributes:
        text: текст статьи

        novelty_agent: память агента новизны
        scientificity_agent: память агента научности
        readability_agent: память агента читаемости
        complexity_agent: память агента сложности

        review_agent: память агента чернового ревью
        final_agent: память финального агента

        agents_group: общая память между агентами

        scores: итоговые оценки по критериям
        reasons: объяснения оценок

        draft_review: черновик ревью
        final_review: финальный текст ревью

        verdict: итоговое решение

        agents_outputs: лог работы агентов
        metadata: служебные данные (время, ошибки и тд)
    """

    # вход
    text: str = ""

    # память агентов (criteria)
    novelty_agent: Dict[str, Any] = field(default_factory=dict)
    scientificity_agent: Dict[str, Any] = field(default_factory=dict)
    readability_agent: Dict[str, Any] = field(default_factory=dict)
    complexity_agent: Dict[str, Any] = field(default_factory=dict)

    # память агентов (review)
    review_agent: Dict[str, Any] = field(default_factory=dict)
    final_agent: Dict[str, Any] = field(default_factory=dict)

    # общая память
    agents_group: Dict[str, Any] = field(default_factory=dict)

    # агрегированные данные
    scores: Dict[str, float] = field(default_factory=dict)
    reasons: Dict[str, str] = field(default_factory=dict)

    # ревью
    draft_review: str = ""
    final_review: str = ""

    # итоговое решение
    verdict: str = ""

    # лог
    agents_outputs: List[Dict[str, Any]] = field(default_factory=list)

    # служебка (метаданные, время и тд)
    metadata: Dict[str, Any] = field(default_factory=dict)
