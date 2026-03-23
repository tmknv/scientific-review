# основной multi-agent pipeline: запуск агентов и сбор финального результата

from scientific_review.agents.state import State
from scientific_review.agents.criteria_agents import NoveltyAgent, ScientificityAgent, ReadabilityAgent, ComplexityAgent
from scientific_review.agents.review_agents import RawReviewAgent, FinalReviewAgent


class MultiAgentPipeline:
    def __init__(self):
        self.agents = [
            NoveltyAgent(),
            ScientificityAgent(),
            ReadabilityAgent(),
            ComplexityAgent(),
        ]

    def run(self, text: str) -> State:
        state = State(text=text)

        # этап 1 — агенты
        for agent in self.agents:
            state = agent.run(state)

        # этап 2 — генерация рецензии
        state = RawReviewAgent().run(state)
        state = FinalReviewAgent().run(state)

        return state
