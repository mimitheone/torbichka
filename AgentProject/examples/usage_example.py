#!/usr/bin/env python3
"""
Примерна употреба на ClassifierAgent API
"""

from classifier_agent import ClassifierAgent

def main():
    print("🚀 Пример за използване на ClassifierAgent\n")
    
    # Създай агент
    agent = ClassifierAgent()
    
    # Зареди данни
    agent.load_data("examples/sample_data.csv")
    
    # Анализирай данните
    analysis = agent.analyze_data()
    agent.print_analysis(analysis)
    
    # Подготви класификация (предвиждане на category базирано на text)
    agent.prepare_classification(target_column='category', feature_columns=['text'])
    
    # Извърши класификацията
    results = agent.classify(model_type='random_forest')
    
    print("\n" + "="*60)
    print("🎯 Тестване на модела с нови данни")
    print("="*60)
    
    # Тествай с нови примери
    test_examples = [
        {"text": "Много съм доволен от качеството на продукта!"},
        {"text": "Куриерът пристигна точно навреме."},
        {"text": "Операторът в поддръжката ми помогна много."}
    ]
    
    for example in test_examples:
        prediction = agent.predict_new_data(example)
        print(f"\n📝 Текст: {example['text']}")
        print(f"✅ Предвидена категория: {prediction['predicted_class']}")
        print(f"🎯 Увереност: {prediction['confidence']:.2%}")
        print(f"📊 Вероятности:")
        for cls, prob in prediction['probabilities'].items():
            print(f"      {cls}: {prob:.2%}")
    
    print("\n" + "="*60)
    print("✨ Готово!")


if __name__ == '__main__':
    main()

