#!/usr/bin/env python3
"""
CLI интерфейс за AI Agent за класификация
"""

import argparse
import sys
from pathlib import Path
from colorama import init, Fore, Style
from classifier_agent import ClassifierAgent

# Инициализирай colorama за цветен output
init()


def print_header():
    """Принтира header на приложението"""
    print(Fore.CYAN + """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║        🤖 AI Agent за Класификация на Данни 🤖        ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """ + Style.RESET_ALL)


def main():
    parser = argparse.ArgumentParser(
        description='AI Agent за автоматична класификация на данни'
    )
    parser.add_argument(
        'file',
        help='Път до файл с данни (CSV или JSON)'
    )
    parser.add_argument(
        '--target', '-t',
        help='Име на target колоната за класификация'
    )
    parser.add_argument(
        '--features', '-f',
        nargs='+',
        help='Feature колони (по подразбиране: всички освен target)'
    )
    parser.add_argument(
        '--model', '-m',
        choices=['auto', 'random_forest', 'logistic', 'naive_bayes'],
        default='auto',
        help='Тип на ML модела'
    )
    parser.add_argument(
        '--test-size',
        type=float,
        default=0.2,
        help='Процент данни за тестване (0.0-1.0)'
    )
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Само анализирай данните, без класификация'
    )
    
    args = parser.parse_args()
    
    print_header()
    
    try:
        # Създай агента
        agent = ClassifierAgent()
        
        # Зареди данните
        agent.load_data(args.file)
        
        # Анализирай данните
        analysis = agent.analyze_data()
        agent.print_analysis(analysis)
        
        if args.analyze_only:
            print(Fore.GREEN + "✅ Анализът е завършен!" + Style.RESET_ALL)
            return
        
        # Ако няма зададен target, питай потребителя
        target_column = args.target
        if not target_column:
            print(Fore.YELLOW + "⚠️  Не е зададена target колона." + Style.RESET_ALL)
            print("\nДостъпни колони:")
            for i, col in enumerate(analysis['columns'], 1):
                unique = analysis['unique_values'][col]
                print(f"   {i}. {col} ({unique} уникални стойности)")
            
            choice = input("\n👉 Изберете номер на target колона: ").strip()
            try:
                target_column = analysis['columns'][int(choice) - 1]
            except (ValueError, IndexError):
                print(Fore.RED + "❌ Невалиден избор!" + Style.RESET_ALL)
                sys.exit(1)
        
        # Подготви класификацията
        agent.prepare_classification(target_column, args.features)
        
        # Изпълни класификацията
        results = agent.classify(model_type=args.model, test_size=args.test_size)
        
        # Покажи подробни резултати
        print("\n" + "="*60)
        print(Fore.GREEN + "✨ КЛАСИФИКАЦИЯ ЗАВЪРШЕНА ✨" + Style.RESET_ALL)
        print("="*60)
        print(f"\n🎯 Модел: {results['model']}")
        print(f"🎓 Тренировъчни данни: {results['train_size']}")
        print(f"🧪 Тестови данни: {results['test_size']}")
        print(f"✅ Точност: {Fore.GREEN}{results['accuracy']:.2%}{Style.RESET_ALL}")
        
        print(f"\n📊 Детайлни резултати по класове:\n")
        report = results['classification_report']
        for cls in results['classes']:
            if cls in report:
                metrics = report[cls]
                print(f"   {cls}:")
                print(f"      Precision: {metrics['precision']:.2%}")
                print(f"      Recall:    {metrics['recall']:.2%}")
                print(f"      F1-Score:  {metrics['f1-score']:.2%}")
                print(f"      Support:   {metrics['support']}")
                print()
        
        print("="*60)
        print(Fore.GREEN + "🎉 Успешно завършено!" + Style.RESET_ALL)
        
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

