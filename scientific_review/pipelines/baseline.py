import time
import uuid
from pathlib import Path

from scientific_review.llm.client import LLMClient
from scientific_review.utils.parser import extract_json


class BaselinePipeline:
    def __init__(self):
        self.client = LLMClient()
        self.prompt = Path("scientific_review/prompts/baseline.txt").read_text(encoding="utf-8")

    def run(self, text, paper_id=None):
        start = time.perf_counter()
        prompt = self.prompt.replace("{{TEXT}}", text)
        response = self.client.generate(prompt)
        data = extract_json(response["text"])

        return {
            "paper_id": paper_id or "unknown",
            "mode": "baseline",
            "scores": data["scores"],
            "verdict": data["verdict"],
            "strengths": data.get("strengths", []),
            "weaknesses": data.get("weaknesses", []),
            "suggestions": data.get("suggestions", []),
            "bias_risks": data.get("bias_risks", []),
            "explanations": data.get("explanations", {}),
            "criterion_comments": {},
            "review": data.get("review", ""),
            "review_consistency": None,
            "agents_outputs": [],
            "model_info": {
                "baseline_model": "qwen/qwen3-4b"
            },
            "runtime_info": {
                "latency": round(time.perf_counter() - start, 4),
                "usage": response["usage"],
                "cache_hit": False,
                "run_id": str(uuid.uuid4())
            },
            "raw_output": response["text"]
        }

    def close(self):
        self.client.close()
