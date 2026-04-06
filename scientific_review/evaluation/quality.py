# scientific_review/evaluation/quality.py
# оценка качества: baseline vs multi-agent (human labels + judge)

import asyncio
from typing import List, Dict, Any, Optional

from scientific_review.utils.utils import extract_scores
from scientific_review.evaluation.metrics import spearman_correlation
from scientific_review.utils.logger import setup_logging, get_logger

from scientific_review.baseline.baseline_pipeline import BaselinePipeline
from scientific_review.agents.multiagent_pipeline import MultiAgentPipeline
from scientific_review.evaluation.judge_pipeline import JudgePipeline

setup_logging()
logger = get_logger(__name__)


# прогон одного текста
async def evaluate_single(
    text: str,
    baseline_pipeline: BaselinePipeline,
    multiagent_pipeline: MultiAgentPipeline,
    judge_pipeline: Optional[JudgePipeline] = None,
    human_scores: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    Оценка ОДНОГО текста. 

    Считает:
    - baseline_scores vs human_scores
    - multiagent_scores vs human_scores

    Args:
        text: Текст статьи
        baseline_pipeline: Пайплайн для baseline
        multiagent_pipeline: Пайплайн для multi-agent
        judge_pipeline: Пайплайн для judge (опционально)
        human_scores: Human-оценки (опционально)

    Returns:
        Полный результат (baseline, multiagent, metrics, judge)
    """
    try:
        logger.debug("Запускаем пайплайны baseline и multiagent...")
        baseline_task = asyncio.create_task(baseline_pipeline.run(text))
        multiagent_task = asyncio.create_task(multiagent_pipeline.run(text))

        baseline_result, multiagent_result = await asyncio.gather(baseline_task, multiagent_task)
    except Exception as e:
        logger.exception(f"Ошибка при выполнении пайплайнов baseline и multiagent: {e}")
        return {
            "error": str(e),
            "baseline": None,
            "multiagent": None,
            "metrics": {},
        }

    baseline_scores = extract_scores(baseline_result)
    multiagent_scores = extract_scores(multiagent_result)

    logger.debug(f"Baseline scores: {baseline_scores}")
    logger.debug(f"Multiagent scores: {multiagent_scores}")

    logger.info("Считаем метрики...")
    metrics = {}
    if human_scores is not None:
        metrics["baseline_vs_human"] = spearman_correlation(baseline_scores, human_scores)
        metrics["multiagent_vs_human"] = spearman_correlation(multiagent_scores, human_scores)

    result = {
        "baseline": baseline_result,
        "multiagent": multiagent_result,
        "metrics": metrics,
    }

    if judge_pipeline:
        try:
            logger.debug("Запускаем пайплайн judge...")
            judge_result = await judge_pipeline.evaluate(text, baseline_result, multiagent_result)
            result["judge"] = judge_result
        except Exception as e:
            logger.exception(f"Ошибка при выполнении пайплайна judge: {e}")
    
    logger.info("Оценка текста завершена.")
    return result


# прогон датасета
async def evaluate_dataset(
    texts: List[str],
    baseline_pipeline: BaselinePipeline,
    multiagent_pipeline: MultiAgentPipeline,
    judge_pipeline: Optional[JudgePipeline] = None,
    human_scores_list: Optional[List[List[float]]] = None,
    concurrency: int = 5,
) -> Dict[str, Any]:
    """
    Оценка датасета. 
    
    Использует evaluate_single для каждого текста, затем агрегирует метрики.

    Args:
        texts: Список текстов
        baseline_pipeline: Пайплайн для baseline
        multiagent_pipeline: Пайплайн для multi-agent
        judge_pipeline: Пайплайн для judge (опционально)
        human_scores_list: Список human-оценок (опционально)
        concurrency: Ограничение параллелизма для semaphore

    Returns:
        Итоговые метрики (средние по датасету) и список результатов для каждого текста + judge
    """
    logger.info(f"Начинаем оценку датасета из {len(texts)} текстов (concurrency={concurrency})...")

    semaphore = asyncio.Semaphore(concurrency)

    async def sem_task(index: int, text: str):
        async with semaphore:
            logger.info(f"Запускаем оценку текста {index + 1}/{len(texts)}...")

            human_scores = None
            if human_scores_list:
                human_scores = human_scores_list[index]

            # считаем метрики для одного текста
            return await evaluate_single(text, baseline_pipeline, multiagent_pipeline, judge_pipeline, human_scores)
    
    tasks = [asyncio.create_task(sem_task(i, text)) for i, text in enumerate(texts)]

    results = await asyncio.gather(*tasks)

    # агрегируем метрики
    logger.info(f"Оценка завершена. Вычисляем средние значения метрик...")
    def avg(values: List[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    baseline_vs_human = [result["metrics"]["baseline_vs_human"] for result in results if "baseline_vs_human" in result["metrics"]]
    multiagent_vs_human = [result["metrics"]["multiagent_vs_human"] for result in results if "multiagent_vs_human" in result["metrics"]]

    final = {
        "num_samples": len(texts),
        "metrics": {
            "baseline_vs_human_avg": avg(baseline_vs_human),
            "multiagent_vs_human_avg": avg(multiagent_vs_human),
        },
        "results": results,
    }

    logger.info(f"Оценка датасета завершена.")
    return final
