# агенты для генерации и улучшения рецензии (draft, critic, editor, final)

from scientific_review.client import Client
from scientific_review.utils import extract_json
from scientific_review.config import PROMPTS


class BaseReviewAgent:
    def __init__(self, name):
        self.name = name
        self.client = Client()

    def run(self, state):
        ...
        raise NotImplementedError("This method should be implemented by subclasses")
    

class RawReviewAgent(BaseReviewAgent):
    def __init__(self):
        super().__init__(name = 'raw_review_agent')

    def run(self, state):

        scores = {output['agent']: output['score'] for output in state.agents_outputs}
    
        reasons = {output['agent']: output['reason'] for output in state.agents_outputs}

        prompt = PROMPTS[self.name].format(text=state.text, scores=scores, reasons=reasons)
        response = self.client.generate(prompt)
        data = extract_json(response)

        review = data.get("Review", response)

        state.draft_review = review

        return state
    
class FinalReviewAgent(BaseReviewAgent):
    def __init__(self):
        super().__init__(name = 'final_review_agent')

    def run(self, state):

        prompt = PROMPTS[self.name].format(text=state.text, draft_review=state.draft_review)
        response = self.client.generate(prompt)
        data = extract_json(response)

        final_review = data.get("final_review", response)
        verdict = data.get("verdict", "undecided")

        state.final_review = final_review
        state.verdict = verdict

        return state
