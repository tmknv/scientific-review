# scripts/run_ablation.py
# запуск ablation study: drop-one-agent vs human

import asyncio
from typing import List, Optional

from scientific_review.utils.utils import save_json, load_dataset
from scientific_review.evaluation.ablation import evaluate_ablation
from scientific_review.utils.logger import setup_logging, get_logger
from scientific_review.utils.params import get_params

setup_logging()
logger = get_logger(__name__)
params = get_params()


async def run_ablation(texts: List[str], human_scores: Optional[List[List[float]]] = None):
    """
    Запускает ablation study: убираем агентов и смотрим деградацию.

    Сравнивает каждый вариант multi-agent с human_scores.

    Args:
        texts: список текстов
        human_scores: human оценки (опционально)
    """
    logger.info("Начало ablation study")

    results = await evaluate_ablation(
        texts=texts,
        human_scores=human_scores,
    )

    save_path = params["paths"]["ablation_results"]
    save_json(results, save_path)
    logger.info(f"Ablation study завершен, результаты сохранены в {save_path}")


async def main():
    path = params["paths"]["dataset"]

    texts, human_scores = load_dataset(path)

    # для теста берем 10 статей
    texts = texts[:10]
    human_scores = human_scores[:10] if human_scores is not None else None

    logger.info(f"Загружено текстов: {len(texts)}")

    await run_ablation(texts=texts, human_scores=human_scores)


if __name__ == "__main__":
    asyncio.run(main())
