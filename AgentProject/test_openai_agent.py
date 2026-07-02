#!/usr/bin/env python3
"""
Тест на LangChain агента с OpenAI
ВАЖНО: Използвай .env файл за API ключа!
"""

import os
from langchain_financial_agent import LangChainFinancialAgent

def main():
    # Провери дали има API key
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY не е зададен!")
        print("\n📝 Създай .env файл:")
        print("   echo 'OPENAI_API_KEY=твоят-ключ' > .env")
        print("\nИли задай в terminal:")
        print("   export OPENAI_API_KEY='твоят-ключ'")
        return
    
    print("✅ API Key намерен!")
    print(f"   Ключ: {api_key[:20]}...{api_key[-4:]}")  # Show partial for verification
    
    # Създай агента
    print("\n🤖 Създавам LangChain AI Agent с OpenAI...")
    
    agent = LangChainFinancialAgent(
        llm_provider='openai',
        model_name='gpt-3.5-turbo',  # По-евтин модел
        api_key=api_key,
        temperature=0.1
    )
    
    # Зареди транзакциите
    agent.load_transactions('examples/transactions.csv')
    
    # Класифицирай с AI
    print("\n🚀 Стартирам AI класификация...")
    agent.classify_all()
    
    # Покажи резултатите
    agent.print_summary()
    
    # Експортирай
    agent.export_results('examples/transactions_openai_classified.csv')
    
    print("\n🎉 Успешно! Транзакциите са класифицирани с OpenAI!")

if __name__ == '__main__':
    main()

