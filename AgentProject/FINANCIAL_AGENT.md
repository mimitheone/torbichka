# 💰 Финансов AI Агент

Интелигентен агент за автоматична класификация на финансови транзакции.

## 🎯 Какво прави?

Анализира твоите транзакции и автоматично:
- ✅ Определя дали са **приход** или **разход**
- 🏷️ Класифицира в **категории** (храна, транспорт, заплата и т.н.)
- 📊 Генерира **финансово обобщение**
- 💡 Дава **insights** за разходите ти

## 🚀 Технологии

Агентът поддържа 3 режима:

### 1. Rule-Based (по подразбиране)
Използва keywords и правила - **работи без интернет и API keys**
- ✅ Бърз и надежден
- ✅ Безплатен
- ✅ Работи offline
- ⚠️ По-ниска точност на сложни случаи

### 2. Ollama (Local LLM)
Използва локален LLM модел (например Llama 3.2)
- ✅ Много интелигентен
- ✅ Безплатен
- ✅ Работи offline
- ⚠️ Изисква инсталиран Ollama

### 3. OpenAI GPT
Използва OpenAI API
- ✅ Най-интелигентен
- ✅ Работи директно
- ⚠️ Изисква API key и интернет
- ⚠️ Платен (но евтин)

## 📦 Инсталация

```bash
# Основни зависимости (вече инсталирани)
pip install -r requirements.txt

# За Ollama (опционално)
# Инсталирай от https://ollama.ai
ollama pull llama3.2

# За OpenAI (опционално)
pip install openai
export OPENAI_API_KEY="your-key-here"
```

## 💻 Употреба

### CLI Mode

```bash
# Основна употреба (rule-based)
python finance.py transactions.csv

# С Ollama (local LLM)
python finance.py transactions.csv --llm ollama

# С OpenAI
python finance.py transactions.csv --llm openai --api-key YOUR_KEY

# Експортирай резултатите
python finance.py transactions.csv --output результати.csv

# Specify колони
python finance.py transactions.csv --description-col описание --amount-col сума
```

### Python API

```python
from financial_agent import FinancialAgent

# Създай агент
agent = FinancialAgent(llm_provider='rule-based')

# Зареди транзакциите
agent.load_transactions('transactions.csv')

# Класифицирай
results = agent.classify_transactions()

# Покажи обобщение
agent.print_summary()

# Експортирай
agent.export_results('output.csv')

# Вземи summary програмно
summary = agent.get_summary()
print(f"Баланс: {summary['balance']:.2f} лв")
```

## 📄 Формат на файла

Файлът трябва да има поне 2 колони:

### CSV пример:
```csv
date,description,amount
2024-01-15,Заплата януари,2500.00
2024-01-16,Kaufland - Пазаруване,-85.50
2024-01-17,OMV - Бензин,-70.00
2024-01-18,Фрийланс проект,450.00
```

### JSON пример:
```json
[
  {
    "date": "2024-01-15",
    "description": "Заплата януари",
    "amount": 2500.00
  },
  {
    "date": "2024-01-16",
    "description": "Kaufland - Пазаруване",
    "amount": -85.50
  }
]
```

**Важно:**
- `description` - Описание на транзакцията
- `amount` - Сума (положителна за приходи, отрицателна за разходи, или винаги положителна - агентът определя)

## 📊 Категории

### Приходи
- Заплата
- Бонус
- Freelance
- Инвестиции
- Подарък
- Възстановяване
- Друг приход

### Разходи
- Храна и напитки
- Ресторанти
- Транспорт
- Бензин
- Сметки (ток, вода, интернет)
- Наем
- Здравеопазване
- Дрехи
- Развлечения
- Покупки
- Образование
- Пътуване
- Спорт
- Подаръци
- Друг разход

## 🎯 Примери

### Пример 1: Бърза класификация

```bash
python finance.py examples/transactions.csv
```

Output:
```
📂 Зареждам транзакции от: examples/transactions.csv
✅ Заредени 7 транзакции

🤖 Стартирам класификация с RULE-BASED...
============================================================
📈 Заплата януари 2024              | 2500.00 лв | Заплата     | 85%
📉 Kaufland - Пазаруване            |  -85.50 лв | Храна       | 80%
📉 OMV - Бензин                     |  -70.00 лв | Бензин      | 80%
📈 Фрийланс проект                  |  450.00 лв | Freelance   | 85%
📉 Кафе Central                     |  -12.50 лв | Ресторанти  | 80%
📉 ЧЕЗ - Ток                        |  -45.30 лв | Сметки      | 80%
📉 Лидл - Хранителни продукти       |  -63.20 лв | Храна       | 80%
============================================================

💰 ФИНАНСОВО ОБОБЩЕНИЕ
============================================================
📊 Обща статистика:
   Общо транзакции: 7
   Средна увереност: 81.4%

📈 Приходи:
   Общо: 2950.00 лв
   • Заплата: 2500.00 лв
   • Freelance: 450.00 лв

📉 Разходи:
   Общо: 276.50 лв
   • Храна и напитки: 148.70 лв
   • Бензин: 70.00 лв
   • Сметки: 45.30 лв
   • Ресторанти: 12.50 лв

✅ Баланс: +2673.50 лв
============================================================
```

