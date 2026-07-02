#!/usr/bin/env python3
"""
Модерен Финансов AI Агент с LangChain
Използва LLM за интелигентна класификация на транзакции
"""

import pandas as pd
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import os

# LangChain imports
try:
    from langchain_openai import ChatOpenAI
    from langchain_community.llms import Ollama
    from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.pydantic_v1 import BaseModel, Field
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️  LangChain не е инсталиран. Инсталирай с: pip install langchain langchain-openai langchain-community")


class TransactionClassification(BaseModel):
    """Pydantic модел за класификация на транзакция"""
    type: str = Field(description="Тип: 'приход' или 'разход'")
    category: str = Field(description="Категория на транзакцията")
    subcategory: Optional[str] = Field(description="Подкатегория (опционално)")
    confidence: float = Field(description="Увереност от 0.0 до 1.0")
    reasoning: str = Field(description="Кратко обяснение защо е класифицирана така")


class LangChainFinancialAgent:
    """
    Интелигентен финансов агент базиран на LangChain и LLM.
    Използва Large Language Model за класификация на транзакции.
    """
    
    def __init__(self, 
                 llm_provider: str = 'ollama',
                 model_name: str = 'llama3.2',
                 api_key: Optional[str] = None,
                 temperature: float = 0.1):
        """
        Args:
            llm_provider: 'ollama' или 'openai'
            model_name: Име на модела (llama3.2, gpt-4, gpt-3.5-turbo и т.н.)
            api_key: OpenAI API key (ако използваш OpenAI)
            temperature: Креативност на модела (0.0-1.0, по-ниска = по-детерминистична)
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain не е инсталиран!")
        
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.temperature = temperature
        self.transactions = None
        self.results = []
        
        # Инициализирай LLM
        if llm_provider == 'ollama':
            print(f"🤖 Използвам Ollama с модел: {model_name}")
            self.llm = Ollama(
                model=model_name,
                temperature=temperature
            )
        elif llm_provider == 'openai':
            api_key = api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("Нужен е OPENAI_API_KEY!")
            print(f"🤖 Използвам OpenAI с модел: {model_name}")
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=temperature,
                api_key=api_key
            )
        else:
            raise ValueError(f"Непознат provider: {llm_provider}")
        
        # Parser за structured output
        self.parser = JsonOutputParser(pydantic_object=TransactionClassification)
        
        # Категории
        self.categories = {
            'приходи': [
                'Заплата', 'Бонус', 'Freelance/Фрийланс', 'Инвестиции',
                'Дивиденти', 'Лихви', 'Подарък', 'Възстановяване', 
                'Продажба', 'Наем (получен)', 'Друг приход'
            ],
            'разходи': [
                'Храна и напитки', 'Ресторанти и кафета', 'Транспорт', 
                'Гориво/Бензин', 'Комунални услуги', 'Наем', 'Интернет и телефон',
                'Здравеопазване', 'Фитнес и спорт', 'Дрехи и обувки',
                'Развлечения', 'Пътувания', 'Образование', 'Подаръци',
                'Домакинство', 'Красота и грижа', 'Застраховки',
                'Данъци', 'Банкови такси', 'Домашни любимци', 'Друг разход'
            ]
        }
        
        # Създай prompt
        self._create_prompt()
    
    def _create_prompt(self):
        """Създава prompt template с few-shot examples"""
        
        # Few-shot примери
        examples = [
            {
                "input": "Описание: Заплата януари 2024, Сума: 2500 лв",
                "output": json.dumps({
                    "type": "приход",
                    "category": "Заплата",
                    "subcategory": "Месечна заплата",
                    "confidence": 0.95,
                    "reasoning": "Ясно посочено като заплата със сума типична за месечно възнаграждение"
                }, ensure_ascii=False)
            },
            {
                "input": "Описание: Kaufland София, Сума: 67.80 лв",
                "output": json.dumps({
                    "type": "разход",
                    "category": "Храна и напитки",
                    "subcategory": "Супермаркет",
                    "confidence": 0.90,
                    "reasoning": "Kaufland е верига супермаркети, типична покупка на хранителни стоки"
                }, ensure_ascii=False)
            },
            {
                "input": "Описание: OMV Бензиностанция, Сума: 85.00 лв",
                "output": json.dumps({
                    "type": "разход",
                    "category": "Гориво/Бензин",
                    "subcategory": "Бензин",
                    "confidence": 0.95,
                    "reasoning": "OMV е бензиностанция, очевидна покупка на гориво"
                }, ensure_ascii=False)
            },
            {
                "input": "Описание: Уеб дизайн проект - клиент ABC Ltd, Сума: 1200 лв",
                "output": json.dumps({
                    "type": "приход",
                    "category": "Freelance/Фрийланс",
                    "subcategory": "Уеб разработка",
                    "confidence": 0.90,
                    "reasoning": "Плащане за фрийланс проект, професионална услуга"
                }, ensure_ascii=False)
            },
            {
                "input": "Описание: А1 България - Интернет, Сума: 35.99 лв",
                "output": json.dumps({
                    "type": "разход",
                    "category": "Интернет и телефон",
                    "subcategory": "Интернет абонамент",
                    "confidence": 0.95,
                    "reasoning": "А1 е телеком оператор, месечен абонамент за интернет"
                }, ensure_ascii=False)
            }
        ]
        
        # Example prompt template
        example_prompt = ChatPromptTemplate.from_messages([
            ("human", "{input}"),
            ("ai", "{output}")
        ])
        
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples
        )
        
        # Главен prompt (escape curly braces with double braces)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", f"""Ти си експерт финансов анализатор. Анализираш транзакции и ги класифицираш.

