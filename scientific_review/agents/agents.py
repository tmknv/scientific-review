# агенты-оценщики: novelty, scientificity, readability, complexity

from abc import ABC, abstractmethod
import time

from scientific_review.client import Client
from scientific_review.utils import extract_json, load_prompts

# для получения имен добавить отдельный метод с @property в BaseAgent
# используйте return self.__name__ или чета такое 

# Нужно ли self.client = Client() в конструктор совать ? 

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
    """
    def __init__(self, name):
        self.name = name
        self.client = Client()

    @abstractmethod
    def run(self, state):
        """
        Метод, который должен быть реализован в каждом агенте. Принимает на вход state и возвращает новый state.
        """
        ...
        raise NotImplementedError("Метод run должен быть реализован в наследниках")
    
    def analyze(self, state):
        """
        Метод для запуска агента с обработкой ошибок и временем выполнения.
        """
        start_time = time.time()
        try:
            new_state = self.run(state)
            end_time = time.time()
            print(f"{self.name} завершен за {end_time - start_time:.2f} секунд")
            return new_state
        except Exception as e:
            end_time = time.time()
            print(f"{self.name} завершен за {end_time - start_time:.2f} секунд с ошибкой: {e}")
            return state

    
# class BaseAgent(ABC):
#     def __init__(self, name):
#         self.name = name
#         self.client = Client()

#     @abstractmethod
#     def run(self, state):
#         prompt = PROMPTS[self.name].format(text=state.text)

#         response = self.client.generate(prompt)
#         data = extract_json(response)

#         score = data.get("score", -1)
#         reason = data.get("reason", response)

#         state.scores[self.name] = score

#         state.agents_outputs.append({
#             "agent": self.name,
#             "raw_output": response,
#             "score": score,
#             "reason": reason
#         })

#         return state


class NoveltyAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="novelty")


class ScientificityAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="scientificity")


class ReadabilityAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="readability")


class ComplexityAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="complexity")

class RawReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__(name = 'raw_review_agent')

    def run(self, state):

        scores = {output['agent']: output['score'] for output in state.agents_outputs}
    
        reasons = {output['agent']: output['reason'] for output in state.agents_outputs}

        prompt = load_prompts().get(self.name, "").format(text=state.text, scores=scores, reasons=reasons)
        response = self.client.generate(prompt)
        data = extract_json(response)

        review = data.get("Review", response)

        state.draft_review = review

        return state
    
class FinalReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__(name = 'final_review_agent')

    def run(self, state):

        prompt = load_prompts().get(self.name, "").format(text=state.text, draft_review=state.draft_review)
        response = self.client.generate(prompt)
        data = extract_json(response)

        final_review = data.get("final_review", response)
        verdict = data.get("verdict", "undecided")

        state.final_review = final_review
        state.verdict = verdict

        return state

