# 🚀 Бърз Старт

## Стъпка 1: Инсталация

```bash
# Инсталирай зависимостите
pip install -r requirements.txt
```

## Стъпка 2: Анализ на данни

Първо анализирай данните за да видиш структурата им:

```bash
python agent.py examples/sample_data.csv --analyze-only
```

## Стъпка 3: Класификация

### Пример 1: Текстова класификация

Класифицирай категориите на текстове:

```bash
python agent.py examples/sample_data.csv --target category
```

Или с конкретен модел:

```bash
python agent.py examples/sample_data.csv --target category --model logistic
```

### Пример 2: Числена класификация

Предвиди одобрение на заем:

```bash
python agent.py examples/numeric_data.csv --target loan_approved
```

## Стъпка 4: Използване в Python код

```python
from classifier_agent import ClassifierAgent

# Създай агент
agent = ClassifierAgent()

# Зареди данни
agent.load_data("my_data.csv")

# Анализирай
analysis = agent.analyze_data()
agent.print_analysis(analysis)

# Класифицирай
agent.prepare_classification(target_column='my_target')
results = agent.classify()

# Предвиди нови данни
prediction = agent.predict_new_data({"feature1": "value1", "feature2": "value2"})
print(f"Предвидена класа: {prediction['predicted_class']}")
print(f"Увереност: {prediction['confidence']:.2%}")
```

## Опции на CLI

- `--target` / `-t`: Target колона за класификация
- `--features` / `-f`: Feature колони (опционално)
- `--model` / `-m`: Модел (`auto`, `random_forest`, `logistic`, `naive_bayes`)
- `--test-size`: Процент тестови данни (по подразбиране: 0.2)
- `--analyze-only`: Само анализ, без класификация

## Поддържани модели

1. **Random Forest** (по подразбиране) - Универсален, добър за повечето задачи
2. **Logistic Regression** - Бърз, добър за линейни зависимости
3. **Naive Bayes** - Ефективен за текстови данни

## Съвети

💡 Агентът автоматично:
- Открива типа на данните (текст, числа, категории)
- Препоръчва подходящи target колони
- Обработва липсващи стойности
- Нормализира данните
- Избира подходящ модел

📊 За най-добри резултати:
- Използвай поне 50-100 записа
- Балансирай класовете (приблизително равен брой от всеки клас)
- Почисти данните преди употреба

