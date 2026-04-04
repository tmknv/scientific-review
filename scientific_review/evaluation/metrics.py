# scientific_review/evaluation/metrics.py
# метрики для оценки качества моделей (baseline vs multi-agent)

from typing import List
import numpy as np
from scipy.stats import spearmanr
from scientific_review.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def spearman_correlation(x: List[float], y: List[float]) -> float:
    """
    Вычисляет коэффициент корреляции Спирмена между двумя наборами оценок.

    Используется для сравнения:
    - baseline_scores vs human_scores
    - multiagent_scores vs human_scores
    - baseline_scores vs multiagent_scores (дополнительно)

    Args:
        x: Первый список значений
        y: Второй список значений

    Returns:
        Коэффициент Спирмена [-1, 1]
    """
    if len(x) != len(y):
        raise ValueError("Длины списков не совпадают")

    if len(x) < 2:
        return 0.0
    try:
        corr, _ = spearmanr(x, y)
        
    except Exception as e:
        logger.error(f"Ошибка при вычислении корреляции Спирмена: {e}")
        return 0.0

    # isnan возникает, если все значения в одном из списков одинаковы 
    # (нулевая дисперсия) => деление на ноль в формуле корреляции
    if np.isnan(corr):
        return 0.0

    return float(corr)


def inter_run_variance(runs: List[List[float]]) -> float:
    """
    Считает среднюю дисперсию по нескольким прогонам.

    Используется для stability test:
    - берём несколько прогонов одной статьи
    - считаем variance по каждому критерию
    - усредняем

    run1, run2, run3... -> mean variance

    Args:
        runs: Список прогонов, где каждый прогон — список оценок

    Returns:
        Средняя дисперсия
    """
    if len(runs) < 2:
        return 0.0

    runs = np.array(runs, dtype=float)

    # ddof=1 делает оценку дисперсии несмещенной (важно для малого числа прогонов),
    # чтобы не занижать реальную нестабильность (variance) ответов агента
    return float(np.mean(np.var(runs, axis=0, ddof=1)))
