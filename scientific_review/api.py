# scientific-review/scientific_review/api.py
# FastAPI для работы с API

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import asyncio

from scientific_review.client import Client
from scientific_review.baseline.baseline_pipeline import BaselinePipeline
from scientific_review.agents.multiagent_pipeline import MultiAgentPipeline
from scientific_review.evaluation.judge_pipeline import JudgePipeline

from scientific_review.evaluation.quality import evaluate_single, evaluate_dataset
from scientific_review.evaluation.stability import evaluate_stability
from scientific_review.evaluation.ablation import evaluate_ablation, build_ablation_summary
from scientific_review.utils.utils import state_to_dict


app = FastAPI(
    title="Scientific Review API", 
    description="API for Baseline and Multi-Agent Scientific Paper Review"
)

client = Client()
baseline_pipeline = BaselinePipeline(client)
multiagent_pipeline = MultiAgentPipeline(client)
judge_pipeline = JudgePipeline(client)

class ReviewRequest(BaseModel):
    """
    Класс для обработки входящих запросов на рецензирование научной статьи.
    
    Attributes:
        text (str): Текст статьи в формате txt
    """
    text: str

class ReviewResponse(BaseModel):
    """
    Класс для обработки выходящих данных рецензирования научной статьи.
    
    Attributes:
        scores (Dict[str, Any]): Словарь с ключами и значениями оценок по критериям
        verdict (str): Оценка в виде строки от одного из ключей в scores
        review (str): Полный текст рецензии
        raw_output (Optional[Any]): Исходные данные выполнения агентов  
    """
    scores: Dict[str, Any]
    verdict: str
    review: str
    raw_output: Optional[Any] = None

class MultiAgentResponse(BaseModel):
    """
    Класс для обработки выходящих данных рецензирования научной статьи с использованием многоагентной системы.
    
    Attributes:
        scores (Dict[str, Any]): Словарь с ключами и значениями оценок по критериям
        reasons (Dict[str, str]): Словарь с ключами и значениями причин оценок по критериям
        final_review (str): Полный текст рецензии
        verdict (str): Вердикт
        agents_outputs (Dict[str, Any]): Словарь с ключами-именами агентов и значениями их выводов
        metadata (Dict[str, Any]): Метаданные    
    """
    scores: Dict[str, Any]
    reasons: Dict[str, str]
    final_review: str
    verdict: str
    agents_outputs: Dict[str, Any]
    metadata: Dict[str, Any]

class QualityRequest(BaseModel):
    """
    Класс для обработки входящих запросов на оценку качества текста.
    
    Attributes:
        text (str): Текст статьи в формате txt
        human_scores (Optional[List[float]]): Список human-оценок для каждого текста
    """
    text: str
    human_scores: Optional[List[float]] = None

class QualityDatasetRequest(BaseModel):
    """
    Класс для обработки входящих запросов на оценку качества датасета текстов.
    
    Attributes:
        texts (List[str]): Список текстов в формате txt
        human_scores (Optional[List[List[float]]]): Список списков human-оценок для каждого текста
        concurrency (int): Количество параллельных запросов к API (опционально)
    """
    texts: List[str]
    human_scores: Optional[List[List[float]]] = None
    concurrency: int = 5

class StabilityRequest(BaseModel):
    """
    Класс для обработки входящих запросов на оценку стабильности текста.
    
    Attributes:
        text (str): Текст статьи в формате txt
        runs (int): Количество запусков оценки (опционально)
        concurrency (int): Количество параллельных запросов к API (опционально)                
    """
    text: str
    runs: int = 15
    concurrency: int = 3

class AblationRequest(BaseModel):
    """
    Класс для обработки входящих запросов на аблацирование оценок.
    
    Attributes:
        texts (List[str]): Список текстов в формате txt
        human_scores (List[List[float]]): Список списков human-оценок для каждого текста
        concurrency (int): Количество параллельных запросов к API (опционально)                
    """
    texts: List[str]
    human_scores: List[List[float]]
    concurrency: int = 5

@app.post("/review/baseline", response_model=ReviewResponse)
async def review_baseline(request: ReviewRequest):
    """
    Обработка запроса на рецензирование научной статьи с использованием базовой системы.
    
    Args:
        request (ReviewRequest): Объект с данными запроса

    Returns:
        ReviewResponse: Объект с данными ответа
    """
    try:
        result = await baseline_pipeline.run(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/review/multiagent", response_model=MultiAgentResponse)
async def review_multiagent(request: ReviewRequest):
    """
    Обработка запроса на рецензирование научной статьи с использованием многоагентной системы.
    
    Args:
        request (ReviewRequest): Объект с данными запроса

    Returns:
        MultiAgentResponse: Объект с данными ответа
    """
    try:
        state = await multiagent_pipeline.run(request.text)
        return state_to_dict(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/review/compare")
async def review_compare(request: ReviewRequest):
    """
    Обработка запроса на сравнение рецензирования научной статьи с использованием baseline и multi-agent систем.
    
    Args:
        request (ReviewRequest): Объект с данными запроса

    Returns:
        Dict[str, Any]: Словарь с данными ответа, включающий результаты обеих систем
    """
    try:
        baseline_task = asyncio.create_task(baseline_pipeline.run(request.text))
        multiagent_task = asyncio.create_task(multiagent_pipeline.run(request.text))
        
        baseline_result, multiagent_result = await asyncio.gather(baseline_task, multiagent_task)
        
        return {
            "baseline": baseline_result,
            "multiagent": state_to_dict(multiagent_result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/quality/single")
async def test_quality_single(request: QualityRequest):
    """
    Обработка запроса на оценку одной статьи.
    
    Args:
        request (QualityRequest): Объект с данными запроса

    Returns:
        Dict[str, Any]: Словарь с данными ответа
    """
    try:
        result = await evaluate_single(
            text=request.text,
            multiagent_pipeline=multiagent_pipeline,
            baseline_pipeline=baseline_pipeline,
            judge_pipeline=judge_pipeline,
            human_scores=request.human_scores
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/experiment/quality/dataset")
async def test_quality_dataset(request: QualityDatasetRequest):
    """
    Обработка запроса на оценку качества датасета текстов.

    Args:
        request (QualityDatasetRequest): Объект с данными запроса

    Returns:
        Итоговые метрики (средние по датасету) и список результатов для каждого текста + judge
    """
    try:
        result = await evaluate_dataset(
            texts=request.texts,
            multiagent_pipeline=multiagent_pipeline,
            baseline_pipeline=baseline_pipeline,
            judge_pipeline=judge_pipeline,
            human_scores_list=request.human_scores,
            concurrency=request.concurrency
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/experiment/stability")
async def test_stability(request: StabilityRequest):
    """
    Обработка запроса на оценку стабильности текста.

    Args:
        request (StabilityRequest): Объект с данными запроса

    Returns:
        Результаты оценки стабильности    
    """
    try:
        result = await evaluate_stability(
            text=request.text,
            baseline_pipeline=baseline_pipeline,
            multiagent_pipeline=multiagent_pipeline,
            runs=request.runs,
            concurrency=request.concurrency
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/experiment/ablation")
async def test_ablation(request: AblationRequest):
    """
    Обработка запроса на ablation study.

    Args:
        request (AblationRequest): Объект с данными запроса

    Returns:
        Список результатов для каждой конфигурации
    """
    try:
        results = await evaluate_ablation(
            texts=request.texts,
            human_scores=request.human_scores,
            concurrency=request.concurrency
        )
        return build_ablation_summary(results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
