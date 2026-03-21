import time
import uuid

from langgraph.graph import END, StateGraph

from scientific_review.agents.aggregator import aggregate
from scientific_review.agents.criteria.complexity import ComplexityAgent
from scientific_review.agents.criteria.novelty import NoveltyAgent
from scientific_review.agents.criteria.readability import ReadabilityAgent
from scientific_review.agents.criteria.scientificity import ScientificityAgent
from scientific_review.agents.review.critic import CriticAgent
from scientific_review.agents.review.draft import DraftReviewerAgent
from scientific_review.agents.review.editor import EditorAgent
from scientific_review.agents.review.final import FinalReviewerAgent
from scientific_review.agents.review.consistency import ConsistencyCheckerAgent


class MultiAgentPipeline:
    """LangGraph-based multi-agent pipeline."""

    def __init__(self):
        self.novelty = NoveltyAgent()
        self.scientificity = ScientificityAgent()
        self.readability = ReadabilityAgent()
        self.complexity = ComplexityAgent()

        self.draft = DraftReviewerAgent()
        self.critic = CriticAgent()
        self.editor = EditorAgent()
        self.final = FinalReviewerAgent()
        self.consistency = ConsistencyCheckerAgent()

        self.app = self.build_graph()

    def build_graph(self):
        graph = StateGraph(dict)

        # nodes
        graph.add_node("novelty", self.novelty.run)
        graph.add_node("scientificity", self.scientificity.run)
        graph.add_node("readability", self.readability.run)
        graph.add_node("complexity", self.complexity.run)

        graph.add_node("draft", self.draft.run)
        graph.add_node("critic", self.critic.run)
        graph.add_node("editor", self.editor.run)
        graph.add_node("final", self.final.run)
        graph.add_node("consistency", self.consistency.run)

        graph.add_node("aggregate", self.aggregate_node)

        # edges
        graph.set_entry_point("novelty")
        graph.add_edge("novelty", "scientificity")
        graph.add_edge("scientificity", "readability")
        graph.add_edge("readability", "complexity")
        graph.add_edge("complexity", "draft")
        graph.add_edge("draft", "critic")
        graph.add_edge("critic", "editor")
        graph.add_edge("editor", "final")
        graph.add_edge("final", "consistency")
        graph.add_edge("consistency", "aggregate")
        graph.add_edge("aggregate", END)

        return graph.compile()

    def aggregate_node(self, state):
        state["final_result"] = aggregate(state)
        return state

    def run(self, text, paper_id=None):
        start = time.perf_counter()

        init_state = {
            "paper_id": paper_id or "unknown",
            "text": text,
            "mode": "multiagent",
            "scores": {},
            "explanations": {},
            "comments": {},
            "agents_outputs": [],
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "bias_risks": []
        }

        final_state = self.app.invoke(init_state)
        result = final_state["final_result"]

        result["model_info"] = {
            "baseline_model": "qwen/qwen3-4b"
        }
        result["runtime_info"] = {
            "latency": round(time.perf_counter() - start, 4),
            "usage": self.collect_usage(final_state.get("agents_outputs", [])),
            "cache_hit": False,
            "run_id": str(uuid.uuid4())
        }
        result["raw_output"] = None
        return result

    def collect_usage(self, outputs):
        usage = {}
        for item in outputs:
            for k, v in item.get("usage", {}).items():
                usage[k] = usage.get(k, 0) + v
        return usage

    def close(self):
        for agent in [self.novelty, self.scientificity, self.readability, self.complexity,
                      self.draft, self.critic, self.editor, self.final, self.consistency]:
            agent.close()
