# scientific_review/evaluation/evaluator.py
# асинхронный evaluator: baseline vs multi-agent + human + judge + stability

import asyncio
from typing import List, Dict, Any, Optional

from scientific_review.utils import extract_scores, save_json
from scientific_review.evaluation.metrics import spearman_correlation, inter_run_variance

from scientific_review.baseline.baseline_pipeline import BaselinePipeline
from scientific_review.agents.multiagent_pipeline import MultiAgentPipeline
from scientific_review.evaluation.judge_pipeline import JudgePipeline


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
    - baseline_scores vs multiagent_scores

    Args:
        text: Текст статьи
        baseline_pipeline: Пайплайн для baseline
        multiagent_pipeline: Пайплайн для multi-agent
        judge_pipeline: Пайплайн для judge (опционально)
        human_scores: Human-оценки (опционально)

    Returns:
        Полный результат (baseline, multiagent, metrics, judge)
    """
    baseline_task = asyncio.create_task(baseline_pipeline.run(text))
    multiagent_task = asyncio.create_task(multiagent_pipeline.run(text))

    baseline_result, multiagent_result = await asyncio.gather(baseline_task, multiagent_task)

    baseline_scores = extract_scores(baseline_result)
    multiagent_scores = extract_scores(multiagent_result)

    metrics = {}
    if human_scores is not None:
        metrics["baseline_vs_human"] = spearman_correlation(baseline_scores, human_scores)
        metrics["multiagent_vs_human"] = spearman_correlation(multiagent_scores, human_scores)
    metrics["baseline_vs_multiagent"] = spearman_correlation(baseline_scores, multiagent_scores)

    result = {
        "baseline": baseline_result,
        "multiagent": multiagent_result,
        "metrics": metrics,
    }

    if judge_pipeline:
        judge_result = await judge_pipeline.evaluate(text, baseline_result, multiagent_result)
        result["judge"] = judge_result
    
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
        save_path: Путь для сохранения
        concurrency: Ограничение параллелизма для semaphore

    Returns:
        Итоговые метрики (средние по датасету) и список результатов для каждого текста + judge
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def sem_task(index: int, text: str):
        async with semaphore:
            human_scores = None
            if human_scores_list:
                human_scores = human_scores_list[index]
            # считаем метрики для одного текста
            return await evaluate_single(text, baseline_pipeline, multiagent_pipeline, judge_pipeline, human_scores)
    
    tasks = [asyncio.create_task(sem_task(i, text)) for i, text in enumerate(texts)]

    results = await asyncio.gather(*tasks)

    # агрегируем метрики
    def avg(values: List[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    baseline_vs_multiagent = [result["metrics"]["baseline_vs_multiagent"] for result in results]
    baseline_vs_human = [result["metrics"]["baseline_vs_human"] for result in results if "baseline_vs_human" in result["metrics"]]
    multiagent_vs_human = [result["metrics"]["multiagent_vs_human"] for result in results if "multiagent_vs_human" in result["metrics"]]

    final = {
        "num_samples": len(texts),
        "metrics": {
            "baseline_vs_multiagent_avg": avg(baseline_vs_multiagent),
            "baseline_vs_human_avg": avg(baseline_vs_human),
            "multiagent_vs_human_avg": avg(multiagent_vs_human),
        },
        "results": results,
    }

    return final


# stability
async def evaluate_stability(
    text: str, 
    baseline_pipeline: BaselinePipeline, 
    multiagent_pipeline: MultiAgentPipeline, 
    runs: int = 5, 
    concurrency: int = 5
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
