# агенты-оценщики: novelty, scientificity, readability, complexity

from scientific_review.agents.state import State
from scientific_review.client import Client
from scientific_review.utils import extract_json

class NoveltyAgent:
    def __init__(self):
        self.client = Client()

    def run(self, state):
        prompt = f"""
            You are a scientific reviewer.

            Evaluate the NOVELTY of the following paper.

            Return STRICT JSON:
            {{
                "score": 1-10,
                "reason": "short explanation"
            }}

            Paper:
            {state.text}
            """

        response = self.client.generate(prompt)
        data = extract_json(response)

        score = data.get("score", -1)
        reason = data.get("reason", response)

        state.scores["novelty"] = score

        state.agents_outputs.append({
            "agent": "novelty",
            "raw_output": response,
            "parsed_score": score,
            "reason": reason
        })

        return state
