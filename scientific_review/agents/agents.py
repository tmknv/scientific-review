# агенты: критерии и рецензенты. Каждый агент - отдельный класс с методом run, который принимает state и возвращает новый state.
# BaseAgent - общий функционал, от которого наследуются все агенты. В нем можно хранить клиента, общие методы для парсинга и тд.

from abc import ABC, abstractmethod
import time
import traceback

from scientific_review.utils.utils import extract_json, serialize_messages
from scientific_review.utils.params import get_params
from scientific_review.utils.prompts import get_prompt_parts
from scientific_review.utils.logger import setup_logging, get_logger
from scientific_review.agents.state import State

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

setup_logging()
logger = get_logger(__name__)
params = get_params()


class BaseAgent(ABC):
    """
    Базовый класс для всех агентов. Содержит общую логику и интерфейс.
    Все агенты должны наследоваться от этого класса и реализовывать метод run.

    Args:
        name (str): Имя агента
        client: Асинхронный клиент для взаимодействия с LLM
    """
    def __init__(self,  client):
        self._name = self.__class__.__name__
        self.client = client

    @property
    def name(self) -> str:
        """
        Возвращает имя агента.

        Returns:
            str: Имя агента.
        """
        return self._name
    
    def build_messages(self, state: State, **kwargs)-> list[SystemMessage | HumanMessage]:
        """
        Строит список сообщений для запроса к модели.

        Args:
            state: Входной state для агента
            **kwargs: Дополнительные параметры для заполнения промта
        
        Returns:
            list[SystemMessage | HumanMessage]: Список сообщений для модели
        """

        system_prompt, user_prompt = get_prompt_parts(self.name, **kwargs)
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Текст статьи:\n{state.text}\n\n{user_prompt}")
        ]
    
    async def request_model(self, state: State, **kwargs) -> str:
        """
        Строит промт для агента, отрпавляет запрос к модели и возвращает ответ.

        Args:
            state: Входной state для агента
            **kwargs: Дополнительные параметры для заполнения промта
        
        Returns:
            str: Ответ модели
        """
        messages = self.build_messages(state, **kwargs)

        logger.info(f"{self.name} запрос отправлен")
        response = await self.client.generate(
            serialize_messages(messages),
            model=params["models"]["agent"],
        )
        logger.info(f"{self.name} отработал")
        return response
    

    @abstractmethod
    async def run(self, state: State) -> State:
        """
        Основной метод агента.

        Args:
            state: Входной state 

        Returns:
            State: Обновленный state 
        """
        pass
    
    async def ainvoke(self, state: State) -> State:
        """
        Метод для интеграции с LangGraph.

        Args:
            state: Входной state 

        Returns:
            State: Обновленный state 
        """
        return await self.analyze(state)
    
    async def analyze(self, state: State) -> State:
        """
        Метод для запуска агента с обработкой ошибок и временем выполнения.

        Args:
            state: Входной state 

        Returns:
            State: Обновленный state с метаданными 
        """
        start_time = time.time()
        try:
            state = await self.run(state)
            state.metadata[f"{self.name}_success"] = True

        except Exception as e:
            state.metadata[f"{self.name}_error"] = str(e)
            state.metadata[f"{self.name}_trace"] = traceback.format_exc()
            state.metadata[f"{self.name}_success"] = False
            logger.error(f"{self.name} failed: {e}", exc_info=True)
            raise

        finally:
            state.metadata[f"{self.name}_time"] = time.time() - start_time

        return state
    



class NoveltyAgent(BaseAgent):
    """
    Агент, оценивающий новизну статьи.

    Извлекает:
        - текст статьи из state.text

    Генерирует:
        - оценку новизны (0–10)
        - объяснение оценки

    Заполняет:
        state.scores["novelty"] - числовая оценка от 0 до 10
        state.reasons["novelty"] - объяснение оценки
        state.agents_outputs["novelty"] - сохранение ответа агента
    """

    async def run(self, state: State) -> State:

        response = await self.request_model(state)

        data = extract_json(response)

        score = data.get("score", -1)
        reason = data.get("reason", "")

        state.messages.append(AIMessage(content=f"score={score}, reason={reason}", name=self.name))
        state.agents_outputs[self.name] = {
            "score": score,
            "reason": reason
        }

        state.scores["novelty"] = score
        state.reasons["novelty"] = reason
        return state


