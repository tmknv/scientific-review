# scientific_review/evaluation/judge.py
# llm-as-judge: сравнение baseline и multi-agent ревью

from typing import Dict, Any, List

from scientific_review.client import Client
from scientific_review.utils.utils import extract_json
from scientific_review.utils.params import get_params
from scientific_review.utils.prompts import get_prompt_parts
from scientific_review.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)
params = get_params()


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


    async def evaluate(self, text: str,
                        baseline_result: Dict[str, Any],
                        multiagent_result: Dict[str, Any],
                        baseline_scores: List[float],
                        human_scores: List[float]) -> Dict[str, Any]:
        """
        Сравнивает два результата и выбирает лучший.

        Args:
            text: Текст статьи
            baseline_result: Результат baseline
            multiagent_result: Результат multi-agent

        Returns:
            Вердикт и результат judge (winner, score_baseline, score_multiagent, reason, raw_output)
        """
        system_prompt, user_prompt = get_prompt_parts(
            "judge", 
            text=text, 
            baseline_review=baseline_result.get("review", ""),
            biseline_score=baseline_scores, 
            multiagent_review=multiagent_result.final_review,
            multiagent_score=multiagent_result.scores,
            human_scores=human_scores,
        )

        messages = [
            {"role": "system", "content": system_prompt}, 
            {"role": "user", "content": user_prompt}
        ]
        
        logger.info("JudgePipeline: отправка запроса")
        response = await self.client.generate(messages, model=params["models"]["judge"])
        logger.info("JudgePipeline: получен ответ")

        data = extract_json(response)

        return {
            "winner": data.get("winner", "unknown"),
            "score_baseline": data.get("score_baseline", -1),
            "score_multiagent": data.get("score_multiagent", -1),
            "reason": data.get("reason", response),
            "raw_output": response,
        }
