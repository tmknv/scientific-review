# scientific_review/evaluation/ablation.py
# ablation study (убираем агентов и смотрим деградацию)

from typing import List, Dict, Any

from scientific_review.evaluation.quality import evaluate_dataset
from scientific_review.utils.logger import setup_logging, get_logger
from scientific_review.utils.params import get_params

from scientific_review.agents.multiagent_pipeline import MultiAgentPipeline
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
            "full": ["NoveltyAgent", "ScientificityAgent", "ReadabilityAgent", "ComplexityAgent"],

            # drop-one
            "no_NoveltyAgent": ["ScientificityAgent", "ReadabilityAgent", "ComplexityAgent"],
            "no_ScientificityAgent": ["NoveltyAgent", "ReadabilityAgent", "ComplexityAgent"],
            "no_ReadabilityAgent": ["NoveltyAgent", "ScientificityAgent", "ComplexityAgent"],
            "no_ComplexityAgent": ["NoveltyAgent", "ScientificityAgent", "ReadabilityAgent"],

            # keep-one
            "only_NoveltyAgent": ["NoveltyAgent"],
            "only_ScientificityAgent": ["ScientificityAgent"],
            "only_ReadabilityAgent": ["ReadabilityAgent"],            
            "only_ComplexityAgent": ["ComplexityAgent"],
        }
    """
    full = params["criteria"]["names"]

    configs = {
        "full": full,
    }

    # drop-one
    for agent in full:
        configs[f"no_{agent}"] = [a for a in full if a != agent]

    # keep-one
    for agent in full:
        configs[f"only_{agent}"] = [agent]

    return configs


async def evaluate_ablation(
        texts: List[str], 
        human_scores: List[List[float]], 
        concurrency: int = params["evaluation"]["concurrency"]
) -> Dict[str, Any]:
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
    logger.info(f"Запуск ablation study (concurrency={concurrency})...")

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


def compute_importance(results: Dict[str, Any]) -> Dict[str, float]:
    """
    Считает вклад каждого агента (drop-one).

    Args: 
        results: Результат evaluate_ablation

    Returns:
        Словарь: ...Agent -> importance (delta между full и no_...Agent)

    Example:
        {
            "NoveltyAgent": 0.01,       # минимальный вклад
            "ScientificityAgent": 0.14, # умеренный вклад
            "ReadabilityAgent": 0.17,   # максимальный вклад
            "ComplexityAgent": 0.01,    # минимальный вклад
        }
    """
    full_score = results["full"]["metrics"]["multiagent_vs_human_avg"]
    importance = {}

    for config, data in results.items():
        if config.startswith("no_"):
            agent = config.replace("no_", "")
            score = data["metrics"]["multiagent_vs_human_avg"]
            importance[agent] = full_score - score

    # сортировка по важности
    return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))


def build_ablation_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Строит json-friendly summary:
    configs:
        - spearman
        - delta_vs_full
    importance:
        - importance

    Args:
        results: Результат evaluate_ablation

    Returns:
        Словарь с summary по каждой конфигурации и важности агентов
    """
    full_score = results["full"]["metrics"]["multiagent_vs_human_avg"]

    configs_summary = {}

    for config, data in results.items():
        score = data["metrics"]["multiagent_vs_human_avg"]

        delta = score - full_score

        configs_summary[config] = {
            "spearman": score,
            "delta_vs_full": delta,
        }

    importance = compute_importance(results)

    return {
        "configs": configs_summary,
        "importance": importance,
    }


def format_ablation_table(summary: Dict[str, Any]) -> str:
    """
    Формирует таблицу из json-формата результата evaluate_ablation.

    Args:
        results: Результат evaluate_ablation

    Returns:
        Отформатированная таблица

    Example:
        Config                    Spearman   Δ vs full   
        -----------------------------------------------
        full                      0.6200     -
        no_NoveltyAgent           0.6000     -0.0200
        no_ScientificityAgent     0.4800     -0.1400
        no_ReadabilityAgent       0.4500     -0.1700
        no_ComplexityAgent        0.6100     -0.0100
        only_NoveltyAgent         0.3000     -0.3200
        only_ScientificityAgent   0.5000     -0.1200
        only_ReadabilityAgent     0.4200     -0.2000
        only_ComplexityAgent      0.2800     -0.3400
    """
    lines = []
    header = f"{'Config':<25} {'Spearman':<10} {'Δ vs full':<12}"
    separator = "-" * len(header)

    lines.append(header)
    lines.append(separator)

    configs = summary["configs"]

    ordered_keys = (
        ["full"]
        + [k for k in configs if k.startswith("no_")]
        + [k for k in configs if k.startswith("only_")]
    )

    for config in ordered_keys:
        data = configs[config]
        score = data["spearman"]
        delta = data["delta_vs_full"]

        if config == "full":
            delta_str = "-"
        else:
            delta_str = f"{delta:+.4f}"

        lines.append(f"{config:<25} {score:<10.4f} {delta_str:<12}")

    return "\n".join(lines)
