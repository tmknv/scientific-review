from pathlib import Path

from scientific_review.agents.state import ReviewState
from scientific_review.config.settings import MODELS
from scientific_review.llm.client import LLMClient


class DraftReviewerAgent:
    def __init__(self) -> None:
        self.client = LLMClient(model=MODELS["review"]["draft"])
        self.prompt = Path("scientific_review/prompts/agents/draft_reviewer.txt").read_text(encoding="utf-8")

    def run(self, state: ReviewState) -> ReviewState:
        response = self.client.generate(self.prompt.replace("{{TEXT}}", state["text"]))
        state["review_draft"] = response["text"].strip()
        state.setdefault("agents_outputs", []).append(
            {"agent": "draft", "raw": response["text"], "usage": response["usage"]}
        )
        return state

    def close(self):
        self.client.close()
