#!/usr/bin/env python3
"""
Финансов AI Агент за класификация на транзакции
Използва LLM (OpenAI или Ollama) за интелигентна категоризация
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import os


class FinancialAgent:
    """
    Интелигентен агент за анализ на финансови транзакции.
    Автоматично класифицира приходи/разходи и определя категории.
    """
    
    def __init__(self, llm_provider: str = 'ollama', api_key: Optional[str] = None):
        """
        Args:
            llm_provider: 'openai' или 'ollama'
            api_key: API key за OpenAI (ако използваш OpenAI)
        """
        self.llm_provider = llm_provider
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.transactions = None
        self.results = []
        
        # Стандартни категории
        self.income_categories = [
            'Заплата', 'Бонус', 'Freelance', 'Инвестиции', 
            'Подарък', 'Възстановяване', 'Друг приход'
        ]
        
        self.expense_categories = [
            'Храна и напитки', 'Ресторанти', 'Транспорт', 
            'Бензин', 'Сметки', 'Наем', 'Здравеопазване',
            'Дрехи', 'Развлечения', 'Покупки', 'Образование',
            'Пътуване', 'Спорт', 'Подаръци', 'Друг разход'
        ]
        
    def load_transactions(self, file_path: str) -> pd.DataFrame:
        """Зарежда транзакции от файл"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файлът {file_path} не съществува")
        
        print(f"📂 Зареждам транзакции от: {file_path}")
        
        if file_path.suffix == '.csv':
            self.transactions = pd.read_csv(file_path)
        elif file_path.suffix == '.json':
            self.transactions = pd.read_json(file_path)
        else:
            raise ValueError("Поддържат се само CSV и JSON файлове")
        
        print(f"✅ Заредени {len(self.transactions)} транзакции")
        return self.transactions
    
    def _classify_with_ollama(self, description: str, amount: float) -> Dict[str, Any]:
        """Класифицира транзакция с Ollama (local LLM)"""
        try:
            import requests
            
            prompt = f"""Анализирай следната финансова транзакция и върни JSON с класификация.

Транзакция: {description}
Сума: {amount} лв

Определи:
1. type: "приход" или "разход"
2. category: избери най-подходящата категория
3. confidence: увереност (0.0-1.0)
4. reasoning: кратко обяснение

Категории за приходи: {', '.join(self.income_categories)}
Категории за разходи: {', '.join(self.expense_categories)}

Отговори само с валиден JSON в следния формат:
{{
    "type": "приход" или "разход",
    "category": "категория",
    "confidence": 0.95,
    "reasoning": "обяснение"
}}"""

            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama3.2',  # или друг модел
                    'prompt': prompt,
                    'stream': False,
                    'format': 'json'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return json.loads(result['response'])
            else:
                # Fallback на rule-based
                return self._classify_rule_based(description, amount)
                
        except Exception as e:
            print(f"⚠️  Ollama грешка: {e}. Използвам rule-based класификация.")
            return self._classify_rule_based(description, amount)
    
    def _classify_with_openai(self, description: str, amount: float) -> Dict[str, Any]:
        """Класифицира транзакция с OpenAI GPT"""
        try:
            import openai
            
            if not self.api_key:
                raise ValueError("Не е зададен OPENAI_API_KEY")
            
            openai.api_key = self.api_key
            
            prompt = f"""Анализирай следната финансова транзакция:

Описание: {description}
Сума: {amount} лв

Определи:
1. Тип: "приход" или "разход"
2. Категория от списъка:
   - Приходи: {', '.join(self.income_categories)}
   - Разходи: {', '.join(self.expense_categories)}
3. Увереност (0.0-1.0)
4. Кратко обяснение

Отговори с JSON:
{{
    "type": "приход/разход",
    "category": "категория",
    "confidence": 0.95,
    "reasoning": "обяснение"
}}"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ти си финансов експерт, който класифицира транзакции."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"⚠️  OpenAI грешка: {e}. Използвам rule-based класификация.")
            return self._classify_rule_based(description, amount)
    
    def _classify_rule_based(self, description: str, amount: float) -> Dict[str, Any]:
        """Fallback: rule-based класификация без LLM"""
        desc_lower = description.lower()
        
        # Ако сумата е положителна, вероятно е приход
        is_positive_amount = amount > 0
        
        # Keywords за приходи
        income_keywords = ['заплата', 'salary', 'бонус', 'bonus', 'freelance', 
                          'получ', 'receive', 'превод от', 'transfer from', 'доход', 'income']
        
        # Keywords за разходи по категории
        expense_rules = {
            'Храна и напитки': ['kaufland', 'lidl', 'billa', 'fantastico', 'хранителен', 
                               'супермаркет', 'магазин'],
            'Ресторанти': ['ресторант', 'кафе', 'restaurant', 'cafe', 'bistro', 
                          'доставка храна', 'delivery'],
            'Транспорт': ['метро', 'автобус', 'такси', 'uber', 'bolt', 'билет'],
            'Бензин': ['бензин', 'gas', 'petrol', 'омв', 'omv', 'shell', 'lukoil'],
            'Сметки': ['ток', 'вода', 'интернет', 'телефон', 'сметка', 'bill'],
            'Наем': ['наем', 'rent', 'квартира'],
            'Здравеопазване': ['аптека', 'лекар', 'болница', 'pharmacy', 'medical'],
            'Дрехи': ['дрехи', 'clothes', 'h&m', 'zara', 'обувки', 'fashion'],
            'Развлечения': ['кино', 'театър', 'концерт', 'cinema', 'movie', 'game'],
            'Покупки': ['amazon', 'ebay', 'онлайн', 'online', 'shop', 'store'],
        }
        
        # Провери за приход
        if any(keyword in desc_lower for keyword in income_keywords) or is_positive_amount:
            return {
                'type': 'приход',
                'category': 'Заплата' if 'заплат' in desc_lower or 'salary' in desc_lower else 'Freelance' if 'freelance' in desc_lower or 'фрийланс' in desc_lower else 'Друг приход',
                'confidence': 0.85 if any(keyword in desc_lower for keyword in income_keywords) else 0.70,
                'reasoning': 'Открити keywords за приход' if any(keyword in desc_lower for keyword in income_keywords) else 'Положителна сума'
            }
        
        # Провери за разход
        for category, keywords in expense_rules.items():
            if any(keyword in desc_lower for keyword in keywords):
                return {
                    'type': 'разход',
                    'category': category,
                    'confidence': 0.80,
                    'reasoning': f'Открити keywords за {category}'
                }
        
        # По подразбиране - разход (ако сумата е отрицателна)
        return {
            'type': 'разход',
            'category': 'Друг разход',
            'confidence': 0.60,
            'reasoning': 'Не са открити специфични keywords'
        }
    
    def classify_transactions(self, description_column: str = 'description', 
                             amount_column: str = 'amount') -> List[Dict[str, Any]]:
        """
        Класифицира всички транзакции
        
        Args:
            description_column: Име на колоната с описание
            amount_column: Име на колоната със сума
        """
        if self.transactions is None:
            raise ValueError("Първо заредете транзакции с load_transactions()")
        
        print(f"\n🤖 Стартирам класификация с {self.llm_provider.upper()}...")
        print("="*60)
        
        self.results = []
        
        for idx, row in self.transactions.iterrows():
            description = str(row[description_column])
            amount = float(row[amount_column])
            
            # Класифицирай според provider
            if self.llm_provider == 'ollama':
                classification = self._classify_with_ollama(description, amount)
            elif self.llm_provider == 'openai':
                classification = self._classify_with_openai(description, amount)
            else:
                classification = self._classify_rule_based(description, amount)
            
            # Използвай абсолютната стойност за показване
            display_amount = abs(amount)
            
            result = {
                'index': idx,
                'description': description,
                'amount': display_amount,
                **classification
            }
            
            self.results.append(result)
            
            # Покажи резултата
            icon = "📈" if classification['type'] == 'приход' else "📉"
            print(f"{icon} {description[:50]:50} | {display_amount:>8.2f} лв | {classification['category']:20} | {classification['confidence']:.0%}")
        
        print("="*60)
        print(f"✅ Класифицирани {len(self.results)} транзакции\n")
        
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        """Връща обобщена статистика"""
        if not self.results:
            raise ValueError("Първо извършете класификация")
        
        df = pd.DataFrame(self.results)
        
        income = df[df['type'] == 'приход']['amount'].sum()
        expenses = df[df['type'] == 'разход']['amount'].sum()
        balance = income - expenses
        
        summary = {
            'total_transactions': len(df),
            'total_income': income,
            'total_expenses': expenses,
            'balance': balance,
            'income_by_category': df[df['type'] == 'приход'].groupby('category')['amount'].sum().to_dict(),
            'expenses_by_category': df[df['type'] == 'разход'].groupby('category')['amount'].sum().to_dict(),
            'avg_confidence': df['confidence'].mean()
        }
        
        return summary
    
    def print_summary(self):
        """Принтира красиво форматирано обобщение"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("💰 ФИНАНСОВО ОБОБЩЕНИЕ")
        print("="*60)
        
        print(f"\n📊 Обща статистика:")
        print(f"   Общо транзакции: {summary['total_transactions']}")
        print(f"   Средна увереност: {summary['avg_confidence']:.1%}")
        
        print(f"\n📈 Приходи:")
        print(f"   Общо: {summary['total_income']:.2f} лв")
        for category, amount in summary['income_by_category'].items():
            print(f"   • {category}: {amount:.2f} лв")
        
        print(f"\n📉 Разходи:")
        print(f"   Общо: {summary['total_expenses']:.2f} лв")
        for category, amount in sorted(summary['expenses_by_category'].items(), 
                                       key=lambda x: x[1], reverse=True):
            print(f"   • {category}: {amount:.2f} лв")
        
        balance = summary['balance']
        balance_icon = "✅" if balance >= 0 else "⚠️"
        print(f"\n{balance_icon} Баланс: {balance:+.2f} лв")
        print("="*60 + "\n")
    
    def export_results(self, output_path: str):
        """Експортира резултатите в CSV"""
        if not self.results:
            raise ValueError("Първо извършете класификация")
        
        df = pd.DataFrame(self.results)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"💾 Резултатите са запазени в: {output_path}")


