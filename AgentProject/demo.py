#!/usr/bin/env python3
"""
Демонстрация на всички възможности на ClassifierAgent
"""

from colorama import init, Fore, Style
from classifier_agent import ClassifierAgent
import time

init()


def print_section(title):
    """Принтира секция"""
    print("\n" + "="*70)
    print(Fore.CYAN + Style.BRIGHT + f"  {title}" + Style.RESET_ALL)
    print("="*70 + "\n")
    time.sleep(1)


def demo_text_classification():
    """Demo за текстова класификация"""
    print_section("📝 ДЕМО 1: Класификация на текстове (NLP)")
    
    agent = ClassifierAgent()
    agent.load_data("examples/sample_data.csv")
    
    # Анализ
    print(Fore.YELLOW + "Анализирам данните..." + Style.RESET_ALL)
    analysis = agent.analyze_data()
    print(f"✓ {analysis['rows']} записа с {len(analysis['columns'])} колони")
    
    # Подготовка
    print(Fore.YELLOW + "\nПодготвям текстова класификация..." + Style.RESET_ALL)
    agent.prepare_classification(target_column='category', feature_columns=['text'])
    
    # Класификация
    print(Fore.YELLOW + "Обучавам модел..." + Style.RESET_ALL)
    results = agent.classify(model_type='random_forest')
    
    print(f"\n{Fore.GREEN}✅ Модел обучен успешно!{Style.RESET_ALL}")
    print(f"   Точност: {results['accuracy']:.2%}")
    print(f"   Класове: {', '.join(results['classes'])}")
    
    # Тестване на модела
    print(Fore.YELLOW + "\n🧪 Тествам модела с нови текстове..." + Style.RESET_ALL)
    test_cases = [
        "Страхотен продукт, много съм доволен!",
        "Куриерът пристигна навреме.",
        "Служителят ми помогна бързо и ефективно."
    ]
    
    for text in test_cases:
        prediction = agent.predict_new_data({'text': text})
        print(f"\n   📄 \"{text}\"")
        print(f"   → {Fore.GREEN}{prediction['predicted_class']}{Style.RESET_ALL} " +
              f"(увереност: {prediction['confidence']:.1%})")


def demo_numeric_classification():
    """Demo за числена класификация"""
    print_section("🔢 ДЕМО 2: Класификация на числови данни")
    
    agent = ClassifierAgent()
    agent.load_data("examples/numeric_data.csv")
    
    # Анализ
    print(Fore.YELLOW + "Анализирам данните..." + Style.RESET_ALL)
    analysis = agent.analyze_data()
    agent.print_analysis(analysis)
    
    # Подготовка
    print(Fore.YELLOW + "Подготвям класификация за одобрение на заем..." + Style.RESET_ALL)
    agent.prepare_classification(
        target_column='loan_approved',
        feature_columns=['age', 'income', 'credit_score']
    )
    
    # Класификация с различни модели
    print(Fore.YELLOW + "\n🎯 Тествам различни модели..." + Style.RESET_ALL)
    
    models = ['random_forest', 'logistic', 'naive_bayes']
    best_model = None
    best_accuracy = 0
    
    for model in models:
        agent_temp = ClassifierAgent()
        agent_temp.load_data("examples/numeric_data.csv")
        agent_temp.prepare_classification(
            target_column='loan_approved',
            feature_columns=['age', 'income', 'credit_score']
        )
        results = agent_temp.classify(model_type=model, test_size=0.2)
        
        print(f"\n   {model.upper()}: {results['accuracy']:.2%}")
        
        if results['accuracy'] > best_accuracy:
            best_accuracy = results['accuracy']
            best_model = model
    
    print(f"\n{Fore.GREEN}🏆 Най-добър модел: {best_model.upper()} " +
          f"({best_accuracy:.2%}){Style.RESET_ALL}")
    
    # Тестване
    print(Fore.YELLOW + "\n🧪 Тествам най-добрия модел..." + Style.RESET_ALL)
    agent.classify(model_type=best_model)
    
    test_cases = [
        {'age': 35, 'income': 60000, 'credit_score': 720},
        {'age': 25, 'income': 30000, 'credit_score': 600},
        {'age': 50, 'income': 95000, 'credit_score': 760}
    ]
    
    for case in test_cases:
        prediction = agent.predict_new_data(case)
        approved = prediction['predicted_class']
        color = Fore.GREEN if approved == 'yes' else Fore.RED
        print(f"\n   👤 Възраст: {case['age']}, Доход: ${case['income']}, " +
              f"Кредитен рейтинг: {case['credit_score']}")
        print(f"   → {color}{approved.upper()}{Style.RESET_ALL} " +
              f"(увереност: {prediction['confidence']:.1%})")


def demo_sentiment_analysis():
    """Demo за sentiment анализ"""
    print_section("😊 ДЕМО 3: Sentiment Analysis (Анализ на емоции)")
    
    agent = ClassifierAgent()
    agent.load_data("examples/sample_data.csv")
    
    print(Fore.YELLOW + "Класифицирам sentiment на текстове..." + Style.RESET_ALL)
    agent.prepare_classification(target_column='sentiment', feature_columns=['text'])
    results = agent.classify(model_type='random_forest')
    
    print(f"\n{Fore.GREEN}✅ Sentiment модел готов!{Style.RESET_ALL}")
    print(f"   Точност: {results['accuracy']:.2%}")
    
    # Тестови текстове
    print(Fore.YELLOW + "\n🧪 Анализирам sentiment на нови текстове..." + Style.RESET_ALL)
    test_texts = [
        "Страхотно! Много съм доволен от услугата.",
        "Разочарован съм, качеството е много лошо.",
        "Приемливо, нищо специално."
    ]
    
    for text in test_texts:
        prediction = agent.predict_new_data({'text': text})
        sentiment = prediction['predicted_class']
        
        emoji = "😊" if sentiment == 'positive' else "😞"
        color = Fore.GREEN if sentiment == 'positive' else Fore.RED
        
        print(f"\n   {emoji} \"{text}\"")
        print(f"   → {color}{sentiment.upper()}{Style.RESET_ALL} " +
              f"(увереност: {prediction['confidence']:.1%})")


def main():
    """Главна функция"""
    print(Fore.CYAN + Style.BRIGHT + """
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║           🤖 ДЕМО: AI Agent за Класификация 🤖                 ║
    ║                                                                ║
    ║         Показва всички възможности на агента!                  ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """ + Style.RESET_ALL)
    
    time.sleep(2)
    
    try:
        # Demo 1: Текстова класификация
        demo_text_classification()
        time.sleep(2)
        
        # Demo 2: Числова класификация
        demo_numeric_classification()
        time.sleep(2)
        
        # Demo 3: Sentiment analysis
        demo_sentiment_analysis()
        
        # Финал
        print_section("🎉 ДЕМОТО ЗАВЪРШИ!")
        print(Fore.GREEN + Style.BRIGHT + """
        Агентът може да:
        ✓ Анализира CSV и JSON файлове
        ✓ Класифицира текстови данни (NLP)
        ✓ Класифицира числови данни
        ✓ Прави sentiment analysis
        ✓ Сравнява различни модели
        ✓ Прави предвиждания за нови данни
        
        🚀 Започни с: python agent.py your_data.csv
        """ + Style.RESET_ALL)
        
    except Exception as e:
        print(Fore.RED + f"\n❌ Грешка: {e}" + Style.RESET_ALL)
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

