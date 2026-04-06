# scientific_review/evaluation/ablation.py
# ablation study (убираем агентов и смотрим деградацию)

from typing import List, Dict, Any

from scientific_review.evaluation.quality import evaluate_dataset
from scientific_review.utils.logger import setup_logging, get_logger
from scientific_review.utils.params import get_params

from scientific_review.baseline.baseline_pipeline import BaselinePipeline
from scientific_review.agents.multiagent_pipeline import MultiAgentPipeline
from scientific_review.evaluation.judge_pipeline import JudgePipeline
from scientific_review.client import Client

setup_logging()
logger = get_logger(__name__)
params = get_params()


def get_ablation_configs() -> Dict[str, List[str]]:
    """
    Генерирует конфигурации для ablation.

    Returns:
        Словарь: configuration_name -> список активных агентов

    Example:
        {        
            "full": ["novelty", "scientificity", "readability", "complexity"],
            "no_novelty": ["scientificity", "readability", "complexity"],
            "no_scientificity": ["novelty", "readability", "complexity"],
            "no_readability": ["novelty", "scientificity", "complexity"],
            "no_complexity": ["novelty", "scientificity", "readability"],
        }
    """
    full = params["criteria"]["order"]

    configs = {
        "full": full,
    }

    for agent in full:
        configs[f"no_{agent}"] = [a for a in full if a != agent]

    return configs


async def evaluate_ablation(texts: List[str], human_scores: List[List[float]], concurrency: int = 5) -> Dict[str, Any]:
    """
    Запускает ablation study: убираем агентов и смотрим деградацию.

    Сравнивает каждый вариант с human_scores.

    Args:
        texts: Тексты статей
        human_scores: Список human-оценок
        concurrency: Ограничение параллелизма для semaphore

    Returns:
        Словарь: configuration_name -> результат evaluate_dataset для каждой конфигурации
    """
    logger.info("Запуск ablation study...")

    configs = get_ablation_configs()
    results = {}

    async with Client() as multiagent_client:

        for name, enabled_agents in configs.items():
            logger.info(f"Ablation configuration: {name} ({enabled_agents})")

            multiagent_pipeline = MultiAgentPipeline(
                multiagent_client,
                enabled_agents=enabled_agents
            )

            dataset_result = await evaluate_dataset(
                texts=texts,
                multiagent_pipeline=multiagent_pipeline,
                human_scores_list=human_scores,
                concurrency=concurrency,
            )

            results[name] = dataset_result

    logger.info("Ablation study завершен.")
    return results
