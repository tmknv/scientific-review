# основной multi-agent pipeline: запуск агентов и сбор финального результата

from scientific_review.agents.state import State
from scientific_review.agents.agents import NoveltyAgent, ScientificityAgent, ReadabilityAgent, ComplexityAgent, RawReviewAgent, FinalReviewAgent
from scientific_review.utils import final_score


class MultiAgentPipeline:
    def __init__(self):
        self.agents = [
            NoveltyAgent(),
            ScientificityAgent(),
            ReadabilityAgent(),
            ComplexityAgent(),
        ]

    def run(self, text):
        state = State(text=text)

        # оценки
        for agent in self.agents:
            state = agent.run(state)

        # рецензия
        state = RawReviewAgent().run(state)
        state = FinalReviewAgent().run(state)
        state.scores["final_score"] = final_score(state)


        return state
