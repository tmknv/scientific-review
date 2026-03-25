# Scientific Review - Автоматическое рецензирование научных статей

Проект для сравнительного анализа мультиагентной системы и большой языковой модели в задаче автоматического рецензирования научных текстов.

## Реализованный код

### Основные модули (`scientific_review/`)
- **config.py** - загрузка переменных окружения и конфигурации из `prompts.yaml`
- **client.py** - унифицированный клиент для работы с OpenRouter API 
- **utils.py** - утилиты: работа с JSON, сохранение файлов, расчёт оценок

### Мультиагентная система (`scientific_review/agents/`)
- **criteria_agents.py** - четыре агента для оценки критериев: NoveltyAgent, ScientificityAgent, ReadabilityAgent, ComplexityAgent
- **review_agents.py** - агенты для составления рецензии: RawReviewAgent и FinalReviewAgent
- **multiagent_pipeline.py** - оркестрация работы всех агентов в последовательный pipeline
- **state.py** - общее состояние для обмена данными между агентами (текст, оценки, рецензии)
- **tools.py** - расширяемый модуль для инструментов агентов (например, поиск для NoveltyAgent)

### Базовый подход (`scientific_review/baseline/`)
- **baseline_pipeline.py** - простой baseline: один вызов монолитной LLM для оценки и рецензии

### Скрипты запуска (`scripts/`)
- **run_baseline.py** - запуск baseline pipeline с примером использования
- **run_multiagent.py** - запуск multiagent pipeline с примером использования
### 3. Запустить pipeline

#### Запуск baseline подхода:
```bash
poetry run python scripts/run_baseline.py
```

#### Запуск мультиагентного подхода:
```bash
poetry run python scripts/run_multiagent.py
```

## Результаты

Результаты экспериментов сохраняются в JSON формате:
- результаты baseline сохраняются в `runs/baseline/`
- результаты multi-agent сохраняются в `runs/multiagent/`

Каждый результат содержит:
- **scores** - числовые оценки по различным критериям
- **review** - текст рецензии
- **verdict** - вердикт (accept/reject/minor/major revisions)
- **agents_outputs** - детальные выходы каждого агента

## Вывод в терминал

При запуске скриптов в терминал выводится:

### Для Baseline Pipeline:
```
{
  "scores": {
    "novelty": 9,
    "scientificity": 6,
    "readability": 8,
    "complexity": 5
    "final_score": 7
  },
  "review": "Детальный текст рецензии...",
  "verdict": "accept"
  "raw_output": " ... "
}
Saved to: runs/baseline/20260325_120543_123456.json
```

### Для Multi-Agent Pipeline:
```
{
  "text": " ... "
  "scores": {
    "novelty": 9,
    "scientificity": 6,
    "readability": 8,
    "complexity": 5
    "final_score": 7
  },
  "draft_review": " ... "
  "final_review": "Детальный текст рецензии от агентов...",
  "verdict": "accept",
  "agents_outputs": [...]
  }
  "metadata": {...}
}
Saved to: runs/multiagent/20260325_120543_654321.json
```

## Реализованный код

### Основные модули (`scientific_review/`)
- **config.py** - загрузка переменных окружения и конфигурации из `prompts.yaml`
- **client.py** - унифицированный клиент для работы с OpenRouter API 
- **utils.py** - утилиты: работа с JSON, сохранение файлов, расчёт оценок

### Мультиагентная система (`scientific_review/agents/`)
- **criteria_agents.py** - четыре агента для оценки критериев: NoveltyAgent, ScientificityAgent, ReadabilityAgent, ComplexityAgent
- **review_agents.py** - агенты для составления рецензии: RawReviewAgent и FinalReviewAgent
- **multiagent_pipeline.py** - оркестрация работы всех агентов в последовательный pipeline
- **state.py** - общее состояние для обмена данными между агентами (текст, оценки, рецензии)
- **tools.py** - расширяемый модуль для инструментов агентов

### Базовый подход (`scientific_review/baseline/`)
- **baseline_pipeline.py** - простой baseline: однозвездный вызов LLM для оценки и рецензии

### Скрипты запуска (`scripts/`)
- **run_baseline.py** - запуск baseline pipeline с примером использования
- **run_multiagent.py** - запуск мультиагентного pipeline с примером использования
