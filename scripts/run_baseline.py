# быстрый запуск baseline pipeline

from scientific_review.baseline.baseline_pipeline import BaselinePipeline
from scientific_review.utils import save_json


if __name__ == "__main__":
    # текст статьи
    text = """
    This paper proposes a novel machine learning approach for NLP tasks.
    """

    pipeline = BaselinePipeline()
    result = pipeline.run(text)

    print(result)

    path = save_json(result, "runs/baseline")

    print("Saved to:", path)
