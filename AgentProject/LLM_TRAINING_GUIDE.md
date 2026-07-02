# 🧠 Как да тренираш собствен LLM модел

Comprehensive guide за обучение на Large Language Models.

## 🎯 3 Основни Подхода

### 1. **Training from Scratch** 🚀
Тренираш напълно нов модел от нулата.

**Pros:**
- ✅ Пълен контрол
- ✅ Специализиран за твоя use case
- ✅ Intellectual property

**Cons:**
- ❌ Много скъпо ($100K - $10M+)
- ❌ Огромни computational resources
- ❌ Месеци тренировка
- ❌ Огромни данни (TB)

**Кога да използваш:**
- Имаш budget от милиони
- Нужен е domain-specific язык
- Security/privacy е критична

---

### 2. **Fine-tuning** ⭐ **Препоръчано**
Взимаш съществуващ модел и го дообучаваш.

**Pros:**
- ✅ По-евтино ($1K - $50K)
- ✅ По-бързо (дни/седмици)
- ✅ По-малко данни (GB)
- ✅ Отлични резултати

**Cons:**
- ⚠️ Все още скъпо
- ⚠️ Нужни GPU resources
- ⚠️ Зависим от base model

**Кога да използваш:**
- Имаш специфична domain
- Нужно е по-добро качество
- Имаш 1000+ quality примера

---

### 3. **LoRA / QLoRA** 🌟 **Най-достъпно**
Low-Rank Adaptation - ефективен fine-tuning.

**Pros:**
- ✅ Много евтино ($100 - $1K)
- ✅ Бързо (часове/дни)
- ✅ Малко GPU memory
- ✅ Може на consumer hardware

**Cons:**
- ⚠️ По-ограничени промени
- ⚠️ Все още нужни данни

**Кога да използваш:**
- Limited budget
- Нужни са промени в стила/формата
- Имаш 100+ качествени примера

---

## 🏗️ Архитектура на LLM

### Transformer Architecture (стандарт)

```
Input Text
    ↓
[Tokenization]
    ↓
[Embedding Layer]
    ↓
[Transformer Blocks] × N
│   ├─ Multi-Head Attention
│   ├─ Feed Forward Network
│   ├─ Layer Normalization
│   └─ Residual Connections
    ↓
[Output Layer]
    ↓
Predicted Tokens
```

### Популярни архитектури:

#### 1. **GPT (Decoder-only)**
```python
# Autoregressive: Предвижда следващия token
"Hello" → "world"
"Hello world" → "!"

# Използват: OpenAI GPT, Meta LLaMA
```

#### 2. **BERT (Encoder-only)**
```python
# Bidirectional: Разбира контекста от двете страни
"The [MASK] sat on the mat" → "cat"

# Използват: Google BERT
```

#### 3. **T5 (Encoder-Decoder)**
```python
# Full seq2seq: Input → Output
"translate to Bulgarian: Hello" → "Здравей"

# Използват: Google T5, BART
```

---

## 🛠️ Технологии и Tools

### 1. **Framework** - PyTorch или JAX

#### PyTorch (най-популярен)
```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load base model
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

# Your training code here
```

**Pros:**
- ✅ Най-популярен
- ✅ Огромна community
- ✅ HuggingFace интеграция

#### JAX/Flax (Google)
```python
import jax
from flax import linen as nn

# More efficient for large-scale training
```

**Pros:**
- ✅ По-бърз за large scale
- ✅ Automatic differentiation
- ⚠️ По-малка community

---

### 2. **Libraries**

#### 🤗 HuggingFace Transformers (Must-have!)
```python
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments
)

# Load model
model = AutoModelForCausalLM.from_pretrained("llama-2-7b")

# Training config
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    warmup_steps=500,
    logging_steps=100,
    save_steps=1000,
)

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)
trainer.train()
```

#### PEFT (Parameter-Efficient Fine-Tuning)
```python
from peft import LoraConfig, get_peft_model

# LoRA configuration
lora_config = LoraConfig(
    r=8,  # Rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Apply LoRA
model = get_peft_model(model, lora_config)
```

#### Axolotl (High-level trainer)
```yaml
# config.yml
base_model: meta-llama/Llama-2-7b-hf
model_type: LlamaForCausalLM
tokenizer_type: LlamaTokenizer

datasets:
  - path: your_dataset.jsonl
    type: alpaca

lora_r: 8
lora_alpha: 16
lora_dropout: 0.05

num_epochs: 3
micro_batch_size: 2
gradient_accumulation_steps: 4
```

---

### 3. **Hardware Requirements**

#### For Fine-tuning 7B model:

**Minimum (LoRA/QLoRA):**
- GPU: RTX 4090 (24GB VRAM)
- RAM: 32GB
- Storage: 100GB SSD
- Cost: ~$2K hardware

