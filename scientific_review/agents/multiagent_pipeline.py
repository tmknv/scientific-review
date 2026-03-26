# основной multi-agent pipeline: запуск агентов и сбор финального результата

from scientific_review.client import Client
from scientific_review.agents.state import State
from scientific_review.agents.agents import NoveltyAgent, ScientificityAgent, ReadabilityAgent, ComplexityAgent, RawReviewAgent, FinalReviewAgent
from scientific_review.utils import final_score


class MultiAgentPipeline:
    """
    Pipeline для одновременного запуска всех агентов и сбора результатов.
    
    Args:
        client: Клиент для взаимодействия с LLM. Если не передан, создается новый экземпляр Client().
    """

    def __init__(self, client: Client = None):
        if client is None:
            client = Client()
        
        self.client = client
        self.agents = [
            NoveltyAgent(client),
            ScientificityAgent(client),
            ReadabilityAgent(client),
            ComplexityAgent(client),
            RawReviewAgent(client),
            FinalReviewAgent(client),
        ]

    async def run(self, text: str) -> State:
        """
        Запускает pipeline обработки текста.
        
        Args:
            text: Текст научной статьи для анализа.
            
        Returns:
            State с результатами анализа всех агентов.
        """
        state = State(text=text)

        for agent in self.agents:
            state = await agent.run(state)

        state.scores["final_score"] = final_score(state)

        return state
