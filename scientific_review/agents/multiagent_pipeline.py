# основной multi-agent pipeline: запуск агентов и сбор финального результата

from scientific_review.agents.state import State
from scientific_review.agents.criteria_agents import NoveltyAgent, ScientificityAgent, ReadabilityAgent, ComplexityAgent


class MultiAgentPipeline:
    def __init__(self):
        self.agents = [NoveltyAgent(), ScientificityAgent(), ReadabilityAgent(), ComplexityAgent()]

    def run(self, text):
        state = State(text=text)

        # критерии
        for agent in self.agents:
            state = agent.run(state)

        # ревью (заглушка)
        state.final_review = "заглушка final_review"
        state.verdict = "заглушка verdict"

        return state
