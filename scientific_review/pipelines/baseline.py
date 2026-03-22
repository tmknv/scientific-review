import time
from pathlib import Path

from scientific_review.llm.client import LLMClient
from scientific_review.utils.parser import extract_json


class BaselinePipeline:
    def __init__(self):
        self.client = LLMClient()
        self.prompt = Path("scientific_review/prompts/baseline.txt").read_text(encoding="utf-8")

    def run(self, text, paper_id="unknown"):
        prompt = self.prompt.replace("{{TEXT}}", text)
        response = self.client.generate(prompt)
        data = extract_json(response["text"])

        scores = data.get("scores", {})
        if "final_score" not in scores:
            scores["final_score"] = round(
                (scores.get("novelty", 0) +
                 scores.get("scientificity", 0) +
                 scores.get("complexity", 0) +
                 scores.get("readability", 0)) / 4,
                2,
            )

        return {
            "paper_id": paper_id,
            "mode": "baseline",
            "scores": scores,
            "review": data.get("review", ""),
            "agents_outputs": [
                {
                    "agent": "baseline",
                    "raw": response["text"],
                    "parsed": data,
                }
            ],
        }

    def close(self):
        self.client.close()
