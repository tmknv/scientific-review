from langgraph.graph import StateGraph, END

from scientific_review.agents.state import ReviewState
from scientific_review.agents.criteria.novelty import NoveltyAgent
from scientific_review.agents.criteria.scientificity import ScientificityAgent
from scientific_review.agents.criteria.readability import ReadabilityAgent
from scientific_review.agents.criteria.complexity import ComplexityAgent
from scientific_review.agents.aggregator import aggregate


class MultiAgentPipeline:
    def __init__(self):
        self.novelty_agent = NoveltyAgent()

        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(ReviewState)

        # nodes
        graph.add_node("novelty", self.novelty_agent.run)
        graph.add_node("novelty", self.novelty_agent.run)
        graph.add_node("scientificity", self.scientificity_agent.run)
        graph.add_node("readability", self.readability_agent.run)
        graph.add_node("complexity", self.complexity_agent.run)
        graph.add_node("aggregate", lambda state: state)

        # edges
        graph.set_entry_point("novelty")
        graph.add_edge("novelty", "scientificity")
        graph.add_edge("scientificity", "readability")
        graph.add_edge("readability", "complexity")
        graph.add_edge("complexity", "aggregate")
        graph.add_edge("aggregate", END)

        return graph.compile()

    def run(self, text: str):
        state = ReviewState(text=text)

        final_state = self.graph.invoke(state)

        result = aggregate(final_state)

        return result