# scientific_review/baseline/baseline_pipeline.py
# baseline pipeline: один вызов llm для оценки и ревью

from typing import Dict, Any

from scientific_review.client import Client
from scientific_review.utils.utils import extract_json
from scientific_review.utils.params import get_params
from scientific_review.utils.prompts import get_prompt_parts
from scientific_review.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)
params = get_params()


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
        system_prompt, user_prompt = get_prompt_parts(name='baseline', text=text)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        logger.info("BaselinePipeline: отправка запроса")
        response = await self.client.generate(messages=messages, model=params["models"]["baseline"])
        logger.info("BaselinePipeline: получен ответ")

        data = extract_json(response)

        scores = data.get("scores", {})
        order = params["criteria"]["order"]

        ordered_scores = {key: scores.get(key, -1) for key in order}
        ordered_scores["final_score"] = data.get("final_score", -1)

        return {
            "scores": ordered_scores,
            "verdict": data.get("verdict", "unknown"),
            "review": data.get("review", response),
            "raw_output": response,
        }
