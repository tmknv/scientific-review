import json
from scientific_review.llm.client import LLMClient
from scientific_review.utils.parser import extract_json
from scientific_review.agents.state import ReviewState
from scientific_review.config.settings import MODELS


class ConsistencyCheckerAgent:
    def __init__(self):
        self.client = LLMClient(
            model=MODELS["review"]["сonsistency"],
            temperature=0.15,
            max_tokens=1200
        )
        with open("scientific_review/prompts/agents/consistency.txt", encoding="utf-8") as f:
            self.prompt_template = f.read()

    async def run(self, state: ReviewState) -> ReviewState:
        if not state.review_final:
            raise ValueError("Final review must exist before ConsistencyChecker")

        scores_str = json.dumps(state.scores, ensure_ascii=False, indent=2)

        prompt = (
            self.prompt_template
            .replace("{{SCORES_JSON}}", scores_str)
            .replace("{{FINAL_REVIEW}}", state.review_final)
        )

        response = await self.client.generate(prompt)
        parsed = extract_json(response["text"])

        if not isinstance(parsed, dict):
            parsed = {
                "is_consistent": False,
                "score_review_mismatches": [],
                "severity": "high",
                "explanation": "Failed to parse consistency check"
            }

        state.agent_outputs.append({
            "agent": "consistency_checker",
            "raw": response["text"],
            "parsed": parsed,
            "latency": response.get("latency", 0.0),
        })

        return state
