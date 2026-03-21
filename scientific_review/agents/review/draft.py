from scientific_review.llm.client import LLMClient
from scientific_review.agents.state import ReviewState
from scientific_review.config.settings import MODELS


class DraftReviewerAgent:
    def __init__(self):
        self.client = LLMClient(
            model=MODELS["review"]["draft"],
            temperature=0.45,
            max_tokens=2200
        )
        with open("scientific_review/prompts/agents/draft_reviewer.txt", encoding="utf-8") as f:
            self.prompt_template = f.read()

    async def run(self, state: ReviewState) -> ReviewState:
        prompt = self.prompt_template.replace("{{TEXT}}", state.text)

        response = await self.client.generate(prompt)

        state.review_draft = response["text"].strip()

        state.agent_outputs.append({
            "agent": "draft_reviewer",
            "raw": response["text"],
            "latency": response.get("latency", 0.0),
        })

        return state
