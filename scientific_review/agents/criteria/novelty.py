from scientific_review.llm.client import LLMClient  
from scientific_review.utils.parser import extract_json
from scientific_review.agents.state import ReviewState  


class NoveltyAgent:
    def __init__(self) -> None:
        self.client = LLMClient()
        with open("scientific_review/prompts/agents/novelty.txt") as f:
            self.prompt_template = f.read()

    async def run(self, state: ReviewState) -> ReviewState:
        prompt = self.prompt_template.replace("{{TEXT}}", state.text)
        response = await self.client.generate(prompt)
        
        parsed = extract_json(response["text"]) or {}

        state.scores["novelty"] = parsed.get("score", 0)
        state.explanations["novelty"] = parsed.get("explanation", "")
        state.comments["novelty"] = parsed.get("issues", [])

        state.agent_outputs.append({
            "agent": "novelty",
            "raw": response["text"],
            "parsed": parsed,
            "latency": response.get("latency", 0),
        })

        return state
