import json
from scientific_review.llm.client import LLMClient
from scientific_review.agents.state import ReviewState
from scientific_review.config.settings import MODELS


class EditorAgent:
    def __init__(self):
        self.client = LLMClient(
            model=MODELS["review"]["editor"],
            temperature=0.25,
            max_tokens=2000
        )
        with open("scientific_review/prompts/agents/editor.txt", encoding="utf-8") as f:
            self.prompt_template = f.read()

    async def run(self, state: ReviewState) -> ReviewState:
        if not state.review_draft:
            raise ValueError("Draft review required before EditorAgent")

        scores_str = json.dumps(state.scores, ensure_ascii=False, indent=2)
        critic_content = state.review_critic or "{}"

        prompt = (
            self.prompt_template
            .replace("{{DRAFT_REVIEW}}", state.review_draft)
            .replace("{{CRITIC_JSON}}", critic_content)
            .replace("{{SCORES_JSON}}", scores_str)
            .replace("{{TEXT}}", state.text[:8000])
        )

        response = await self.client.generate(prompt)

        state.review_refined = response["text"].strip()

        state.agent_outputs.append({
            "agent": "editor",
            "raw": response["text"],
            "latency": response.get("latency", 0.0),
        })

        return state