### Пример 2: С експорт

```bash
python finance.py my_bank_export.csv --output classified.csv
```

Генерира `classified.csv` с класификация за всяка транзакция.

### Пример 3: Python интеграция

```python
from financial_agent import FinancialAgent
import pandas as pd

# Зареди от банкова система
df = pd.read_excel('bank_export.xlsx')

# Преобразувай в правилния формат
df_clean = df[['Дата', 'Описание', 'Сума']].copy()
df_clean.columns = ['date', 'description', 'amount']
df_clean.to_csv('temp_transactions.csv', index=False)

# Класифицирай
agent = FinancialAgent()
agent.load_transactions('temp_transactions.csv')
agent.classify_transactions()

# Вземи статистика
summary = agent.get_summary()

# Използвай данните
print(f"Общо разходи: {summary['total_expenses']:.2f} лв")
print(f"Най-голяма категория: {max(summary['expenses_by_category'].items(), key=lambda x: x[1])}")
```

## 🎨 Advanced Features

### Custom категории

```python
agent = FinancialAgent()

# Добави свои категории
agent.expense_categories.append('Хоби')
agent.income_categories.append('Крипто')

agent.load_transactions('data.csv')
agent.classify_transactions()
```

### Филтриране по период

```python
import pandas as pd
from financial_agent import FinancialAgent

agent = FinancialAgent()
agent.load_transactions('data.csv')

# Филтрирай по дата
agent.transactions['date'] = pd.to_datetime(agent.transactions['date'])
agent.transactions = agent.transactions[agent.transactions['date'] >= '2024-01-01']

agent.classify_transactions()
agent.print_summary()
```

## 🔧 Как работи?

### Rule-Based режим:
1. Анализира keywords в описанието
2. Открива магазини, услуги, банки
3. Определя тип и категория
4. Връща confidence score

### LLM режим (Ollama/OpenAI):
1. Изпраща prompt с контекст
2. LLM анализира естествения език
3. Връща структуриран JSON
4. Fallback на rule-based ако има проблем

## 📈 Use Cases

### Лична употреба
- 📊 Автоматичен месечен отчет
- 💰 Tracking на разходи
- 🎯 Budget planning
- 📉 Намиране на излишни разходи

### Бизнес употреба
- 🏢 Категоризация на разходи
- 📁 Подготовка за счетоводство
- 📊 Финансови отчети
- 🔍 Audit и analysis

### Integration
- 🔌 Интеграция с банкови API
- 📱 Mobile app backend
- 🌐 Web dashboard
- 📧 Автоматични имейл отчети

## 🚀 Production Tips

1. **Batch processing:**
```python
import glob

agent = FinancialAgent()
for file in glob.glob('exports/*.csv'):
    agent.load_transactions(file)
    agent.classify_transactions()
    agent.export_results(f'classified/{Path(file).name}')
```

2. **Caching резултати:**
```python
import pickle

# След класификация
with open('cache.pkl', 'wb') as f:
    pickle.dump(agent.results, f)

# Load от cache
with open('cache.pkl', 'rb') as f:
    agent.results = pickle.load(f)
```

3. **Scheduled runs:**
```bash
# Cron job - всеки ден в 9:00
0 9 * * * cd /path/to/project && python finance.py new_transactions.csv
```

## 🤝 Comparison с ML Agent

| Feature | ML Agent | Financial Agent |
|---------|----------|-----------------|
| Технология | scikit-learn | LLM / Rules |
| Training | Нужни данни | Не е нужен |
| Точност | 75-100% | 80-95% |
| Setup | Complexity | Лесен |
| Use case | Generic ML | Финанси специализиран |
| Offline | ✅ | ✅ (rule-based) |

## 🎉 Заключение

Финансовият агент е **практичен, готов за production** инструмент за автоматизация на финансов анализ.

**Предимства:**
- ✅ Работи веднага без training
- ✅ Интелигентен с LLM
- ✅ Бърз с rule-based
- ✅ Практически use case
- ✅ Лесна интеграция

**Стартирай сега:**
```bash
python financial_agent.py
```

