# scripts/run_quality.py
# запуск оценки качества: baseline vs multi-agent (human labels + judge)

import asyncio
from typing import List, Optional

from scientific_review.utils.utils import save_json
from scientific_review.evaluation.quality import evaluate_dataset
from scientific_review.utils.logger import setup_logging, get_logger
from scientific_review.utils.utils import load_dataset
from scientific_review.utils.params import get_params

from scientific_review.client import Client
from scientific_review.baseline.baseline_pipeline import BaselinePipeline
from scientific_review.agents.multiagent_pipeline import MultiAgentPipeline
from scientific_review.evaluation.judge_pipeline import JudgePipeline

setup_logging()
logger = get_logger(__name__)
params = get_params()


async def run_quality(texts: List[str], human_scores: Optional[List[List[float]]] = None):
    """
    Запускает оценку качества: baseline vs multi-agent (human labels + judge).

    Включает:
    - baseline vs multi-agent (human labels)
    - LLM-as-judge

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
            multiagent_pipeline=multiagent_pipeline,
            baseline_pipeline=baseline_pipeline,
            judge_pipeline=judge_pipeline,
            human_scores_list=human_scores,
        )
        logger.info("Оценка на датасете завершена")

        save_path = params["paths"]["quality_results"]
        save_json(dataset_result, save_path)
        logger.info(f"Результаты оценки качества сохранены в {save_path}")    


async def main():
    path = params["paths"]["dataset"] 

    texts, human_scores = load_dataset(path)
    texts = texts[:10]  # для теста берем 10 текстов
    human_scores = human_scores[:10] if human_scores else None
    logger.info(f"Загружено текстов: {len(texts)}")

    await run_quality(texts=texts, human_scores=human_scores)


if __name__ == "__main__":
    asyncio.run(main())
