# Scientific Review - Автоматическое рецензирование научных статей

Проект для сравнительного анализа мультиагентной системы и большой языковой модели в задаче автоматического рецензирования научных текстов.

## Реализованный код

### Основные модули (`scientific_review/`)
- **config.py** - Загрузка переменных окружения и конфигурации из `prompts.yaml`
- **client.py** - Унифицированный клиент для работы с OpenRouter API 
- **utils.py** - Утилиты: работа с JSON, сохранение файлов, расчёт оценок

### Мультиагентная система (`scientific_review/agents/`)
- **criteria_agents.py** - Четыре агента для оценки критериев: NoveltyAgent, ScientificityAgent, ReadabilityAgent, ComplexityAgent
- **review_agents.py** - Агенты для составления рецензии: RawReviewAgent и FinalReviewAgent
- **multiagent_pipeline.py** - Оркестрация работы всех агентов в последовательный pipeline
- **state.py** - Общее состояние для обмена данными между агентами (текст, оценки, рецензии)
- **tools.py** - Расширяемый модуль для инструментов агентов

### Базовый подход (`scientific_review/baseline/`)
- **baseline_pipeline.py** - Простой baseline: однозвездный вызов LLM для оценки и рецензии

### Скрипты запуска (`scripts/`)
- **run_baseline.py** - Запуск baseline pipeline с примером использования
- **run_multiagent.py** - Запуск мультиагентного pipeline с примером использования
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
- Результаты baseline сохраняются в `runs/baseline/`
- Результаты multi-agent сохраняются в `runs/multiagent/`

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
    "relevance": 0.85,
    "novelty": 0.78,
    ...
  },
  "review": "Детальный текст рецензии...",
  "verdict": "accept"
}
Saved to: runs/baseline/20260325_120543_123456.json
```

### Для Multi-Agent Pipeline:
```
{
  "scores": {
    "relevance": 0.85,
    "novelty": 0.78,
    ...
  },
  "review": "Детальный текст рецензии от агентов...",
  "verdict": "accept",
  "agents_outputs": {
    "relevance_agent": {...},
    "methodology_agent": {...},
    ...
  }
}
Saved to: runs/multiagent/20260325_120543_654321.json
```

## Реализованный код

### Основные модули (`scientific_review/`)
- **config.py** - Загрузка переменных окружения и конфигурации из `prompts.yaml`
- **client.py** - Унифицированный клиент для работы с OpenRouter API 
- **utils.py** - Утилиты: работа с JSON, сохранение файлов, расчёт оценок

### Мультиагентная система (`scientific_review/agents/`)
- **criteria_agents.py** - Четыре агента для оценки критериев: NoveltyAgent, ScientificityAgent, ReadabilityAgent, ComplexityAgent
- **review_agents.py** - Агенты для составления рецензии: RawReviewAgent и FinalReviewAgent
- **multiagent_pipeline.py** - Оркестрация работы всех агентов в последовательный pipeline
- **state.py** - Общее состояние для обмена данными между агентами (текст, оценки, рецензии)
- **tools.py** - Расширяемый модуль для инструментов агентов

### Базовый подход (`scientific_review/baseline/`)
- **baseline_pipeline.py** - Простой baseline: однозвездный вызов LLM для оценки и рецензии

### Скрипты запуска (`scripts/`)
- **run_baseline.py** - Запуск baseline pipeline с примером использования
- **run_multiagent.py** - Запуск мультиагентного pipeline с примером использования
