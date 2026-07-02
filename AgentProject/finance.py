#!/usr/bin/env python3
"""
CLI интерфейс за Финансов AI Агент
"""

import argparse
import sys
from pathlib import Path
from colorama import init, Fore, Style
from financial_agent import FinancialAgent

# Инициализирай colorama
init()


def print_header():
    """Принтира header"""
    print(Fore.CYAN + """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║        💰 Финансов AI Агент 💰                        ║
    ║                                                       ║
    ║     Класифицира приходи и разходи автоматично         ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """ + Style.RESET_ALL)


def main():
    parser = argparse.ArgumentParser(
        description='Финансов AI Агент за класификация на транзакции'
    )
    parser.add_argument(
        'file',
        help='Път до файл с транзакции (CSV или JSON)'
    )
    parser.add_argument(
        '--description-col',
        default='description',
        help='Име на колоната с описание (по подразбиране: description)'
    )
    parser.add_argument(
        '--amount-col',
        default='amount',
        help='Име на колоната със сума (по подразбиране: amount)'
    )
    parser.add_argument(
        '--llm',
        choices=['rule-based', 'ollama', 'openai'],
        default='rule-based',
        help='LLM provider (по подразбиране: rule-based)'
    )
    parser.add_argument(
        '--api-key',
        help='OpenAI API key (или задай OPENAI_API_KEY)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Експортирай резултатите в CSV файл'
    )
    
    args = parser.parse_args()
    
    print_header()
    
    try:
        # Създай агента
        agent = FinancialAgent(llm_provider=args.llm, api_key=args.api_key)
        
        # Зареди транзакциите
        agent.load_transactions(args.file)
        
        # Класифицирай
        agent.classify_transactions(
            description_column=args.description_col,
            amount_column=args.amount_col
        )
        
        # Покажи обобщение
        agent.print_summary()
        
        # Експортирай ако е зададено
        if args.output:
            agent.export_results(args.output)
        
        print(Fore.GREEN + "✅ Класификацията е завършена успешно!" + Style.RESET_ALL)
        
    except FileNotFoundError as e:
        print(Fore.RED + f"❌ Грешка: {e}" + Style.RESET_ALL)
        sys.exit(1)
    except Exception as e:
        print(Fore.RED + f"❌ Грешка: {e}" + Style.RESET_ALL)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