class ScientificityAgent(BaseAgent):
    """
    Aгент, оценивающий научность статьи.

    Извлекает:
        - текст статьи из state.text

    Генерирует:
        - оценку научности (0–10)
        - объяснение оценки
    
    Заполняет:
        state.scores["scientificity"] - числовая оценка от 0 до 10
        state.reasons["scientificity"] - объяснение оценки
        state.agents_outputs["scientificity"] - сохранение ответа агента
    """

    async def run(self, state: State) -> State:

        response = await self.request_model(state)
        data = extract_json(response)

        score = data.get("score", -1)
        reason = data.get("reason", "")

        state.messages.append(AIMessage(content=f"score={score}, reason={reason}", name=self.name))
        
        state.agents_outputs[self.name] = {
            "score": score,
            "reason": reason
        }

        state.scores["scientificity"] = score
        state.reasons["scientificity"] = reason
        return state


class ReadabilityAgent(BaseAgent):
    """
    Aгент, оценивающий читаемость статьи.

    Извлекает:
        - текст статьи из state.text

    Генерирует:
        - оценку читаемости (0–10)
        - объяснение оценки
    
    Заполняет:
        state.scores["readability"] - числовая оценка от 0 до 10
        state.reasons["readability"] - объяснение оценки        
        state.agents_outputs["readability"] - сохранение ответа агента
    """

    async def run(self, state: State) -> State:    

        response = await self.request_model(state)
        data = extract_json(response)
        
        score = data.get("score", -1)
        reason = data.get("reason", "")

        state.messages.append(AIMessage(content=f"score={score}, reason={reason}", name=self.name))
        state.agents_outputs[self.name] = {
            "score": score,
            "reason": reason
        }

        state.scores["readability"] = score
        state.reasons["readability"] = reason
        return state


class ComplexityAgent(BaseAgent):
    """
    Aгент, оценивающий сложность статьи.

    Извлекает:    
        - текст статьи из state.text

    Генерирует:
        - оценку сложности (0–10)
        - объяснение оценки

    Заполняет:
        state.scores["complexity"] - числовая оценка от 0 до 10
        state.reasons["complexity"] - объяснение оценки
        state.agents_outputs["complexity"] - сохранение ответа агента
    """

    async def run(self, state: State) -> State:

        response = await self.request_model(state)
        data = extract_json(response)

        score = data.get("score", -1)
        reason = data.get("reason", "")

        state.messages.append(AIMessage(content=f"score={score}, reason={reason}", name=self.name))
        
        state.agents_outputs[self.name] = {
            "score": score,
            "reason": reason
        }

        state.scores["complexity"] = score
        state.reasons["complexity"] = reason
        return state


class RawReviewAgent(BaseAgent):
    """
    Aгент, который на основе текста статьи и оценок от критериев 
    пишет черновой вариант рецензии.
    
    Извлекает:
        - текст статьи из state.text
        - оценки по критериям из state.scores
        - объяснения оценок из state.reasons

    Генерирует:
        - черновой текст рецензии (draft_review)

    Заполняет:
        state.draft_review - текст чернового ревью
        state.agents_outputs["raw_review"] - сохранение ответа агента
    """

    async def run(self, state: State) -> State:

        response = await self.request_model(
            state,
            scores=state.scores,
            reasons=state.reasons,
        )
        data = extract_json(response)

        review = data.get("Review", response)

        state.messages.append(AIMessage(content=review, name=self.name))
        state.agents_outputs[self.name] = {
            "draft_review": review
        }

        state.draft_review = review

        return state
    
class FinalReviewAgent(BaseAgent):
    """
    Aгент, который на основе текста статьи, оценок от критериев и чернового ревью 
    пишет финальный вариант рецензии и выносит вердикт.
    
    Извлекает:
        - текст статьи из state.text
        - оценки по критериям из state.scores
        - объяснения оценок из state.reasons
        - черновой текст рецензии из state.draft_review

    Генерирует:
        - финальный текст рецензии (final_review)
        - вердикт из рецензии (verdict)

    Заполняет:
        state.final_review - текст финального ревью
        state.verdict - "accept / minor revision / major revision / reject"
        state.agents_outputs["final_review"] - сохранение ответа агента
    """

    async def run(self, state: State) -> State:

        response = await self.request_model(state, draft_review=state.draft_review)
        data = extract_json(response)

        final_review = data.get("final_review", response)
        verdict = data.get("verdict", "undecided")

        state.messages.append(
            AIMessage(content=f"{final_review}\n\nВердикт: {verdict}", name=self.name)
        )
        state.agents_outputs[self.name] = {
            "final_review": final_review,
            "verdict": verdict
        }

        state.final_review = final_review
        state.verdict = verdict

        return state
