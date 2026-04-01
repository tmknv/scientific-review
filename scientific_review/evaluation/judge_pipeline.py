# scientific_review/evaluation/judge.py
# llm-as-judge: сравнение baseline и multi-agent ревью

from typing import Dict, Any

from scientific_review.client import Client
from scientific_review.utils import build_prompt, extract_json
from scientific_review.config import MODELS


class JudgePipeline:
    """
    LLM-as-Judge pipeline.

    Сравнивает два ревью:
    - baseline
    - multi-agent

    и выдает вердикт (winner) + баллы (score) + обоснование (reason)
    """

    def __init__(self, client: Client):
        """
        Args:
            client: LLM клиент
        """
        self.client = client


    async def evaluate(self, text: str, baseline_result: Dict[str, Any], multiagent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Сравнивает два результата и выбирает лучший.

        Args:
            text: Текст статьи
            baseline_result: Результат baseline
            multiagent_result: Результат multi-agent

        Returns:
            Вердикт и результат judge (winner, score_baseline, score_multiagent, reason, raw_output)
        """
        prompt = build_prompt(
            "judge", 
            text=text, 
            baseline_review=baseline_result.get("review", ""), 
            multiagent_review=multiagent_result.final_review
        )


        messages = [{"role": "user", "content": prompt}]

        response = await self.client.generate(messages, model=MODELS["judge"])

        data = extract_json(response)

        return {
            "winner": data.get("winner", "unknown"),
            "score_baseline": data.get("score_baseline", -1),
            "score_multiagent": data.get("score_multiagent", -1),
            "reason": data.get("reason", response),
            "raw_output": response,
        }
