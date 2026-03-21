from pathlib import Path

from scientific_review.agents.state import ReviewState
from scientific_review.config.settings import MODELS
from scientific_review.llm.client import LLMClient
from scientific_review.utils.parser import extract_json


class ComplexityAgent:
    def __init__(self) -> None:
        self.client = LLMClient(model=MODELS["criteria"]["complexity"])
        self.prompt = Path("scientific_review/prompts/agents/complexity.txt").read_text(encoding="utf-8")

    def run(self, state: ReviewState) -> ReviewState:
        response = self.client.generate(self.prompt.replace("{{TEXT}}", state["text"]))
        data = extract_json(response["text"])

        state.setdefault("scores", {})["complexity"] = int(data["score"])
        state.setdefault("explanations", {})["complexity"] = data.get("explanation", "")
        state.setdefault("comments", {})["complexity"] = data.get("issues", [])
        state.setdefault("agents_outputs", []).append(
            {"agent": "complexity", "raw": response["text"], "parsed": data, "usage": response["usage"]}
        )
        return state

    def close(self):
        self.client.close()