def main():
    """Демо на финансовия агент"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║           💰 Финансов AI Агент 💰                              ║
    ║                                                                ║
    ║         Класифицира транзакции с AI технология                 ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Създай примерен файл ако не съществува
    example_file = 'examples/transactions.csv'
    if not Path(example_file).exists():
        print("📝 Създавам примерен файл с транзакции...")
        sample_data = {
            'date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', 
                    '2024-01-19', '2024-01-20', '2024-01-21'],
            'description': [
                'Заплата януари 2024',
                'Kaufland - Пазаруване',
                'OMV - Бензин',
                'Счетоводство - Фрийланс проект',
                'Кафе Central',
                'ЧЕЗ - Ток',
                'Лидл - Хранителни продукти'
            ],
            'amount': [2500.00, -85.50, -70.00, 450.00, -12.50, -45.30, -63.20]
        }
        df = pd.DataFrame(sample_data)
        df.to_csv(example_file, index=False, encoding='utf-8-sig')
        print(f"✅ Създаден {example_file}\n")
    
    # Създай агента (използва rule-based по подразбиране)
    agent = FinancialAgent(llm_provider='rule-based')
    
    # Зареди транзакциите
    agent.load_transactions(example_file)
    
    # Класифицирай
    agent.classify_transactions()
    
    # Покажи обобщение
    agent.print_summary()
    
    # Експортирай резултатите
    agent.export_results('examples/transactions_classified.csv')
    
    print("🎉 Готово! Можеш да използваш агента със своите данни!")


if __name__ == '__main__':
    main()

