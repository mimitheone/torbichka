# 🎉 Добре дошъл в Agent Project!

Проект с **3 различни AI агента** за класификация на данни.

## 🚀 Какво имаш?

### 1️⃣ ML Agent (Machine Learning)
**Технология:** scikit-learn  
**Use case:** Generic ML класификация, учебна цел

```bash
python demo.py  # Виж демо
python agent.py data.csv --target column_name
```

📖 **Документация:** `README.md`, `TECHNICAL.md`

---

### 2️⃣ Financial Agent (Rule-Based)
**Технология:** Keyword matching  
**Use case:** Бърза класификация на транзакции

```bash
python financial_agent.py  # Демо
python finance.py transactions.csv
```

📖 **Документация:** `FINANCIAL_AGENT.md`

---

### 3️⃣ LangChain AI Agent (LLM) 🔥 **НОВ!**
**Технология:** LangChain + Ollama/OpenAI  
**Use case:** Интелигентна, production-ready класификация

```bash
# Инсталирай зависимости
pip install langchain langchain-openai langchain-community

# Инсталирай Ollama (безплатен local LLM)
# https://ollama.ai
ollama pull llama3.2

# Стартирай
python langchain_financial_agent.py
```

📖 **Документация:** `LANGCHAIN_AGENT.md`

---

## 🎯 Кой да избера?

### Бърз отговор:

**За учене ML:** → ML Agent  
**За бърза класификация:** → Rule-Based Agent  
**За сериозен проект:** → **LangChain AI Agent** 🏆

### Детайлно сравнение:

Виж **`AGENTS_COMPARISON.md`** за пълно сравнение.

---

## 📚 Документация

### Общо
- **`START_HERE.md`** ← Този файл
- **`AGENTS_COMPARISON.md`** - Сравнение на 3-те агента
- **`OVERVIEW.md`** - Общ преглед

### ML Agent
- **`README.md`** - Главна документация
- **`QUICKSTART.md`** - Бърз старт
- **`TECHNICAL.md`** - Технически детайли
- **`PROJECT_SUMMARY.md`** - Обобщение

### Financial Agents
- **`FINANCIAL_AGENT.md`** - Rule-based документация
- **`LANGCHAIN_AGENT.md`** - LangChain AI документация

---

## 🏃 Бърз Старт

### Стъпка 1: Инсталирай зависимости

```bash
# Основни (ML + Rule-based)
pip install -r requirements.txt

# За LangChain AI (препоръчано!)
pip install langchain langchain-openai langchain-community
```

### Стъпка 2: Избери агент и стартирай

```bash
# ML Agent Demo
python demo.py

# Rule-Based Financial Agent
python financial_agent.py

# LangChain AI Agent (НАЙ-ДОБЪР!)
python langchain_financial_agent.py
```

---

## 💡 Препоръки

### За начинаещи:
1. Започни с **`python demo.py`** - виж ML в action
2. Опитай **`python financial_agent.py`** - виж финансова класификация
3. Прочети **`AGENTS_COMPARISON.md`** - разбери разликите

### За напреднали:
1. Инсталирай **Ollama**
2. Стартирай **LangChain AI Agent**
3. Интегрирай в свой проект

---

## 🌟 Highlights

### ML Agent
- ✅ 3 ML модела (Random Forest, Logistic Regression, Naive Bayes)
- ✅ Текстова (NLP) и числова класификация
- ✅ Sentiment analysis
- ✅ Пълна документация

### Rule-Based Agent
- ✅ Бърз и лесен
- ✅ Работи веднага
- ✅ Безплатен
- ✅ Offline

### LangChain AI Agent 🔥
- ✅ **Най-интелигентен**
- ✅ LLM-базиран (Ollama или OpenAI)
- ✅ Разбира контекст
- ✅ Дава reasoning
- ✅ Автоматични подкатегории
- ✅ **Production-ready**

---

## 📊 Примерни Резултати

### ML Agent
```
📝 Текстова класификация: 75% точност
🔢 Числова класификация: 100% точност
😊 Sentiment Analysis: 75% точност
```

