# 🔧 Технически Детайли

## Архитектура

AI Agent за класификация използва модулна архитектура с ясно разделение на отговорности:

```
┌─────────────────────────────────────────────────────┐
│                   CLI / API Layer                   │
│                (agent.py / Python API)              │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              ClassifierAgent (ядро)                 │
│  • Data Loading & Analysis                          │
│  • Feature Engineering                              │
│  • Model Selection & Training                       │
│  • Prediction & Evaluation                          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│           scikit-learn ML Models                    │
│  Random Forest | Logistic Regression | Naive Bayes │
└─────────────────────────────────────────────────────┘
```

## Как работи агентът

### 1. Data Loading (Зареждане на данни)

```python
def load_data(self, file_path: str) -> pd.DataFrame:
    # Автоматично разпознава формата (CSV/JSON)
    # Зарежда данните в pandas DataFrame
    # Връща метаданни за размер и структура
```

**Поддържани формати:**
- CSV (comma-separated values)
- JSON (JavaScript Object Notation)

### 2. Data Analysis (Анализ на данни)

```python
def analyze_data(self) -> Dict[str, Any]:
    # Определя типовете на колоните
    # Брои уникални стойности
    # Намира липсващи стойности
    # Генерира интелигентни препоръки
```

**Анализирани характеристики:**
- Тип на данните (numeric, text, categorical)
- Брой уникални стойности
- Липсващи стойности (NaN)
- Потенциални target колони
- Текстови колони (за NLP)

### 3. Data Preparation (Подготовка на данни)

```python
def prepare_classification(self, target_column, feature_columns):
    # Разделя данните на features (X) и target (y)
    # Премахва редове с липсващи стойности
    # Подготвя pipeline за обработка
```

**Feature Engineering:**

За **текстови данни**:
```python
# TF-IDF Vectorization
TfidfVectorizer(max_features=1000)
# Преобразува текст в числови вектори
```

За **категорийни данни**:
```python
# Label Encoding
LabelEncoder()
# Преобразува категории в числа (0, 1, 2, ...)
```

За **числови данни**:
```python
# Standardization
StandardScaler()
# Нормализира данните: (x - mean) / std
```

### 4. Model Training (Обучение на модел)

```python
def classify(self, model_type='auto', test_size=0.2):
    # Split данните (train/test)
    # Избира подходящ модел
    # Тренира модела
    # Оценява точността
    # Връща детайлни метрики
```

**Train/Test Split:**
```python
train_test_split(X, y, test_size=0.2, stratify=y)
# 80% train, 20% test
# Stratified - запазва пропорциите на класовете
```

### 5. Model Evaluation (Оценка на модела)

**Метрики:**

1. **Accuracy** (Точност)
   ```
   accuracy = (TP + TN) / (TP + TN + FP + FN)
   ```

2. **Precision** (Прецизност)
   ```
   precision = TP / (TP + FP)
   ```

3. **Recall** (Пълнота)
   ```
   recall = TP / (TP + FN)
   ```

4. **F1-Score** (Хармонична средна)
   ```
   F1 = 2 * (precision * recall) / (precision + recall)
   ```

Където:
- TP = True Positives
- TN = True Negatives
- FP = False Positives
- FN = False Negatives

### 6. Prediction (Предвиждане)

```python
def predict_new_data(self, new_data):
    # Обработва новите данни по същия начин
    # Прави предвиждане
    # Връща клас и вероятности
```

## ML Модели в детайли

### Random Forest Classifier

```python
RandomForestClassifier(n_estimators=100, random_state=42)
```

**Как работи:**
1. Създава 100 decision trees
2. Всяко дърво тренира на random subset от данните
3. При предвиждане - всяко дърво "гласува"
4. Избира се класът с най-много гласове

**Предимства:**
- Висока точност
- Устойчив на overfitting
- Работи добре с различни типове данни
- Може да обработи нелинейни зависимости

**Недостатъци:**
- По-бавен от логистична регресия
- По-труден за интерпретация

### Logistic Regression

```python
LogisticRegression(max_iter=1000, random_state=42)
```

**Как работи:**
1. Изчислява линейна комбинация от features
2. Прилага sigmoid функция
3. Получава вероятности между 0 и 1
4. Класифицира базирано на threshold (обикновено 0.5)

**Формула:**
```
P(y=1) = 1 / (1 + e^-(w0 + w1*x1 + w2*x2 + ... + wn*xn))
```

**Предимства:**
- Бърз и ефективен
- Лесен за интерпретация
- Работи добре с линейни зависимости
- Малко параметри

