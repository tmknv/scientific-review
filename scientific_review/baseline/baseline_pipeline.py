# baseline pipeline: один вызов llm для генерации оценки и ревью

from scientific_review.client import Client
from scientific_review.config import PROMPTS
from scientific_review.utils import extract_json


class BaselinePipeline:
    def __init__(self):
        self.client = Client()

    def run(self, text):
        prompt = PROMPTS["baseline"].format(text=text)

        response = self.client.generate(prompt)
        data = extract_json(response)

        scores = data.get("scores", {})

        result = {
            "scores": {
                "novelty": scores.get("novelty", -1),
                "scientificity": scores.get("scientificity", -1),
                "readability": scores.get("readability", -1),
                "complexity": scores.get("complexity", -1),
                "final_score": data.get("final_score", -1),
            },
            "verdict": data.get("verdict", "no verdict"),
            "review": data.get("review", response),
            "raw_output": response
        }

        return result
