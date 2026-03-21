import json
from scientific_review.llm.client import LLMClient
from scientific_review.agents.state import ReviewState
from scientific_review.config.settings import MODELS


class FinalReviewerAgent:
    def __init__(self):
        self.client = LLMClient(
            model=MODELS["review"]["final"],
            temperature=0.3,
            max_tokens=3000
        )
        with open("scientific_review/prompts/agents/final_reviewer.txt", encoding="utf-8") as f:
            self.prompt_template = f.read()

    async def run(self, state: ReviewState) -> ReviewState:
        scores_str = json.dumps(state.scores, ensure_ascii=False, indent=2)

        input_review = (
            state.review_refined
            or state.review_draft
            or "No previous review draft was generated."
        )

        critic_content = state.review_critic or "{}"

        prompt = (
            self.prompt_template
            .replace("{{SCORES_JSON}}", scores_str)
            .replace("{{DRAFT_REVIEW}}", input_review)
            .replace("{{CRITIC_JSON}}", critic_content)
            .replace("{{TEXT}}", state.text[:10000])
        )

        response = await self.client.generate(prompt)

        state.review_final = response["text"].strip()

        state.agent_outputs.append({
            "agent": "final_reviewer",
            "raw": response["text"],
            "latency": response.get("latency", 0.0),
        })

        return state
