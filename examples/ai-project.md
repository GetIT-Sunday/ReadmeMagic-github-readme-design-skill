<p align="center">
  <h1 align="center">🤖 Transformers</h1>
  <p align="center">
    <strong>State-of-the-art Machine Learning for Jax, PyTorch and TensorFlow</strong>
  </p>
  <p align="center">
    <a href="#-features">Features</a> • 
    <a href="#-installation">Installation</a> • 
    <a href="#-quick-start">Quick Start</a> • 
    <a href="#-models">Models</a> • 
    <a href="#-training">Training</a>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-4.35.0-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/license-Apache%202.0-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/python-3.8+-yellow?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/pytorch-2.0+-red?style=flat-square" alt="PyTorch">
  <img src="https://img.shields.io/badge/tensorflow-2.12+-orange?style=flat-square" alt="TensorFlow">
  <img src="https://img.shields.io/huggingface-transformers/4.35.0-blue?style=flat-square" alt="Transformers">
  <img src="https://img.shields.io/github/stars/huggingface/transformers?style=social" alt="Stars">
</p>

---

## ✨ Features

<table>
  <tr>
    <td width="50%">
      <h3>🧠 State-of-the-art Models</h3>
      <ul>
        <li>100,000+ pre-trained models</li>
        <li>100+ languages supported</li>
        <li>Text, Audio, Vision tasks</li>
      </ul>
    </td>
    <td width="50%">
      <h3>⚡ Easy to Use</h3>
      <ul>
        <li>Simple API</li>
        <li>3 lines of code to use</li>
        <li>Extensive documentation</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🔧 Framework Agnostic</h3>
      <ul>
        <li>PyTorch</li>
        <li>TensorFlow</li>
        <li>JAX</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🚀 Production Ready</h3>
      <ul>
        <li>ONNX export</li>
        <li>TensorRT optimization</li>
        <li>TorchScript support</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🚀 Quick Start

### Installation

```bash
pip install transformers
```

### Quick Example

```python
from transformers import pipeline

# Sentiment analysis
classifier = pipeline("sentiment-analysis")
result = classifier("I love this product!")
print(result)
# [{'label': 'POSITIVE', 'score': 0.9998}]

# Text generation
generator = pipeline("text-generation", model="gpt2")
result = generator("Once upon a time", max_length=50)
print(result[0]['generated_text'])
```

---

## 📦 Installation

### Requirements

- Python 3.8+
- PyTorch 2.0+ or TensorFlow 2.12+

### Install

```bash
# Basic installation
pip install transformers

# With PyTorch
pip install transformers[torch]

# With TensorFlow
pip install transformers[tf-cpu]

# With JAX
pip install transformers[jax]
```

### From Source

```bash
git clone https://github.com/huggingface/transformers.git
cd transformers
pip install -e .
```

---

## 🧠 Models

### Popular Models

| Model | Description | Size | Download |
|-------|-------------|------|----------|
| BERT | Bidirectional Encoder Representations | 110M-340M | [Link](https://huggingface.co/bert-base-uncased) |
| GPT-2 | Generative Pre-trained Transformer 2 | 117M-1.5B | [Link](https://huggingface.co/gpt2) |
| T5 | Text-to-Text Transfer Transformer | 60M-11B | [Link](https://huggingface.co/t5-small) |
| LLaMA | Large Language Model Meta AI | 7B-65B | [Link](https://huggingface.co/meta-llama) |
| Mistral | Mistral 7B | 7B | [Link](https://huggingface.co/mistralai/Mistral-7B-v0.1) |

### Model Hub

Browse 100,000+ models on [Hugging Face Hub](https://huggingface.co/models).

---

## 🎯 Training

### Fine-tuning

```python
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=2
)

# Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

# Train
trainer.train()
```

### Distributed Training

```bash
# Multi-GPU
python -m torch.distributed.launch \
  --nproc_per_node=4 \
  train.py

# Multi-node
python -m torch.distributed.launch \
  --nnodes=2 \
  --nproc_per_node=4 \
  train.py
```

---

## 🔮 Inference

### Python API

```python
from transformers import pipeline

# Text classification
classifier = pipeline("text-classification")
result = classifier("This movie is great!")

# Named entity recognition
ner = pipeline("ner")
result = ner("Apple is looking at buying U.K. startup for $1 billion")

# Question answering
qa = pipeline("question-answering")
result = qa(question="What is the capital of France?", context="France is a country in Europe.")
```

### REST API

```bash
# Start server
transformers-cli env
transformers-cli serve --model bert-base-uncased

# Call API
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!"}'
```

---

## 📊 Benchmarks

| Model | GLUE | SQuAD | SuperGLUE | Speed |
|-------|------|-------|-----------|-------|
| BERT-base | 79.0 | 80.8 | 66.4 | 100% |
| BERT-large | 82.1 | 84.1 | 73.7 | 75% |
| RoBERTa-base | 83.5 | 84.6 | 78.8 | 95% |
| GPT-2 | 78.5 | 76.3 | 62.1 | 110% |

---

## 📁 Project Structure

```
transformers/
├── src/
│   └── transformers/
│       ├── models/           # Model implementations
│       ├── pipelines/        # High-level pipelines
│       ├── trainer/          # Training utilities
│       └── utils/            # Utility functions
├── examples/                 # Example scripts
├── tests/                    # Test suite
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
└── setup.py
```

---

## 🧪 Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run specific test
pytest tests/test_modeling_bert.py

# Run linting
make quality

# Format code
make style
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Good First Issues

- [ ] Add new model
- [ ] Improve documentation
- [ ] Add tests
- [ ] Fix bugs

---

## 📄 License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

---

## 📚 References

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [BERT: Pre-training of Deep Bidirectional Transformers](https://arxiv.org/abs/1810.04805)
- [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165)

---

<p align="center">
  <strong>⭐ If Transformers helps you, please give it a star!</strong>
</p>

<p align="center">
  <a href="https://star-history.com/#huggingface/transformers&Date">
    <img src="https://api.star-history.com/svg?repos=huggingface/transformers&type=Date" alt="Star History Chart" width="600">
  </a>
</p>
