from scientific_review.llm.client import LLMClient 
from scientific_review.utils.parser import extract_json
from scientific_review.agents.state import ReviewState 


class ReadabilityAgent:
    def __init__(self) -> None:
        self.client = LLMClient()
        with open("scientific_review/prompts/agents/readability.txt") as f:
            self.prompt_template = f.read()

    async def run(self, state: ReviewState) -> ReviewState:
        prompt = self.prompt_template.replace("{{TEXT}}", state.text)
        response = await self.client.generate(prompt)
        
        parsed = extract_json(response["text"]) or {}

        state.scores["readability"] = parsed.get("score", 0)
        state.explanations["readability"] = parsed.get("explanation", "")
        state.comments["readability"] = parsed.get("issues", [])

        state.agent_outputs.append({
            "agent": "readability",
            "raw": response["text"],
            "parsed": parsed,
            "latency": response.get("latency", 0),
        })

        return state
