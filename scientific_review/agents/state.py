# общий state, через который взаимодействуют все агенты
# все агенты читают и записывают данные в один этот объект

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class State:
    # вход
    text: str

    # оценки
    scores: Dict[str, float] = field(default_factory=dict)

    # тексты ревью
    draft_review: str = "" # черновик
    final_review: str = "" # чистовик

    # итог
    verdict: str = ""

    # лог всех агентов
    agents_outputs: List[Dict[str, Any]] = field(default_factory=list)

    # служебка (метаданные, время и тд)
    metadata: Dict[str, Any] = field(default_factory=dict)
