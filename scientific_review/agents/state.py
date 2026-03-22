from typing import Any, TypedDict


class ReviewState(TypedDict, total=False):
    paper_id: str
    text: str
    mode: str

    scores: dict[str, float]
    reasons: dict[str, str]
    issues: dict[str, list[str]]

    review: str
    agents_outputs: list[dict[str, Any]]
    final_result: dict[str, Any]
