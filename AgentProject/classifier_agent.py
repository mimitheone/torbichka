"""
AI Agent за Класификация на Данни
Интелигентен агент, който анализира и класифицира данни от файлове
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report, accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class ClassifierAgent:
    """
    Интелигентен агент за класификация на данни.
    Автоматично определя типа на данните и избира подходящ модел.
    """
    
    def __init__(self):
        self.data = None
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.vectorizer = None
        self.feature_columns = []
        self.target_column = None
        self.is_text_classification = False
        
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Зарежда данни от файл (CSV или JSON)"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файлът {file_path} не съществува")
        
        print(f"📂 Зареждам данни от: {file_path}")
        
        if file_path.suffix == '.csv':
            self.data = pd.read_csv(file_path)
        elif file_path.suffix == '.json':
            self.data = pd.read_json(file_path)
        else:
            raise ValueError("Поддържат се само CSV и JSON файлове")
        
        print(f"✅ Заредени {len(self.data)} записа с {len(self.data.columns)} колони")
        return self.data
    
    def analyze_data(self) -> Dict[str, Any]:
        """Анализира структурата и типовете данни"""
        if self.data is None:
            raise ValueError("Първо заредете данни с load_data()")
        
        print("\n🔍 Анализирам данните...")
        
        analysis = {
            'rows': len(self.data),
            'columns': list(self.data.columns),
            'dtypes': {},
            'missing_values': {},
            'unique_values': {},
            'recommendations': []
        }
        
        for col in self.data.columns:
            analysis['dtypes'][col] = str(self.data[col].dtype)
            analysis['missing_values'][col] = int(self.data[col].isna().sum())
            analysis['unique_values'][col] = int(self.data[col].nunique())
        
        # Намери потенциални target колони (с малко уникални стойности)
        potential_targets = []
        for col in self.data.columns:
            unique_ratio = self.data[col].nunique() / len(self.data)
            if 0.01 < unique_ratio < 0.3 and self.data[col].nunique() < 20:
                potential_targets.append(col)
        
        if potential_targets:
            analysis['recommendations'].append(
                f"Препоръчвам тези колони за класификация (target): {', '.join(potential_targets)}"
            )
        
        # Провери за текстови данни
        text_columns = []
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                avg_length = self.data[col].astype(str).str.len().mean()
                if avg_length > 20:  # Дълги текстове
                    text_columns.append(col)
        
        if text_columns:
            analysis['recommendations'].append(
                f"Открити текстови колони за NLP класификация: {', '.join(text_columns)}"
            )
        
        return analysis
    
    def prepare_classification(self, target_column: str, 
                              feature_columns: Optional[List[str]] = None) -> None:
        """Подготвя данните за класификация"""
        if self.data is None:
            raise ValueError("Първо заредете данни с load_data()")
        
        if target_column not in self.data.columns:
            raise ValueError(f"Колоната '{target_column}' не съществува")
        
        print(f"\n⚙️  Подготвям класификация за target: '{target_column}'")
        
        self.target_column = target_column
        
        # Ако не са зададени feature колони, използвай всички освен target
        if feature_columns is None:
            self.feature_columns = [col for col in self.data.columns 
                                   if col != target_column]
        else:
            self.feature_columns = feature_columns
        
        # Премахни редове с липсващи стойности в target
        self.data = self.data.dropna(subset=[target_column])
        
        print(f"📊 Features: {', '.join(self.feature_columns)}")
        print(f"🎯 Target: {target_column} ({self.data[target_column].nunique()} класа)")
        
        # Премахни редове с липсващи стойности във features
        rows_before = len(self.data)
        self.data = self.data.dropna(subset=self.feature_columns)
        rows_after = len(self.data)
        if rows_before != rows_after:
            print(f"⚠️  Премахнати {rows_before - rows_after} реда с липсващи стойности")
        
    def classify(self, model_type: str = 'auto', test_size: float = 0.2) -> Dict[str, Any]:
        """
        Извършва класификация на данните
        
        Args:
            model_type: 'auto', 'random_forest', 'logistic', 'naive_bayes'
            test_size: Процент на данните за тестване
        """
        if self.target_column is None:
            raise ValueError("Първо извикайте prepare_classification()")
        
        print(f"\n🤖 Стартирам класификация с модел: {model_type}")
        
        # Подготви features
        X = self.data[self.feature_columns].copy()
        y = self.data[self.target_column].copy()
        
        # Провери дали е текстова класификация
        if len(self.feature_columns) == 1 and X[self.feature_columns[0]].dtype == 'object':
            print("📝 Открита текстова класификация - използвам TF-IDF")
            self.is_text_classification = True
            self.vectorizer = TfidfVectorizer(max_features=1000)
            X = self.vectorizer.fit_transform(X[self.feature_columns[0]].astype(str))
            X = X.toarray()
        else:
            # Обработи числови и категорийни данни
            for col in self.feature_columns:
                if X[col].dtype == 'object':
                    le = LabelEncoder()
                    X[col] = le.fit_transform(X[col].astype(str))
            
            X = self.scaler.fit_transform(X)
        
        # Encode target
        y = self.label_encoder.fit_transform(y)
        
        # Split данните
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Избери модел
        if model_type == 'auto':
            model_type = 'random_forest'  # Default
        
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        elif model_type == 'logistic':
            self.model = LogisticRegression(max_iter=1000, random_state=42)
        elif model_type == 'naive_bayes':
            self.model = GaussianNB()
        else:
            raise ValueError(f"Непознат модел: {model_type}")
        
        # Тренирай модела
        print("🎓 Обучавам модела...")
        self.model.fit(X_train, y_train)
        
        # Предвиждания
        y_pred = self.model.predict(X_test)
        
        # Оценка
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(
            y_test, y_pred, 
            target_names=self.label_encoder.classes_,
            output_dict=True
        )
        
        results = {
            'model': model_type,
            'accuracy': accuracy,
            'classification_report': report,
            'classes': list(self.label_encoder.classes_),
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
        
        print(f"\n✨ Резултати:")
        print(f"   Точност: {accuracy:.2%}")
        print(f"   Класове: {', '.join(results['classes'])}")
        
        return results
    
    def predict_new_data(self, new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Прави предвиждане за нови данни"""
        if self.model is None:
            raise ValueError("Първо обучете модел с classify()")
        
        # Подготви входните данни
        if self.is_text_classification:
            X_new = self.vectorizer.transform([new_data[self.feature_columns[0]]])
            X_new = X_new.toarray()
        else:
            df_new = pd.DataFrame([new_data])
            for col in self.feature_columns:
                if df_new[col].dtype == 'object':
                    le = LabelEncoder()
                    df_new[col] = le.fit_transform(df_new[col].astype(str))
            X_new = self.scaler.transform(df_new[self.feature_columns])
        
        # Предвиди
        prediction = self.model.predict(X_new)[0]
        prediction_proba = self.model.predict_proba(X_new)[0]
        
        predicted_class = self.label_encoder.inverse_transform([prediction])[0]
        
        result = {
            'predicted_class': predicted_class,
            'confidence': float(max(prediction_proba)),
            'probabilities': {
                cls: float(prob) 
                for cls, prob in zip(self.label_encoder.classes_, prediction_proba)
            }
        }
        
        return result
    
    def print_analysis(self, analysis: Dict[str, Any]) -> None:
        """Принтира анализа на данните по четим начин"""
        print("\n" + "="*60)
        print("📊 АНАЛИЗ НА ДАННИТЕ")
        print("="*60)
        print(f"\n📈 Общо записи: {analysis['rows']}")
        print(f"📋 Колони: {len(analysis['columns'])}")
        
        print("\n🔤 Типове данни:")
        for col, dtype in analysis['dtypes'].items():
            missing = analysis['missing_values'][col]
            unique = analysis['unique_values'][col]
            print(f"   • {col}: {dtype} | {unique} уникални | {missing} липсващи")
        
        if analysis['recommendations']:
            print("\n💡 Препоръки:")
            for rec in analysis['recommendations']:
                print(f"   ✓ {rec}")
        
        print("="*60 + "\n")

