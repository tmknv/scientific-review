# агенты-оценщики: novelty, scientificity, readability, complexity

from scientific_review.client import Client
from scientific_review.utils import extract_json
from scientific_review.config import PROMPTS


class BaseCriteriaAgent:
    def __init__(self, name):
        self.name = name
        self.client = Client()

    def run(self, state):
        prompt = PROMPTS[self.name].format(text=state.text)

        response = self.client.generate(prompt)
        data = extract_json(response)

        score = data.get("score", -1)
        reason = data.get("reason", response)

        state.scores[self.name] = score

        state.agents_outputs.append({
            "agent": self.name,
            "raw_output": response,
            "score": score,
            "reason": reason
        })

        return state


class NoveltyAgent(BaseCriteriaAgent):
    def __init__(self):
        super().__init__(name="novelty")


class ScientificityAgent(BaseCriteriaAgent):
    def __init__(self):
        super().__init__(name="scientificity")


class ReadabilityAgent(BaseCriteriaAgent):
    def __init__(self):
        super().__init__(name="readability")


class ComplexityAgent(BaseCriteriaAgent):
    def __init__(self):
        super().__init__(name="complexity")
