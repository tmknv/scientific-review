import json
from pathlib import Path

from scientific_review.agents.state import ReviewState
from scientific_review.config.settings import MODELS
from scientific_review.llm.client import LLMClient
from scientific_review.utils.parser import extract_json


class CriticAgent:
    def __init__(self) -> None:
        self.client = LLMClient(model=MODELS["review"]["critic"])
        self.prompt = Path("scientific_review/prompts/agents/critic.txt").read_text(encoding="utf-8")

    def run(self, state: ReviewState) -> ReviewState:
        prompt = (
            self.prompt
            .replace("{{DRAFT_REVIEW}}", state.get("review_draft", ""))
            .replace("{{SCORES_JSON}}", json.dumps(state.get("scores", {}), ensure_ascii=False))
            .replace("{{TEXT}}", state["text"])
        )
        response = self.client.generate(prompt)
        data = extract_json(response["text"])

        state["review_critic"] = data
        state.setdefault("agents_outputs", []).append(
            {"agent": "critic", "raw": response["text"], "parsed": data, "usage": response["usage"]}
        )
        return state

    def close(self):
        self.client.close()