**Недостатъци:**
- Само линейни границі между класове
- Може да underfit на сложни данни

### Naive Bayes

```python
GaussianNB()
```

**Как работи:**
1. Използва Bayes' theorem
2. Предполага независимост на features (naive assumption)
3. Изчислява вероятности за всеки клас
4. Избира класа с най-висока вероятност

**Формула:**
```
P(class|features) = P(features|class) * P(class) / P(features)
```

**Предимства:**
- Много бърз
- Добър за текстови данни
- Изисква малко training data
- Работи добре с високодименсионални данни

**Недостатъци:**
- Naive assumption не винаги е вярна
- По-ниска точност на сложни задачи

## Pipeline Flow

```
1. Load Data
   ↓
2. Analyze Structure
   ↓
3. Select Target & Features
   ↓
4. Data Preprocessing
   ├── Text → TF-IDF Vectorization
   ├── Categorical → Label Encoding
   └── Numeric → Standardization
   ↓
5. Split Train/Test
   ↓
6. Select Model
   ↓
7. Train Model
   ↓
8. Evaluate
   ↓
9. Make Predictions
```

## Обработка на данни

### Текстови данни

```python
# Input
text = "Този продукт е страхотен!"

# TF-IDF
vectorizer.fit_transform([text])
# Output: [0.0, 0.32, 0.0, 0.87, ..., 0.15]
# 1000-dimensional vector
```

### Категорийни данни

```python
# Input
categories = ["red", "blue", "red", "green"]

# Label Encoding
encoder.fit_transform(categories)
# Output: [2, 0, 2, 1]
```

### Числови данни

```python
# Input
values = [100, 200, 150]

# Standardization
scaler.fit_transform(values)
# Output: [-1.22, 1.22, 0.0]
# Mean=0, Std=1
```

## Оптимизация и Best Practices

### Memory Efficiency

- Използва pandas за ефективна работа с данни
- TF-IDF ограничен на 1000 features
- Lazy evaluation където е възможно

### Speed

- Vectorized операции с numpy
- Паралелизация в Random Forest
- Ефективно splitting с stratification

### Accuracy

- Stratified train/test split
- Cross-validation в бъдещи версии
- Feature scaling за stability

## Разширяване на функционалност

### Добавяне на нов модел

```python
# В classifier_agent.py, метод classify()

elif model_type == 'svm':
    from sklearn.svm import SVC
    self.model = SVC(kernel='rbf', probability=True)
```

### Добавяне на нов формат за данни

```python
# В classifier_agent.py, метод load_data()

elif file_path.suffix == '.xlsx':
    self.data = pd.read_excel(file_path)
```

### Добавяне на feature engineering

```python
# Преди model.fit()

if feature_type == 'polynomial':
    from sklearn.preprocessing import PolynomialFeatures
    poly = PolynomialFeatures(degree=2)
    X_train = poly.fit_transform(X_train)
```

## Performance Tips

1. **За големи datasets** (>100K rows):
   - Използвай sampling за бърза итерация
   - Ограничи TF-IDF features
   - Използвай по-прости модели първо

2. **За малки datasets** (<100 rows):
   - Намали test_size (10-15%)
   - Използвай cross-validation
   - Опитай Naive Bayes

3. **За text data**:
   - Увеличи max_features в TF-IDF
   - Добави n-grams
   - Премахни stop words

4. **За imbalanced classes**:
   - Използвай class_weight='balanced'
   - SMOTE за oversampling
   - Undersample majority class

## Dependencies версии

```
pandas>=2.0.0    - DataFrame операции
sklearn>=1.3.0   - ML модели и preprocessing
numpy>=1.24.0    - Числени операции
colorama>=0.4.6  - Terminal coloring
```

## Бъдещи подобрения

- [ ] Cross-validation за по-надеждна оценка
- [ ] Grid search за hyperparameter tuning
- [ ] Feature importance visualization
- [ ] Confusion matrix visualization
- [ ] ROC curves и AUC scores
- [ ] Support за multi-label classification
- [ ] Deep learning модели (опционално)
- [ ] API endpoint (Flask/FastAPI)
- [ ] Model persistence (save/load)
- [ ] Batch predictions

## Ресурси за учене

- [scikit-learn Documentation](https://scikit-learn.org/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [Machine Learning Crash Course](https://developers.google.com/machine-learning/crash-course)
- [Python Data Science Handbook](https://jakevdp.github.io/PythonDataScienceHandbook/)

