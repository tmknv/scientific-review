# основной multi-agent pipeline: запуск агентов и сбор финального результата

from scientific_review.agents.state import State
from scientific_review.agents.criteria_agents import NoveltyAgent


class MultiAgentPipeline:
    def __init__(self):
        self.novelty_agent = NoveltyAgent()

    def run(self, text):
        state = State(text=text)

        # критерии
        state = self.novelty_agent.run(state)

        # финал (заглушка)
        state.final_review = "заглушка final_review"
        state.verdict = "заглушка verdict"

        return state
