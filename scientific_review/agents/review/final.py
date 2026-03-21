import json
from pathlib import Path

from scientific_review.agents.state import ReviewState
from scientific_review.config.settings import MODELS
from scientific_review.llm.client import LLMClient
from scientific_review.utils.parser import extract_json


class FinalReviewerAgent:
    def __init__(self) -> None:
        self.client = LLMClient(model=MODELS["review"]["final"])
        self.prompt = Path("scientific_review/prompts/agents/final_reviewer.txt").read_text(encoding="utf-8")

    def run(self, state: ReviewState) -> ReviewState:
        prompt = (
            self.prompt
            .replace("{{SCORES_JSON}}", json.dumps(state.get("scores", {}), ensure_ascii=False))
            .replace("{{DRAFT_REVIEW}}", state.get("review_draft", ""))
            .replace("{{REFINED_REVIEW}}", state.get("review_refined", ""))
            .replace("{{CRITIC_JSON}}", json.dumps(state.get("review_critic", {}), ensure_ascii=False))
            .replace("{{TEXT}}", state["text"])
        )
        response = self.client.generate(prompt)
        data = extract_json(response["text"])

        state["review_final"] = data.get("review", response["text"])
        state["strengths"] = data.get("strengths", [])
        state["weaknesses"] = data.get("weaknesses", [])
        state["suggestions"] = data.get("suggestions", [])
        state["bias_risks"] = data.get("bias_risks", [])
        state.setdefault("agents_outputs", []).append(
            {"agent": "final", "raw": response["text"], "parsed": data, "usage": response["usage"]}
        )
        return state

    def close(self):
        self.client.close()
