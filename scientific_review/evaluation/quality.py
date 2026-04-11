# scientific_review/evaluation/quality.py
# оценка качества: baseline vs multi-agent (human labels + judge)

import asyncio
from typing import List, Dict, Any, Optional

from scientific_review.utils.utils import extract_scores
from scientific_review.evaluation.metrics import spearman_correlation
from scientific_review.utils.logger import setup_logging, get_logger
from scientific_review.utils.params import get_params

from scientific_review.baseline.baseline_pipeline import BaselinePipeline
from scientific_review.agents.multiagent_pipeline import MultiAgentPipeline
from scientific_review.evaluation.judge_pipeline import JudgePipeline

setup_logging()
logger = get_logger(__name__)
params = get_params()

# прогон одного текста
async def evaluate_single(
    text: str,
    multiagent_pipeline: MultiAgentPipeline,
    baseline_pipeline: Optional[BaselinePipeline] = None,
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

        {
            "baseline": ...,
            "multiagent": ...,
            "metrics": {
                "baseline_vs_human": ...,
                "multiagent_vs_human": ...
            },
            "human_scores": human_scores,
            "judge": ...,
        }
    """
    try:
        logger.debug("Запускаем пайплайны baseline и multiagent...")
        tasks = []
        if baseline_pipeline:
            tasks.append(asyncio.create_task(baseline_pipeline.run(text)))
        tasks.append(asyncio.create_task(multiagent_pipeline.run(text)))

        results = await asyncio.gather(*tasks)

        result = {
            "baseline": None,
            "multiagent": None, 
            "metrics": {},
            "human_scores": human_scores,
        }

        if baseline_pipeline:
            baseline_result = results[0]
            baseline_scores = extract_scores(baseline_result)
            result["baseline"] = baseline_result
            logger.debug(f"Baseline scores: {baseline_scores}")
            multiagent_result = results[1]
        else:
            baseline_result = None
            baseline_scores = None
            multiagent_result = results[0]
        multiagent_scores = extract_scores(multiagent_result)
        result["multiagent"] = multiagent_result
        logger.debug(f"Multiagent scores: {multiagent_scores}")
        
    except Exception as e:
        logger.exception(f"Ошибка при выполнении пайплайнов baseline и multiagent: {e}")
        result["error"] = str(e)
        return result

    logger.info("Считаем метрики...")
    if human_scores is not None:
        if baseline_pipeline:
            result["metrics"]["baseline_vs_human"] = spearman_correlation(baseline_scores, human_scores)
        result["metrics"]["multiagent_vs_human"] = spearman_correlation(multiagent_scores, human_scores)

    if judge_pipeline:
        try:
            logger.debug("Запускаем пайплайн judge...")
            judge_result = await judge_pipeline.evaluate(text, baseline_result, multiagent_result, baseline_scores, human_scores)
            result["judge"] = judge_result
        except Exception as e:
            logger.exception(f"Ошибка при выполнении пайплайна judge: {e}")
    
    logger.info("Оценка текста завершена.")
    return result


# прогон датасета
async def evaluate_dataset(
    texts: List[str],
    multiagent_pipeline: MultiAgentPipeline,
    baseline_pipeline: Optional[BaselinePipeline] = None,
    judge_pipeline: Optional[JudgePipeline] = None,
    human_scores_list: Optional[List[List[float]]] = None,
    concurrency: int = params["evaluation"]["concurrency"],
) -> Dict[str, Any]:
    """
    Оценка датасета. 
    
    Использует evaluate_single для каждого текста, затем агрегирует метрики.

    Args:
        texts: Список текстов
        multiagent_pipeline: Пайплайн для multi-agent
        baseline_pipeline: Пайплайн для baseline (опционально для ablation)
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
            return await evaluate_single(text, multiagent_pipeline, baseline_pipeline, judge_pipeline, human_scores)
    
    tasks = [asyncio.create_task(sem_task(i, text)) for i, text in enumerate(texts)]

    results = await asyncio.gather(*tasks)
    small_results = [
        {
            "metrics": r.get("metrics", {}),
            "review_baseline": r.get("baseline", {}).get("review") if r.get("baseline") else None,
            "scores_baseline": r.get("baseline", {}).get("scores", []) if r.get("baseline") else None,
            "review_multiagent": r.get("multiagent", {}).final_review if r.get("multiagent") else None,
            "scores_multiagent": r.get('multiagent', {}).scores if r.get("multiagent") else None,
            "judge": r.get("judge"),
            "human_scores": r.get("human_scores"),
        }
        for r in results
    ]
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
        "results": small_results,
    }

    logger.info(f"Оценка датасета завершена.")
    return final
