# scripts/run_stability.py
# запуск оценки стабильности: дисперсия по нескольким прогонам одной статьи

import asyncio

from scientific_review.utils.utils import save_json
from scientific_review.evaluation.stability import evaluate_stability
from scientific_review.utils.logger import setup_logging, get_logger
from scientific_review.utils.utils import load_dataset
from scientific_review.utils.params import get_params

from scientific_review.client import Client
from scientific_review.baseline.baseline_pipeline import BaselinePipeline
from scientific_review.agents.multiagent_pipeline import MultiAgentPipeline

setup_logging()
logger = get_logger(__name__)
params = get_params()


async def run_stability(text: str):
    """
    Запускает оценку стабильности: дисперсия по нескольким прогонам одной статьи.

    Включает:
    - дисперсию по нескольким прогонам одной статьи

    Args:
        text: текст для оценки стабильности
    """
    async with Client() as baseline_client, \
                Client() as multiagent_client:

        baseline_pipeline = BaselinePipeline(baseline_client)
        multiagent_pipeline = MultiAgentPipeline(multiagent_client)
        logger.info("Пайплайны и клиенты инициализированы")

        stability_result = await evaluate_stability(
            text=text,
            baseline_pipeline=baseline_pipeline,
            multiagent_pipeline=multiagent_pipeline,
        )

    save_path = params["paths"]["stability_results"]
    save_json(stability_result, save_path)
    logger.info(f"Результаты оценки стабильности сохранены в {save_path}")


async def main():
    path = params["paths"]["dataset"] 

    texts, _ = load_dataset(path)
    text = texts[0]

    await run_stability(text=text)


if __name__ == "__main__":
    asyncio.run(main()) 
