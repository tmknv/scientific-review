# bot/client.py
import asyncio
import random
from typing import Dict, Any

class AnalysisClient:
    """Клиент для анализа (мок по ТЗ).
    В реальном проекте замените на httpx.post к api/main.py"""
    
    async def analyze(self, text: str, mode: str) -> Dict[str, Any]:
        await asyncio.sleep(1.5)  # имитация обработки
        
        scores = {
            "новизна": random.randint(65, 98),
            "научность": random.randint(70, 99),
            "сложность": random.randint(45, 85),
            "читаемость": random.randint(55, 95),
        }
        total = sum(scores.values()) // 4
        
        review = (
            f"✅ Мок-рецензия ({mode}):\n"
            f"Текст обладает высокой научной ценностью. "
            f"Рекомендуется усилить раздел «Обсуждение результатов»."
        )
        
        result = {
            "total_score": total,
            "scores": scores,
            "review": review,
            "mode": mode
        }
        
        # Специальная логика по ТЗ
        if mode == "Тест стабильности":
            runs = [random.randint(70, 95) for _ in range(5)]
            avg = sum(runs) / 5
            variance = sum((x - avg) ** 2 for x in runs) / 5
            result["stability"] = {
                "runs": runs,
                "average": round(avg, 2),
                "variance": round(variance, 2)
            }
        
        if mode == "Сравнение моделей":
            result["comparison"] = {
                "llm": {"total": total - 5, "review": "Быстрый LLM"},
                "multi": {"total": total + 3, "review": "Multi-agent"}
            }
        
        return result