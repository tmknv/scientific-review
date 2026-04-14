# scripts/run_ablation.py
# запуск ablation study: drop-one-agent vs human

import asyncio
from typing import List, Optional

from scientific_review.utils.utils import save_json, load_dataset
from scientific_review.evaluation.ablation import evaluate_ablation, build_ablation_summary, format_ablation_table
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

    summary = build_ablation_summary(results)

    final_output = {
        "results": results,
        "summary": summary,
    }

    save_path = params["paths"]["ablation_results"]
    save_json(final_output, save_path)
    logger.info(f"Ablation study завершен, результаты сохранены в {save_path}")

    table = format_ablation_table(summary)
    print("\n" + table + "\n")
    logger.info("\n" + table)


async def main():
    path = params["paths"]["dataset"]

    logger.info(f"Загрузка датасета из {path}")
    texts, human_scores = load_dataset(path)

    # для теста берем 10 текстов
    texts = texts[:5]  
    human_scores = human_scores[:5] if human_scores else None
    
    logger.info(f"Загружено текстов: {len(texts)}")

    await run_ablation(texts=texts, human_scores=human_scores)


if __name__ == "__main__":
    asyncio.run(main())
