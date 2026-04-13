# Scientific Review: Multi-Agent vs LLM

Сравнительный анализ мультиагентной системы (на базе SLM) и одиночной LLM  
в задаче автоматического рецензирования научных текстов.

## Описание проекта

В проекте реализованы два подхода к автоматическому рецензированию научных статей:

### Baseline (LLM)
- Один запрос к большой языковой модели.
- Результат содержит:
  - оценки по всем критериям,
  - итоговый score,
  - полный review и verdict.

### Multi-Agent (SLM)
- Набор специализированных агентов:
  - `NoveltyAgent`
  - `ScientificityAgent`
  - `ReadabilityAgent`
  - `ComplexityAgent`
- Генерация рецензии выполняется в два этапа:
  - `RawReviewAgent`
  - `FinalReviewAgent`

Декомпозиция задачи на специализированные агенты обеспечивает более управляемое, стабильное и объяснимое поведение системы.


## Гипотеза

Мультиагентная система на базе SLM:
- обеспечивает более стабильные результаты,
- выдает оценки более близкие к экспертным (human) оценкам,
- обладает более прозрачной и интерпретируемой структурой оценки.


## Архитектура

### Multi-Agent Pipeline

```
├── NoveltyAgent
├── ScientificityAgent
├── ReadabilityAgent
└── ComplexityAgent
         ↓
   RawReviewAgent
         ↓
   FinalReviewAgent
         ↓
   Final State (scores + review + verdict)
```


## Критерии оценки

- **Novelty** – новизна исследования
- **Scientificity** – научная обоснованность
- **Readability** – читаемость и ясность изложения
- **Complexity** – уровень сложности материала


## Эксперименты

### E1: Quality
Сравнение baseline и multi-agent на полном датасете.  
Метрики: MAE (Mean Absolute Error) по отношению к human labels, LLM-as-a-Judge для оценки ревью.

### E2: Stability
15 независимых прогонов одной и той же статьи.  
Измеряется inter-run variance результатов baseline и multi-agent.

### E3: Ablation Study
Отключение отдельных агентов и проверка деградации качества.
Для каждой конфигурации (1 агент, 2 агента, 3 агента, 4 агента = full) генерируется review через multi-agent pipeline.  
Каждый multi-agent review сравнивается с baseline review с помощью LLM-as-a-Judge.  
Рассчитывается **Win Rate** – доля случаев, где LLM-as-a-Judge выбрал multi-agent review лучше baseline.
Анализируется зависимость:  
- X – количество агентов (1, 2, 3, 4)  
- Y – средний win-rate по конфигурациям с данным числом агентов  


## Метрики

1. **MAE (Mean Absolute Error)** – среднее арифметическое отклонение оценок модели от оценок экспертов.
2. **LLM-as-a-Judge** – одна языковая модель проверяет и оценивает ответы другой модели по заданным критериям (сравнение ревью baseline и multi-agent).
3. **Inter-run Variance** – межпрогонная дисперсия, разброс результатов при многократных запусках на одних и тех же данных.


## Запуск экспериментов

```
# E1: Quality
poetry run python scripts/run_quality.py

# E2: Stability
poetry run python scripts/run_stability.py

# E3: Ablation
poetry run python scripts/run_ablation.py
```

Результаты сохраняются в папку `runs/`:
- `runs/quality`
- `runs/stability`
- `runs/ablation`

## Запуск pipeline

```
# Запуск baseline pipeline:
poetry run python scripts/run_baseline.py

# Запуск multi-agent pipeline:
poetry run python scripts/run_multiagent.py
```

Результаты сохраняются в папку `runs/`:
- `runs/baseline`
- `runs/multiagent`


## Ключевые особенности

- Асинхронная обработка (`asyncio`)
- Параллельный запуск агентов
- Оркестрация через LangGraph
- JSON-артефакты всех результатов для воспроизводимости исследований


## Основные результаты

- Multi-agent система превосходит baseline по MAE (качество оценок) и LLM-as-a-Judge (качество ревью).
- Multi-agent система демонстрирует существенно меньшую межпрогонную дисперсию (выше стабильность).
- Win Rate растет с увеличением количества агентов; разбиение задачи даёт значительный прирост качества.
