from pathlib import Path

from scientific_review.llm.client import LLMClient
from scientific_review.utils.parser import extract_json


class ReadabilityAgent:
    def __init__(self):
        self.client = LLMClient(temperature=0.2, max_tokens=700)
        self.prompt = Path("scientific_review/prompts/agents/readability.txt").read_text(encoding="utf-8")

    def run(self, state):
        prompt = self.prompt.replace("{{TEXT}}", state["text"])
        response = self.client.generate(prompt)
        data = extract_json(response["text"])

        state.setdefault("scores", {})["readability"] = int(data["score"])
        state.setdefault("reasons", {})["readability"] = data.get("reasoning", "")
        state.setdefault("issues", {})["readability"] = data.get("issues", [])
        state.setdefault("agents_outputs", []).append(
            {"agent": "readability", "raw": response["text"], "parsed": data}
        )
        return state

    def close(self):
        self.client.close()
