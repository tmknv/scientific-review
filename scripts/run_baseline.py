# scripts/run_baseline.py
# быстрый запуск baseline pipeline

import asyncio

from scientific_review.baseline.baseline_pipeline import BaselinePipeline
from scientific_review.utils import print_json, save_json
from scientific_review.client import Client
from scientific_review.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def main():
    """
    Запускает baseline pipeline на одном тексте.

    Выполняет:
    1) один вызов LLM (baseline)
    2) вывод результата в консоль
    3) сохранение JSON артефакта в runs/baseline
    """
    
    # текст статьи
    text = """
    This paper proposes a novel machine learning approach for NLP tasks.
    """

    async with Client() as client:
        pipeline = BaselinePipeline(client=client)
        result = await pipeline.run(text)

    print_json(result)

    path = save_json(result, "runs/baseline")

    logger.info(f"Saved to: {path}")


if __name__ == "__main__":
    asyncio.run(main())
