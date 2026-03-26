# агенты: критерии и рецензенты. Каждый агент - отдельный класс с методом run, который принимает state и возвращает новый state.
# BaseAgent - общий функционал, от которого наследуются все агенты. В нем можно хранить клиента, общие методы для парсинга и тд.

from abc import ABC, abstractmethod
import time
import traceback

from scientific_review.utils import extract_json, load_prompts
from scientific_review.agents.state import State

# для получения имен добавить отдельный метод с @property в BaseAgent
# используйте return self.__name__ или чета такое 


# Если используете ООП, делайте нормально. Почему BaseAgent
# Не наследуется от ABC ? Почему нет абстратных методов ? 
# Сделайте два метода, run и analyze, run - абстрактный, analyze будет запускать 
#  run и считать время работы. Также в analyze сделать обработку ошибок(try/except) чтобы 
# было понятно где агент и какой упал, а главное почему. 

# Где структура вывода ? Обязательно сделать типизацию. 
# Свой тип сделать с помощью @dataclass (им будут агенты обмениваться)

#PROMPTS нужно хранить в .yaml файлике

# Уверены что агенты должны юыть синхронные ? Реально ждать каждого будете ? 

#state какого типа ? Вам нужно создать структуру данных для state, чтобы state: State.
# State - short memory для мультиагентов. 

#ТИПИЗАЦИЯ !!!!! ДОКСТРИНГИ!!!!! ШАПКА!!!!!


class BaseAgent(ABC):
    """
    Базовый класс для всех агентов. Содержит общую логику и интерфейс.
    Все агенты должны наследоваться от этого класса и реализовывать метод run.

    Args:
        name (str): Имя агента. 
        client: Клиент для взаимодействия с LLM.
    """
    def __init__(self, name, client):
        self._name = name
        self.client = client

    @property
    def name(self) -> str:
        """Возвращает имя агента."""
        return self._name

    @abstractmethod
    async def run(self, state: State) -> State:
        """
        Метод, который должен быть реализован в каждом агенте. Принимает на вход state и возвращает новый state.
        """
        pass
    
    async def analyze(self, state: State) -> State:
        """
        Метод для запуска агента с обработкой ошибок и временем выполнения.

        Args:
            state (State): Входной state для агента.

        Returns:
            State: Новый state после выполнения агента. Если произошла ошибка, в metadata будет информация об ошибке.
        """
        start_time = time.time()
        try:
            state = await self.run(state)

        except Exception as e:
            state["metadata"][f"{self.name}_error"] = str(e)
            state["metadata"][f"{self.name}_trace"] = traceback.format_exc()
            raise

        finally:
            state["metadata"][f"{self.name}_time"] = time.time() - start_time

        return state


class NoveltyAgent(BaseAgent):
    """
    Aгент, оценивающий новизну статьи.

    Использует: 
    text из state, генерирует prompt на основе шаблона.

    Заполняет:
    state.scores['novelty'] - числовая оценка от 0 до 10
    state.novelty_agent - добавляет словарь с по
    """

    def __init__(self, client):
        super().__init__(name="novelty", client=client)

    async def run(self, state: State) -> State:

        prompt = load_prompts().get(self.name, "").replace("{text}", state.text)
        response = await self.client.generate(prompt)
        data = extract_json(response)

        score = data.get("score", -1)
        reason = data.get("reason", "")

        state.scores["novelty"] = score
        state.reasons["novelty"] = reason
        state.novelty_agent = data

        return state


class ScientificityAgent(BaseAgent):
    """Aгент, оценивающий научность статьи.

    Использует: 
    text из state, генерирует prompt на основе шаблона.
    
    Заполняет:
    state.scores['scientificity'] - числовая оценка от 0 до 10
    state.scientificity_agent - добавляет словарь с подробным разбором по
    """
    def __init__(self, client):
        super().__init__(name="scientificity", client=client)

    async def run(self, state: State) -> State:

        prompt = load_prompts().get(self.name, "").replace("{text}", state.text)
        response = await self.client.generate(prompt)
        data = extract_json(response)

        score = data.get("score", -1)
        reason = data.get("reason", "")
        state.scores["scientificity"] = score
        state.reasons["scientificity"] = reason
        state.scientificity_agent = data
        return state


class ReadabilityAgent(BaseAgent):
    """
    Aгент, оценивающий читаемость статьи.

    Использует: 
    text из state, генерирует prompt на основе шаблона.
    
    Заполняет:
    state.scores['readability'] - числовая оценка от 0 до 10
    state.readability_agent - добавляет словарь с подробным разбором по
    """
    def __init__(self, client):
        super().__init__(name="readability", client=client)

    async def run(self, state: State) -> State:
        
        prompt = load_prompts().get(self.name, "").replace("{text}", state.text)
        response = await self.client.generate(prompt)
        data = extract_json(response)

        score = data.get("score", -1)
        reason = data.get("reason", "")
        state.scores["readability"] = score
        state.reasons["readability"] = reason
        state.readability_agent = data
        return state


class ComplexityAgent(BaseAgent):
    """
    Aгент, оценивающий сложность статьи.

    Использует: 
    text из state, генерирует prompt на основе шаблона.
    
    Заполняет:
    state.scores['complexity'] - числовая оценка от 0 до 10
    state.complexity_agent - добавляет словарь с подробным разбором по
    """
    def __init__(self, client):
        super().__init__(name="complexity", client=client)

    async def run(self, state: State) -> State:

        prompt = load_prompts().get(self.name, "").replace("{text}", state.text)
        response = await self.client.generate(prompt)
        data = extract_json(response)

        score = data.get("score", -1)
        reason = data.get("reason", "")
        state.scores["complexity"] = score
        state.reasons["complexity"] = reason
        state.complexity_agent = data
        return state

class RawReviewAgent(BaseAgent):
    """
    Aгент, который на основе текста статьи и оценок от критериев пишет черновой вариант рецензии.
    
    Использует:
    text из state, state.scores, state.reasons, генерирует prompt на основе шаблона.

    Заполняет:
    state.draft_review - текст чернового ревью
    """
    def __init__(self, client):
        super().__init__(name = 'raw_review_agent', client=client)

    async def run(self, state):

        scores = {output['agent']: output['score'] for output in state.agents_outputs}
    
        reasons = {output['agent']: output['reason'] for output in state.agents_outputs}

        prompt = load_prompts().get(self.name, "").replace("{text}", state.text).replace("{scores}", str(scores)).replace("{reasons}", str(reasons))
        response = self.client.generate(prompt)
        data = extract_json(response)

        review = data.get("Review", response)

        state.draft_review = review

        return state
    
class FinalReviewAgent(BaseAgent):
    """
    Aгент, который на основе текста статьи, оценок от критериев и чернового ревью пишет финальный вариант рецензии и выносит вердикт.
    
    Использует:
    text из state, state.scores, state.reasons, state.draft_review, генерирует prompt на основе шаблона.
    
    Заполняет:
    state.final_review - текст финального ревью
    state.verdict - строка "accept", "reject" или "undecided"
    """
    def __init__(self, client):
        super().__init__(name = 'final_review_agent', client=client)

    async def run(self, state):

        prompt = load_prompts().get(self.name, "").replace("{text}", state.text).replace("{draft_review}", state.draft_review)
        response = self.client.generate(prompt)
        data = extract_json(response)

        final_review = data.get("final_review", response)
        verdict = data.get("verdict", "undecided")

        state.final_review = final_review
        state.verdict = verdict

        return state

