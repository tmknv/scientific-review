from pydantic import BaseModel, Field

class ReviewState(BaseModel):
    text: str

    scores: dict[str, float] = Field(default_factory=dict)
    explanations: dict[str, str] = Field(default_factory=dict)
    comments: dict[str, list[str]] = Field(default_factory=dict)

    review_draft: str | None = None
    review_critic: str | None = None
    review_refined: str | None = None
    review_final: str | None = None

    agent_outputs: list[dict[str, any]] = Field(default_factory=list)