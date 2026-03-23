# быстрый запуск multi-agent pipeline

from scientific_review.agents.multiagent_pipeline import MultiAgentPipeline
from scientific_review.utils import save_json


if __name__ == "__main__":
    # текст статьи
    text = """
    This paper proposes a novel machine learning approach for NLP tasks.
    """

    pipeline = MultiAgentPipeline()
    state = pipeline.run(text)

    result = {
        "scores": state.scores,
        "review": state.final_review,
        "verdict": state.verdict,
        "agents_outputs": state.agents_outputs
    }

    print(result)

    path = save_json(result, "runs/multiagent")

    print("Saved to:", path)
