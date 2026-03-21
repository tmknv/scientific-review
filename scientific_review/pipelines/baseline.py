import uuid
import time
from scientific_review.llm.client import LLMClient
from scientific_review.utils.parser import extract_json

def load_prompt(path):
    with open(path, "r") as f:
        return f.read()


class BaselinePipeline:
    def __init__(self):
        self.client = LLMClient()

        self.prompt_template = load_prompt(
            "scientific_review/prompts/baseline.txt"
        )

    def run(self, text: str, paper_id: str = None):
        run_id = str(uuid.uuid4())
        start = time.time()

        prompt = self.prompt_template.replace("{{TEXT}}", text)

        response = self.client.generate(prompt)

        parsed = extract_json(response["text"])

        latency = time.time() - start

        result = {
            "paper_id": paper_id or "unknown",
            "mode": "baseline",
            "scores": parsed.get("scores", {}),
            "verdict": parsed.get("verdict"),
            "review": parsed.get("review"),
            "strengths": parsed.get("strengths", []),
            "weaknesses": parsed.get("weaknesses", []),
            "suggestions": parsed.get("suggestions", []),
            "bias_risks": parsed.get("bias_risks", []),
            "explanations": parsed.get("explanations", {}),
            "model_info": {
                "baseline_model": self.client.model,
            },
            "runtime_info": {
                "latency": latency,
                "token_usage": response.get("usage", {}),
                "run_id": run_id,
                "timestamp": time.time(),
            },
            "raw_output": response["text"],
        }

        return result