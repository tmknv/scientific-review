from langgraph.graph import END, StateGraph

from scientific_review.agents.aggregator import aggregate
from scientific_review.agents.criteria.complexity import ComplexityAgent
from scientific_review.agents.criteria.novelty import NoveltyAgent
from scientific_review.agents.criteria.readability import ReadabilityAgent
from scientific_review.agents.criteria.scientificity import ScientificityAgent
from scientific_review.agents.review import ReviewAgent
from scientific_review.agents.state import ReviewState


class MultiAgentPipeline:
    def __init__(self):
        self.novelty = NoveltyAgent()
        self.scientificity = ScientificityAgent()
        self.complexity = ComplexityAgent()
        self.readability = ReadabilityAgent()
        self.review_agent = ReviewAgent()

        self.app = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(ReviewState)

        graph.add_node("novelty", self.novelty.run)
        graph.add_node("scientificity", self.scientificity.run)
        graph.add_node("complexity", self.complexity.run)
        graph.add_node("readability", self.readability.run)
        graph.add_node("review", self.review_agent.run)
        graph.add_node("aggregate", self._aggregate)

        graph.set_entry_point("novelty")
        graph.add_edge("novelty", "scientificity")
        graph.add_edge("scientificity", "complexity")
        graph.add_edge("complexity", "readability")
        graph.add_edge("readability", "review")
        graph.add_edge("review", "aggregate")
        graph.add_edge("aggregate", END)

        return graph.compile()

    def _aggregate(self, state):
        state["final_result"] = aggregate(state)
        return state

    def run(self, text, paper_id="unknown"):
        init_state = {
            "paper_id": paper_id,
            "text": text,
            "mode": "multiagent",
            "scores": {},
            "reasons": {},
            "issues": {},
            "agents_outputs": [],
        }

        final_state = self.app.invoke(init_state)
        return final_state["final_result"]

    def close(self):
        self.novelty.close()
        self.scientificity.close()
        self.complexity.close()
        self.readability.close()
        self.review_agent.close()