### Rule-Based Agent
```
💰 ФИНАНСОВО ОБОБЩЕНИЕ
📈 Приходи: 2950.00 лв
📉 Разходи: 276.50 лв
✅ Баланс: +2673.50 лв
```

### LangChain AI Agent
```
🤖 AI класификация с OLLAMA (llama3.2)
📉 Kaufland София | 67.80 лв | Храна и напитки | 90%
💡 "Kaufland е верига супермаркети, типична покупка..."

📈 Freelance проект | 1200.00 лв | Freelance | 90%
💡 "Плащане за професионална услуга..."
```

---

## 🎓 Use Cases

### ML Agent
- Email класификация
- Sentiment analysis
- Категоризация на текст
- Числова класификация
- **Учебна цел**

### Financial Agents
- Лични финанси
- Бюджет tracking
- Бизнес разходи
- Месечни отчети
- Категоризация на транзакции

---

## 🔧 Структура на файловете

```
AgentProject/
│
├── 📚 ДОКУМЕНТАЦИЯ
│   ├── START_HERE.md          ← Започни тук!
│   ├── AGENTS_COMPARISON.md   ← Сравнение
│   ├── README.md              ← ML Agent docs
│   ├── FINANCIAL_AGENT.md     ← Rule-based docs
│   └── LANGCHAIN_AGENT.md     ← LangChain AI docs
│
├── 🤖 ML AGENT
│   ├── classifier_agent.py
│   ├── agent.py
│   └── demo.py
│
├── 💰 RULE-BASED FINANCIAL AGENT
│   ├── financial_agent.py
│   └── finance.py
│
├── 🔥 LANGCHAIN AI AGENT
│   └── langchain_financial_agent.py
│
├── 📊 EXAMPLES
│   └── examples/
│
└── ⚙️ CONFIG
    └── requirements.txt
```

---

## 💻 Python API Примери

### ML Agent
```python
from classifier_agent import ClassifierAgent

agent = ClassifierAgent()
agent.load_data("data.csv")
agent.prepare_classification(target_column='category')
results = agent.classify()
```

### Rule-Based Agent
```python
from financial_agent import FinancialAgent

agent = FinancialAgent(llm_provider='rule-based')
agent.load_transactions("transactions.csv")
agent.classify_transactions()
agent.print_summary()
```

### LangChain AI Agent
```python
from langchain_financial_agent import LangChainFinancialAgent

agent = LangChainFinancialAgent(
    llm_provider='ollama',
    model_name='llama3.2'
)
agent.load_transactions("transactions.csv")
agent.classify_all()
agent.print_summary()
```

---

## 🎯 Следващи Стъпки

1. **Прочети** `AGENTS_COMPARISON.md` - разбери кой агент е за теб
2. **Изпробвай** всички три агента
3. **Избери** най-подходящия за твоя проект
4. **Интегрирай** в твой workflow

---

## 🤝 Който и да избереш, имаш пълна документация!

- 📖 8+ документационни файла
- 💻 3 напълно функционални агента
- 🎯 Примерни данни и use cases
- 🚀 Production-ready код

---

## 🌟 Нашата Препоръка

За нови проекти използвай **LangChain AI Agent**:
- 🤖 Най-модерна технология
- 🎯 Най-точен
- 💡 Дава reasoning
- 🆓 Безплатен (с Ollama)
- 🚀 Production-ready

```bash
# Инсталирай Ollama
ollama pull llama3.2

# Стартирай агента
python langchain_financial_agent.py
```

---

## ❓ Въпроси?

- За **ML Agent** → виж `README.md`
- За **Rule-Based** → виж `FINANCIAL_AGENT.md`
- За **LangChain AI** → виж `LANGCHAIN_AGENT.md`
- За **Сравнение** → виж `AGENTS_COMPARISON.md`

---

## 🎉 Започни!

```bash
# Изпробвай всички агенти
python demo.py                        # ML Agent
python financial_agent.py             # Rule-Based
python langchain_financial_agent.py   # LangChain AI (препоръчан!)
```

**Enjoy coding!** 🚀

