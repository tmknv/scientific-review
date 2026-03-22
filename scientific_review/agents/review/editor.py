import json
from pathlib import Path

from scientific_review.agents.state import ReviewState
from scientific_review.config.settings import MODELS
from scientific_review.llm.client import LLMClient


class EditorAgent:
    def __init__(self) -> None:
        self.client = LLMClient(model=MODELS["review"]["editor"])
        self.prompt = Path("scientific_review/prompts/agents/editor.txt").read_text(encoding="utf-8")

    def run(self, state: ReviewState) -> ReviewState:
        prompt = (
            self.prompt
            .replace("{{DRAFT_REVIEW}}", state.get("review_draft", ""))
            .replace("{{CRITIC_JSON}}", json.dumps(state.get("review_critic", {}), ensure_ascii=False))
            .replace("{{TEXT}}", state["text"])
        )
        response = self.client.generate(prompt)
        state["review_refined"] = response["text"].strip()
        state.setdefault("agents_outputs", []).append(
            {"agent": "editor", "raw": response["text"], "usage": response["usage"]}
        )
        return state

    def close(self):
        self.client.close()