**Recommended (Full fine-tuning):**
- GPU: 2-4x A100 (80GB each)
- RAM: 256GB
- Storage: 1TB NVMe
- Cost: ~$50K hardware or $5-10/hour cloud

**From Scratch (100B+ model):**
- GPU: 100s of A100/H100
- Cost: $1M+ infrastructure

#### Cloud Options:

| Provider | GPU | Cost/hour | Best for |
|----------|-----|-----------|----------|
| **Lambda Labs** | A100 (80GB) | $1.29 | LoRA/QLoRA |
| **RunPod** | RTX 4090 | $0.69 | Experimentation |
| **Vast.ai** | Various | $0.20+ | Budget training |
| **Google Colab Pro+** | A100 | $50/mo | Learning |
| **AWS SageMaker** | p4d.24xlarge | $32.77 | Enterprise |

---

## 📊 Data Preparation

### 1. **Data Collection**

За финансов агент нужни са примери:

```json
[
  {
    "instruction": "Класифицирай транзакцията",
    "input": "Kaufland София - 85.50 лв",
    "output": {
      "type": "разход",
      "category": "Храна и напитки",
      "subcategory": "Супермаркет",
      "reasoning": "Kaufland е верига супермаркети"
    }
  },
  {
    "instruction": "Класифицирай транзакцията",
    "input": "Заплата януари 2024 - 2500 лв",
    "output": {
      "type": "приход",
      "category": "Заплата",
      "subcategory": "Месечна заплата",
      "reasoning": "Ясно посочено като заплата"
    }
  }
]
```

**Колко данни са нужни?**
- LoRA: 100-1000 качествени примера
- Fine-tuning: 1K-100K примера
- From Scratch: 10M+ примера

### 2. **Data Format**

#### Alpaca Format (популярен)
```json
{
  "instruction": "Какво прави този код?",
  "input": "def hello():\n    print('hi')",
  "output": "Принтира 'hi'"
}
```

#### ShareGPT Format
```json
{
  "conversations": [
    {"from": "human", "value": "Класифицирай: Kaufland"},
    {"from": "gpt", "value": "Категория: Храна и напитки"}
  ]
}
```

### 3. **Data Quality > Quantity**

```python
def validate_training_example(example):
    """Провери качеството на примера"""
    
    checks = {
        'has_input': bool(example.get('input')),
        'has_output': bool(example.get('output')),
        'reasonable_length': 10 < len(example['input']) < 500,
        'diverse': check_diversity(example),
        'correct': human_validate(example)
    }
    
    return all(checks.values())

# Filter dataset
good_examples = [ex for ex in dataset if validate_training_example(ex)]
```

---

## 🚀 Practical Training Pipeline

### Step-by-Step: LoRA Fine-tuning (Препоръчано за начало)

#### 1. **Setup Environment**

```bash
# Create virtual environment
python -m venv llm-env
source llm-env/bin/activate

# Install dependencies
pip install torch transformers peft accelerate bitsandbytes datasets

# Login to HuggingFace (for model access)
huggingface-cli login
```

#### 2. **Prepare Data**

```python
# prepare_data.py
import json
from datasets import Dataset

# Your training data
data = [
    {
        "instruction": "Класифицирай транзакцията",
        "input": "Kaufland - 85.50 лв",
        "output": '{"type":"разход","category":"Храна и напитки"}'
    },
    # ... more examples
]

# Convert to HuggingFace dataset
dataset = Dataset.from_list(data)

# Format for training
def format_instruction(example):
    return {
        "text": f"### Instruction:\n{example['instruction']}\n\n"
                f"### Input:\n{example['input']}\n\n"
                f"### Output:\n{example['output']}"
    }

dataset = dataset.map(format_instruction)
dataset.save_to_disk("./financial_dataset")
```

#### 3. **Training Script**

```python
# train.py
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_from_disk

# Load base model (quantized for memory efficiency)
model_name = "meta-llama/Llama-2-7b-hf"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_8bit=True,  # 8-bit quantization
    device_map="auto",
    torch_dtype=torch.float16
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

# Prepare for training
model = prepare_model_for_kbit_training(model)

# LoRA config
lora_config = LoraConfig(
    r=16,  # Rank (higher = more parameters to train)
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()  # Should be ~0.1% of original

# Load dataset
dataset = load_from_disk("./financial_dataset")

def tokenize(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=512,
        padding="max_length"
    )

tokenized_dataset = dataset.map(tokenize, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir="./lora-financial-model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_steps=100,
    save_total_limit=3,
    warmup_steps=100,
    optim="paged_adamw_8bit"
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
)

# Train!
trainer.train()

# Save
model.save_pretrained("./lora-financial-model-final")
tokenizer.save_pretrained("./lora-financial-model-final")
```

#### 4. **Inference**

