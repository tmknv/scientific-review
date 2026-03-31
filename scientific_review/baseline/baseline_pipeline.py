# scientific_review/baseline/baseline_pipeline.py
# baseline pipeline: один вызов llm для оценки и ревью

from typing import Dict, Any

from scientific_review.client import Client
from scientific_review.utils import build_prompt, extract_json
from scientific_review.config import MODELS


class BaselinePipeline:
    """
    Baseline pipeline.

    Один вызов LLM:
    - генерирует оценки
    - генерирует review
    """

    def __init__(self, client: Client):
        """
        Args:
            client: LLM клиент
        """
        self.client = client


    async def run(self, text: str) -> Dict[str, Any]:
        """
        Запускает baseline модель.

        Args:
            text: Текст статьи

        Returns:
            Результат baseline (scores, verdict, review, raw_output)
        """
        prompt = build_prompt("baseline", text=text)
        messages = [{"role": "user", "content": prompt}]

        response = await self.client.generate(messages=messages, model=MODELS["baseline"])

        data = extract_json(response)

        scores = data.get("scores", {})

        return {
            "scores": {
                "novelty": scores.get("novelty", -1),
                "scientificity": scores.get("scientificity", -1),
                "readability": scores.get("readability", -1),
                "complexity": scores.get("complexity", -1),
                "final_score": data.get("final_score", -1),
            },
            "verdict": data.get("verdict", "unknown"),
            "review": data.get("review", response),
            "raw_output": response,
        }
