# 🤖 AI Agent за Класификация на Данни

Елементарен, но мощен проект с AI агент, който класифицира данни от файлове.

## ✨ Възможности

- 📁 **Приема CSV и JSON файлове** - Гъвкаво зареждане на данни
- 🤖 **Автоматично анализира структурата** - Интелигентно разпознаване на типове данни
- 🎯 **Класифицира данни** - Текстови, числови и категорийни данни
- 📊 **Множество ML модели** - Random Forest, Logistic Regression, Naive Bayes
- 🔍 **Интелигентни препоръки** - Автоматично предлага подходящи колони за класификация
- 💡 **NLP поддръжка** - Текстова класификация с TF-IDF
- 📈 **Детайлни метрики** - Precision, Recall, F1-Score, Accuracy

## 🚀 Бърз Старт

### 1. Инсталация

```bash
pip install -r requirements.txt
```

### 2. Стартирай demo

```bash
python demo.py
```

Това ще покаже всички възможности на агента с готови примери!

### 3. Използвай с твои данни

```bash
# Анализ на данни
python agent.py your_data.csv --analyze-only

# Класификация
python agent.py your_data.csv --target column_name
```

## 📖 Употреба

### CLI Mode

```bash
# Основна употреба
python agent.py data.csv --target column_name

# С конкретен модел
python agent.py data.csv --target category --model random_forest

# С конкретни features
python agent.py data.csv --target category --features text description

# Само анализ
python agent.py data.csv --analyze-only
```

### Python API

```python
from classifier_agent import ClassifierAgent

# Създай агент
agent = ClassifierAgent()

# Зареди данни
agent.load_data("data.csv")

# Анализирай данните
analysis = agent.analyze_data()
agent.print_analysis(analysis)

# Подготви класификация
agent.prepare_classification(
    target_column='category',
    feature_columns=['text', 'description']
)

# Класифицирай
results = agent.classify(model_type='random_forest')
print(f"Точност: {results['accuracy']:.2%}")

# Предвиди нови данни
prediction = agent.predict_new_data({
    'text': 'Нов текст за класификация',
    'description': 'Допълнително описание'
})
print(f"Предвидена класа: {prediction['predicted_class']}")
print(f"Увереност: {prediction['confidence']:.2%}")
```

## 📚 Примери

Проектът включва готови примери:

### 1. Текстова класификация (NLP)
```bash
python agent.py examples/sample_data.csv --target category
```
Класифицира текстове в категории (product_review, delivery, customer_service)

### 2. Числова класификация
```bash
python agent.py examples/numeric_data.csv --target loan_approved
```
Предвижда одобрение на заем базирано на възраст, доход и кредитен рейтинг

### 3. Sentiment Analysis
```bash
python agent.py examples/sample_data.csv --target sentiment
```
Анализира sentiment (positive/negative) на текстове

### 4. Използване в Python
```bash
python examples/usage_example.py
```

## 🏗️ Структура на проекта

```
AgentProject/
├── agent.py                    # Главен CLI интерфейс
├── classifier_agent.py         # AI Agent клас (ядро)
├── demo.py                     # Пълно демо на възможностите
├── requirements.txt            # Python зависимости
├── README.md                   # Този файл
├── QUICKSTART.md               # Бърз старт гайд
├── .gitignore                  # Git ignore правила
└── examples/                   # Примерни данни и скриптове
    ├── sample_data.csv         # Текстови данни за класификация
    ├── numeric_data.csv        # Числови данни за класификация
    └── usage_example.py        # Пример за Python API
```

## 🧠 ML Модели

Агентът поддържа 3 типа модели:

1. **Random Forest** (по подразбиране)
   - Универсален и точен
   - Добре работи с различни типове данни
   - Устойчив на overfitting

2. **Logistic Regression**
   - Бърз и ефективен
   - Добър за линейни зависимости
   - Лесен за интерпретация

3. **Naive Bayes**
   - Много бърз
   - Отличен за текстови данни
   - Изисква по-малко данни за обучение

## 🎯 Use Cases

- 📧 **Email класификация** - Spam detection, категоризация
- 📝 **Sentiment analysis** - Анализ на отзиви, коментари
- 🏦 **Финансови предвиждания** - Одобрение на заеми, риск оценка
- 🛍️ **E-commerce** - Категоризация на продукти
- 📞 **Customer support** - Автоматично рутиране на запитвания
- 📰 **Новини** - Категоризация на статии

## 📊 Метрики и оценка

Агентът предоставя детайлни метрики:

- **Accuracy** - Обща точност на модела
- **Precision** - Точност по класове
- **Recall** - Пълнота на откриване
- **F1-Score** - Балансирана метрика
- **Confusion Matrix** - Детайлен анализ на грешки

## 🔧 Технологии

- **Python 3.7+**
- **pandas** - Обработка на данни
- **scikit-learn** - Machine Learning модели
- **numpy** - Числени операции
- **colorama** - Цветен terminal output

## 💡 Съвети за най-добри резултати

1. **Качество на данните** - Почиствай данните преди употреба
2. **Достатъчно данни** - Минимум 50-100 записа, препоръчително 500+
3. **Балансирани класове** - Равномерно разпределение на класовете
4. **Релевантни features** - Избирай смислени колони
5. **Експериментирай с модели** - Пробвай различни модели за най-добри резултати

## 🤝 Как да допринесеш

Проектът е отворен за подобрения:

1. Добави нови ML модели
2. Подобри обработката на данни
3. Добави визуализации
4. Разшири документацията
5. Създай нови примери

## 📄 Лиценз

Свободен за използване в образователни и комерсиални цели.

## 🎓 За начинаещи

Това е отличен проект за:
- Учене на Machine Learning
- Разбиране на класификация
- Експериментиране с различни модели
- Практика с Python и scikit-learn

Виж `QUICKSTART.md` за детайлно ръководство!