```python
# inference.py
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    device_map="auto"
)

# Load LoRA weights
model = PeftModel.from_pretrained(base_model, "./lora-financial-model-final")

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

# Test
prompt = """### Instruction:
Класифицирай транзакцията

### Input:
Kaufland София - хранителни стоки 67.80 лв

### Output:"""

inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

---

## 💰 Cost Breakdown

### LoRA Fine-tuning (7B model):

| Item | Cost |
|------|------|
| **Data Collection** | $500-2K (if manual labeling) |
| **GPU Time** (Lambda A100) | $10-50 (10-40 hours @ $1.29/hr) |
| **Storage** | $5/month |
| **Inference** (hosted) | $0.001-0.01 per request |
| **Total Initial** | **~$1K-3K** |

### Full Fine-tuning (7B model):

| Item | Cost |
|------|------|
| **Data** | $2K-10K |
| **GPU Time** (4x A100) | $500-2K |
| **Engineering Time** | $5K-20K |
| **Total** | **~$10K-30K** |

### From Scratch (7B model):

| Item | Cost |
|------|------|
| **Compute** | $100K-500K |
| **Data** | $50K-200K |
| **Engineering** | $200K-1M |
| **Total** | **~$500K-2M** |

---

## 🎯 За финансовия агент конкретно:

### Препоръчвам: **LoRA Fine-tuning на Llama 2**

```python
# Financial Transaction Classifier - LoRA

# 1. Събери 500-1000 примера
examples = collect_financial_transactions()

# 2. Fine-tune Llama 2 7B с LoRA
train_lora(
    base_model="llama-2-7b",
    data=examples,
    epochs=3
)

# 3. Deploy локално с Ollama
ollama create financial-classifier -f Modelfile

# 4. Use in production
result = ollama.generate(
    model="financial-classifier",
    prompt="Класифицирай: Kaufland - 85 лв"
)
```

**Benefits:**
- ✅ Специализиран за български език и магазини
- ✅ По-точен от general-purpose GPT
- ✅ Работи offline
- ✅ Безплатен за inference
- ✅ Privacy (data не излиза навън)

---

## 📚 Learning Resources

### Tutorials:
1. **HuggingFace Course** - https://huggingface.co/learn/nlp-course
2. **FastAI** - https://course.fast.ai/
3. **Andrej Karpathy's lectures** - YouTube

### Papers:
1. **"Attention Is All You Need"** - Original Transformer
2. **"LoRA: Low-Rank Adaptation"** - LoRA technique
3. **"LLaMA: Open and Efficient Foundation Models"** - Meta's approach

### Tools:
1. **Axolotl** - https://github.com/OpenAccess-AI-Collective/axolotl
2. **LLaMA Factory** - https://github.com/hiyouga/LLaMA-Factory
3. **PEFT** - https://github.com/huggingface/peft

---

## 🚦 Decision Tree: Кой подход да избереш?

```
Имаш ли $100K+ budget?
│
├─ ДА → Имаш ли уникален domain/език?
│       │
│       ├─ ДА → Train from Scratch
│       └─ НЕ → Full Fine-tuning
│
└─ НЕ → Имаш ли $1K-10K?
        │
        ├─ ДА → Имаш ли 1000+ примера?
        │       │
        │       ├─ ДА → Full Fine-tuning
        │       └─ НЕ → LoRA Fine-tuning
        │
        └─ НЕ → Prompt Engineering with existing LLMs
                (което имаш сега!)
```

---

## ⚡ Quick Start: LoRA в 5 стъпки

```bash
# 1. Install
pip install transformers peft accelerate bitsandbytes

# 2. Prepare data (JSON format)
# [{"instruction": "...", "input": "...", "output": "..."}]

# 3. Use готов tool
git clone https://github.com/hiyouga/LLaMA-Factory
cd LLaMA-Factory

# 4. Configure
cat > config.yaml << EOF
model_name_or_path: meta-llama/Llama-2-7b-hf
dataset: your_dataset
lora_rank: 8
lora_alpha: 16
num_train_epochs: 3
EOF

# 5. Train
python src/train_bash.py config.yaml
```

---

## 🎓 Summary

| Aspect | From Scratch | Fine-tuning | LoRA |
|--------|--------------|-------------|------|
| **Cost** | $500K+ | $10K-30K | **$1K-3K** ✅ |
| **Time** | Months | Weeks | **Days** ✅ |
| **Data** | 10M+ | 10K-100K | **100-1K** ✅ |
| **GPU** | 100s | 4-8 | **1-2** ✅ |
| **Complexity** | Very High | High | **Medium** ✅ |
| **Results** | Best | Very Good | **Good** ✅ |

**За research/hobby проект: LoRA е перфектен избор!** 🌟

---

## 🚀 Next Steps

1. **Learn** - HuggingFace course
2. **Experiment** - Google Colab с малък dataset
3. **Collect Data** - 100-500 quality примера
4. **Train** - LoRA на Llama 2
5. **Evaluate** - Test на real data
6. **Deploy** - Ollama за local inference

Готов си да тренираш собствен модел! 💪

