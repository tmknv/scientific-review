from typing import Any, TypedDict


class ReviewState(TypedDict, total=False):
    paper_id: str
    text: str
    mode: str

    scores: dict[str, float]
    explanations: dict[str, str]
    comments: dict[str, list[str]]

    review_draft: str
    review_critic: dict[str, Any]
    review_refined: str
    review_final: str
    review_consistency: dict[str, Any]

    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    bias_risks: list[str]

    agents_outputs: list[dict[str, Any]]
    final_result: dict[str, Any]
    raw_output: str | None
