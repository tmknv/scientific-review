# быстрый запуск multi-agent pipeline

from scientific_review.agents.multiagent_pipeline import MultiAgentPipeline
from pprint import pprint

if __name__ == "__main__":
    # текст статьи
    text = """
    This paper proposes a novel machine learning approach for NLP tasks.
    """

    pipeline = MultiAgentPipeline()
    result = pipeline.run(text)

    print(result)
