from pydantic import BaseModel, Field
from typing import Any, Dict, List

class ReviewState(BaseModel):
    text: str

    scores: Dict[str, float] = Field(default_factory=dict)
    explanations: Dict[str, str] = Field(default_factory=dict)
    comments: Dict[str, List[str]] = Field(default_factory=dict)

    review_draft: str | None = None
    review_critic: Dict[str, Any] | None = None
    review_refined: str | None = None
    review_final: str | None = None

    agent_outputs: List[Dict[str, Any]] = Field(default_factory=list)