Категории за ПРИХОДИ: {', '.join(self.categories['приходи'])}
Категории за РАЗХОДИ: {', '.join(self.categories['разходи'])}

Отговори САМО с JSON в следния формат:
{{{{
    "type": "приход" или "разход",
    "category": "категория от списъка по-горе",
    "subcategory": "подкатегория (опционално)",
    "confidence": число между 0.0 и 1.0,
    "reasoning": "кратко обяснение"
}}}}"""),
            few_shot_prompt,
            ("human", "Описание: {description}, Сума: {amount} лв")
        ])
        
        # Създай chain
        self.chain = self.prompt | self.llm | self.parser
    
    def load_transactions(self, file_path: str) -> pd.DataFrame:
        """Зарежда транзакции от файл"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файлът {file_path} не съществува")
        
        print(f"\n📂 Зареждам транзакции от: {file_path}")
        
        if file_path.suffix == '.csv':
            self.transactions = pd.read_csv(file_path)
        elif file_path.suffix == '.json':
            self.transactions = pd.read_json(file_path)
        else:
            raise ValueError("Поддържат се само CSV и JSON файлове")
        
        print(f"✅ Заредени {len(self.transactions)} транзакции")
        return self.transactions
    
    def classify_transaction(self, description: str, amount: float) -> Dict[str, Any]:
        """Класифицира една транзакция с LLM"""
        try:
            result = self.chain.invoke({
                "description": description,
                "amount": abs(amount)
            })
            return result
        except Exception as e:
            print(f"⚠️  Грешка при класификация: {e}")
            # Fallback
            return {
                "type": "разход" if amount < 0 else "приход",
                "category": "Друг разход" if amount < 0 else "Друг приход",
                "subcategory": None,
                "confidence": 0.50,
                "reasoning": f"Грешка при LLM класификация: {str(e)}"
            }
    
    def classify_all(self, 
                     description_column: str = 'description',
                     amount_column: str = 'amount',
                     batch_size: int = 1) -> List[Dict[str, Any]]:
        """
        Класифицира всички транзакции
        
        Args:
            description_column: Колона с описание
            amount_column: Колона със сума
            batch_size: Брой транзакции за обработка наведнъж (засега 1)
        """
        if self.transactions is None:
            raise ValueError("Първо заредете транзакции с load_transactions()")
        
        print(f"\n🤖 Стартирам AI класификация с {self.llm_provider.upper()} ({self.model_name})...")
        print("="*80)
        
        self.results = []
        total = len(self.transactions)
        
        for idx, row in self.transactions.iterrows():
            description = str(row[description_column])
            amount = float(row[amount_column])
            
            # Класифицирай с LLM
            classification = self.classify_transaction(description, amount)
            
            result = {
                'index': idx,
                'description': description,
                'amount': abs(amount),
                **classification
            }
            
            self.results.append(result)
            
            # Progress indicator
            icon = "📈" if classification['type'] == 'приход' else "📉"
            progress = f"[{idx+1}/{total}]"
            
            print(f"{icon} {progress:8} {description[:40]:40} | {abs(amount):>8.2f} лв | "
                  f"{classification['category']:25} | {classification['confidence']:.0%}")
            
            # Show reasoning за първите няколко
            if idx < 3:
                print(f"           💡 {classification['reasoning']}")
        
        print("="*80)
        print(f"✅ Класифицирани {len(self.results)} транзакции с AI\n")
        
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        """Генерира финансово обобщение"""
        if not self.results:
            raise ValueError("Първо класифицирайте транзакциите")
        
        df = pd.DataFrame(self.results)
        
        income = df[df['type'] == 'приход']['amount'].sum()
        expenses = df[df['type'] == 'разход']['amount'].sum()
        
        return {
            'total_transactions': len(df),
            'total_income': income,
            'total_expenses': expenses,
            'balance': income - expenses,
            'income_by_category': df[df['type'] == 'приход'].groupby('category')['amount'].sum().to_dict(),
            'expenses_by_category': df[df['type'] == 'разход'].groupby('category')['amount'].sum().to_dict(),
            'avg_confidence': df['confidence'].mean()
        }
    
    def print_summary(self):
        """Принтира красиво обобщение"""
        summary = self.get_summary()
        
        print("\n" + "="*80)
        print("💰 AI ФИНАНСОВ АНАЛИЗ")
        print("="*80)
        
        print(f"\n📊 Статистика:")
        print(f"   Транзакции: {summary['total_transactions']}")
        print(f"   AI Увереност: {summary['avg_confidence']:.1%}")
        print(f"   LLM: {self.llm_provider.upper()} ({self.model_name})")
        
        print(f"\n📈 Приходи: {summary['total_income']:.2f} лв")
        for cat, amt in sorted(summary['income_by_category'].items(), key=lambda x: x[1], reverse=True):
            print(f"   • {cat}: {amt:.2f} лв")
        
        print(f"\n📉 Разходи: {summary['total_expenses']:.2f} лв")
        for cat, amt in sorted(summary['expenses_by_category'].items(), key=lambda x: x[1], reverse=True):
            print(f"   • {cat}: {amt:.2f} лв")
        
        balance = summary['balance']
        icon = "✅" if balance >= 0 else "⚠️"
        print(f"\n{icon} Баланс: {balance:+.2f} лв")
        print("="*80 + "\n")
    
    def export_results(self, output_path: str):
        """Експортира резултатите"""
        if not self.results:
            raise ValueError("Няма резултати за експорт")
        
        df = pd.DataFrame(self.results)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"💾 Резултатите са запазени в: {output_path}")


