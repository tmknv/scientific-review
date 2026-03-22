from pathlib import Path

from scientific_review.llm.client import LLMClient


class ReviewAgent:
    def __init__(self):
        self.client = LLMClient(temperature=0.3, max_tokens=1200)
        self.prompt = Path("scientific_review/prompts/agents/review.txt").read_text(encoding="utf-8")

    def build_context(self, state):
        lines = []
        for key in ["novelty", "scientificity", "complexity", "readability"]:
            score = state.get("scores", {}).get(key, 0)
            reason = state.get("reasons", {}).get(key, "")
            issues = state.get("issues", {}).get(key, [])
            lines.append(
                f"{key}: score={score}\nreason={reason}\nissues={'; '.join(issues) if issues else 'none'}"
            )
        return "\n\n".join(lines)

    def run(self, state):
        prompt = self.prompt.replace("{{TEXT}}", state["text"])
        prompt = prompt.replace("{{CRITERIA_SUMMARY}}", self.build_context(state))

        response = self.client.generate(prompt)
        state["review"] = response["text"].strip()
        state.setdefault("agents_outputs", []).append(
            {"agent": "review", "raw": response["text"]}
        )
        return state

    def close(self):
        self.client.close()
