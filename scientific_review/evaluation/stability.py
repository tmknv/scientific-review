# scientific_review/evaluation/stability.py
# оценка стабильности: дисперсия по нескольким прогонам одной статьи

import asyncio
from typing import Dict, Any

from scientific_review.utils.utils import extract_scores
from scientific_review.evaluation.metrics import inter_run_variance
from scientific_review.utils.logger import setup_logging, get_logger
from scientific_review.utils.params import get_params

from scientific_review.baseline.baseline_pipeline import BaselinePipeline
from scientific_review.agents.multiagent_pipeline import MultiAgentPipeline

setup_logging() 
logger = get_logger(__name__)
params = get_params()


async def evaluate_stability(
    text: str, 
    baseline_pipeline: BaselinePipeline, 
    multiagent_pipeline: MultiAgentPipeline, 
    runs: int = 5, 
    concurrency: int = params["evaluation"]["concurrency"]
) -> Dict[str, Any]:
    """
    Stability test
    Считает дисперсию по нескольким прогонам одной статьи.

    baseline run1, run2, run3... -> baseline_var  
    multiagent run1, run2, run3... -> multiagent_var

    Args:
        text: Текст статьи
        baseline_pipeline: Пайплайн для baseline
        multiagent_pipeline: Пайплайн для multi-agent
        runs: Количество прогонов
        concurrency: Ограничение параллелизма для semaphore

    Returns:
        Variance для baseline и multi-agent
    """
    logger.info(f"Запуск теста стабильности (runs={runs}, concurrency={concurrency})...")

    # concurrency не может быть больше количества прогонов
    concurrency = min(concurrency, runs) 
    semaphore = asyncio.Semaphore(concurrency)

    async def sem_run_baseline():
        async with semaphore:
            return await baseline_pipeline.run(text)

    async def sem_run_multiagent():
        async with semaphore:
            return await multiagent_pipeline.run(text)

    baseline_tasks = [asyncio.create_task(sem_run_baseline()) for _ in range(runs)]
    multiagent_tasks = [asyncio.create_task(sem_run_multiagent()) for _ in range(runs)]

    baseline_results = await asyncio.gather(*baseline_tasks)
    multiagent_results = await asyncio.gather(*multiagent_tasks)

    baseline_runs = [extract_scores(result) for result in baseline_results]
    multiagent_runs = [extract_scores(result) for result in multiagent_results]

    baseline_var = inter_run_variance(baseline_runs)
    multiagent_var = inter_run_variance(multiagent_runs)

    logger.info(f"Оценка стабильности завершена.")

    return {
        "baseline": {
            "runs": baseline_runs,
            "variance": baseline_var,
        },
        "multiagent": {
            "runs": multiagent_runs,
            "variance": multiagent_var,
        },
    }