def main():
    """Demo на LangChain агента"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║        🤖 AI Финансов Агент с LangChain 🤖                     ║
    ║                                                                ║
    ║         LLM-базирана интелигентна класификация                 ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    if not LANGCHAIN_AVAILABLE:
        print("❌ LangChain не е инсталиран!")
        print("\n📦 Инсталирай с:")
        print("   pip install langchain langchain-openai langchain-community")
        return
    
    # Провери дали има Ollama
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        ollama_available = response.status_code == 200
    except:
        ollama_available = False
    
    if not ollama_available:
        print("⚠️  Ollama не е стартиран!")
        print("\n📦 Инсталирай Ollama от: https://ollama.ai")
        print("   Стартирай с: ollama run llama3.2")
        print("\n   Или използвай OpenAI с --llm openai --api-key YOUR_KEY")
        return
    
    # Провери дали transactions.csv съществува
    trans_file = 'examples/transactions.csv'
    if not Path(trans_file).exists():
        print(f"📝 Създавам примерен файл...")
        sample_data = {
            'date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19'],
            'description': [
                'Заплата януари 2024',
                'Kaufland София - Хранителни стоки',
                'OMV Бензиностанция',
                'Уеб дизайн проект - ABC Ltd',
                'А1 България - Интернет'
            ],
            'amount': [2500.00, -67.80, -85.00, 1200.00, -35.99]
        }
        df = pd.DataFrame(sample_data)
        Path('examples').mkdir(exist_ok=True)
        df.to_csv(trans_file, index=False, encoding='utf-8-sig')
        print(f"✅ Създаден {trans_file}")
    
    # Създай агента
    agent = LangChainFinancialAgent(
        llm_provider='ollama',
        model_name='llama3.2',
        temperature=0.1
    )
    
    # Зареди и класифицирай
    agent.load_transactions(trans_file)
    agent.classify_all()
    
    # Покажи обобщение
    agent.print_summary()
    
    # Експортирай
    agent.export_results('examples/transactions_ai_classified.csv')
    
    print("🎉 Готово! AI агентът класифицира транзакциите!")


if __name__ == '__main__':
    main()

