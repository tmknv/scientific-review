# scripts/run_multiagent.py
# быстрый запуск multi-agent pipeline

import asyncio
from scientific_review.agents.multiagent_pipeline import MultiAgentPipeline
from scientific_review.utils import print_json, save_json
from scientific_review.client import Client
from scientific_review.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def main():
    """
    Запускает multi-agent pipeline на одном тексте.

    Выполняет:
    1) прогон мультиагентной системы
    2) вывод результата в консоль
    3) сохранение JSON артефакта в runs/multiagent
    """

    # текст статьи
    text = """
    This paper proposes a novel machine learning approach for NLP tasks.
    """
    async with Client() as client:
        logger.info("Клиент инициализирован")
        pipeline = MultiAgentPipeline(client=client)
        state = await pipeline.run(text)

    result = {
        "scores": state.scores,
        "review": state.final_review,
        "verdict": state.verdict,
        "agents_outputs": state.agents_outputs
    }

    print_json(state)

    path = save_json(result, "runs/multiagent")

    logger.info(f"Saved to: {path}")


if __name__ == "__main__":
    asyncio.run(main())
