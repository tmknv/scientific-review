# основной multi-agent pipeline: запуск агентов и сбор финального результата

import asyncio
import copy
from langgraph.graph import START, StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

from scientific_review.client import Client
from scientific_review.agents.state import State
from scientific_review.agents.agents import NoveltyAgent, ScientificityAgent, ReadabilityAgent, ComplexityAgent, RawReviewAgent, FinalReviewAgent
from scientific_review.utils import final_score


class MultiAgentPipeline:
    """
    Pipeline для одновременного запуска всех агентов и сбора результатов.
    
    Args:
        client: Клиент для взаимодействия с LLM. Если не передан, создается новый экземпляр Client().
    
    returns:
        State с результатами анализа всех агентов.
    """

    def __init__(self, client: Client = None):
        if client is None:
            client = Client()
        
        self.client = client
        agents_list = [
            NoveltyAgent(client),
            ScientificityAgent(client),
            ReadabilityAgent(client),
            ComplexityAgent(client),
        ]
        self.agents = {agent.name: agent for agent in agents_list}
        self.raw_review_agent = RawReviewAgent(client)
        self.final_review_agent = FinalReviewAgent(client)

        self.workflow = self.build_workflow().compile()

    def build_workflow(self) -> StateGraph:
        """
        Строит граф выполнения агентов для LangGraph.
         returns:
            StateGraph, описывающий порядок выполнения агентов и передачу данных между ними.
        """

        workflow = StateGraph(state_schema=State)
        
        for name, agent in self.agents.items():
            workflow.add_node(name, agent.ainvoke)
            workflow.add_edge(START, name) 

        workflow.add_node("raw_review", self.raw_review_agent.ainvoke)
        workflow.add_node("final_review", self.final_review_agent.ainvoke)

        for agent_name in self.agents.keys():
            workflow.add_edge(agent_name, "raw_review")

        workflow.add_edge("raw_review", "final_review")

        workflow.add_edge("final_review", END)

        return workflow

    async def run(self, text: str) -> State:
        """
        Запускает pipeline обработки текста.
        
        Args:
            text: Текст научной статьи для анализа.
            
        Returns:
            State с результатами анализа всех агентов.
        """
        initial_state = State(text=text, messages=[SystemMessage(content=text)])
        final_state = await self.workflow.ainvoke(initial_state)

        if not isinstance(final_state, State):
            final_state = State(**final_state)
        else:
            final_state = final_state

        final_state.scores["final_score"] = final_score(final_state)

        return final_state
