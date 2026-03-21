from scientific_review.llm.client import LLMClient
from scientific_review.utils.parser import extract_json


class ComplexityAgent:
    def __init__(self):
        self.client = LLMClient()
        with open("scientific_review/prompts/agents/complexity.txt") as f:
            self.prompt_template = f.read()

    async def run(self, state):
        prompt = self.prompt_template.replace("{{TEXT}}", state.text)
        response = await self.client.generate(prompt)
        parsed = extract_json(response["text"])

        state.scores["novelty"] = parsed.get("score", 0)
        state.explanations["novelty"] = parsed.get("explanation", "")
        state.comments["novelty"] = parsed.get("issues", [])

        state.agent_outputs.append({
            "agent": "novelty",
            "raw": response["text"],
            "parsed": parsed,
            "latency": response["latency"],
        })

        return state