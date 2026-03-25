# агенты-оценщики: novelty, scientificity, readability, complexity

from scientific_review.client import Client
from scientific_review.utils import extract_json
from scientific_review.config import PROMPTS

# для получения имен добавить отдельный метод с @property в BaseCriteriaAgent
# используйте return self.__name__ или чета такое 

# Нужно ли self.client = Client() в конструктор совать ? 

# Если используете ООП, делайте нормально. Почему BaseCriteriaAgent
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

class BaseCriteriaAgent:
    def __init__(self, name):
        self.name = name
        self.client = Client()

    def run(self, state):
        prompt = PROMPTS[self.name].format(text=state.text)

        response = self.client.generate(prompt)
        data = extract_json(response)

        score = data.get("score", -1)
        reason = data.get("reason", response)

        state.scores[self.name] = score

        state.agents_outputs.append({
            "agent": self.name,
            "raw_output": response,
            "score": score,
            "reason": reason
        })

        return state


class NoveltyAgent(BaseCriteriaAgent):
    def __init__(self):
        super().__init__(name="novelty")


class ScientificityAgent(BaseCriteriaAgent):
    def __init__(self):
        super().__init__(name="scientificity")


class ReadabilityAgent(BaseCriteriaAgent):
    def __init__(self):
        super().__init__(name="readability")


class ComplexityAgent(BaseCriteriaAgent):
    def __init__(self):
        super().__init__(name="complexity")
