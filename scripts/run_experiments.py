# scripts/run_experiments.py
# запуск экспериментов: baseline vs multi-agent + judge + stability

import asyncio
from typing import List, Optional

from scientific_review.client import Client
from scientific_review.utils.utils import save_json

from scientific_review.baseline.baseline_pipeline import BaselinePipeline
from scientific_review.agents.multiagent_pipeline import MultiAgentPipeline
from scientific_review.evaluation.judge_pipeline import JudgePipeline
from scientific_review.evaluation.evaluator import evaluate_dataset, evaluate_stability
from scientific_review.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def run_experiments(texts: List[str], human_scores: Optional[List[List[float]]] = None):
    """
    Запускает полный эксперимент.

    Включает:
    - baseline vs multi-agent
    - LLM-as-judge
    - stability test

    Args:
        texts: список текстов
        human_scores: human оценки (опционально)
    """

    async with Client() as baseline_client, \
               Client() as multiagent_client, \
               Client() as judge_client:

        baseline_pipeline = BaselinePipeline(baseline_client)
        multiagent_pipeline = MultiAgentPipeline(multiagent_client)
        judge_pipeline = JudgePipeline(judge_client)
        logger.info("Пайплайны и клиенты инициализированы")

        # dataset evaluation
        logger.info("Начало оценки на датасете")
        dataset_result = await evaluate_dataset(
            texts=texts,
            baseline_pipeline=baseline_pipeline,
            multiagent_pipeline=multiagent_pipeline,
            judge_pipeline=judge_pipeline,
            human_scores_list=human_scores,
        )
        logger.info("Оценка на датасете завершена")

        dataset_path = save_json(dataset_result, "runs/evaluation")
        logger.info(f"Сохранено в: {dataset_path}")

        # stability evaluation 
        # stability_result = await evaluate_stability(
        #     text=texts[0],
        #     baseline_pipeline=baseline_pipeline,
        #     multiagent_pipeline=multiagent_pipeline,
        # )

        # stability_path = save_json(stability_result, "runs/stability")
        # logger.info(f"Stability results saved to: {stability_path}")


async def main():
    texts = [
        "This paper proposes a novel machine learning method for NLP.",
        "We study optimization techniques for deep neural networks.",
    ]

    human_scores = None
    await run_experiments(texts=texts, human_scores=human_scores)


if __name__ == "__main__":
    asyncio.run(main())
