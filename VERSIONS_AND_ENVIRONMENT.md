# VERSIONS_AND_ENVIRONMENT.md

This file records the recommended starting environment for the project.

---

## 1. Python

Recommended:
- Python 3.11

Fallback:
- Python 3.12 only if the host environment is cleaner there and package compatibility is verified.

---

## 2. PyTorch

Install PyTorch using the official selector:
https://pytorch.org/get-started/locally/

Do not guess a wheel URL if the host has a specific CUDA / ROCm / CPU setup.

Record:
- `torch.__version__`
- CUDA version
- device name
- `torch.cuda.is_available()`

---

## 3. Core package pins

Recommended exact starting pins:
```text
transformers==5.5.3
datasets==4.8.4
accelerate==1.13.0
evaluate==0.4.6
peft==0.18.1
sentencepiece==0.2.1
```

Recommended supporting packages:
```text
rouge_score>=0.1.2
bert-score>=0.3.13
nltk>=3.9
numpy>=1.26,<3
pandas>=2.2,<3
pyarrow>=17,<20
scikit-learn>=1.5,<2
scipy>=1.13,<2
matplotlib>=3.9,<4
pyyaml>=6.0,<7
jsonlines>=4.0.0,<5
spacy>=3.8,<4
typer>=0.12,<1
rich>=13,<14
```

---

## 4. Environment strategy

### Default
One `uv` project environment:
- `pyproject.toml`
- `.python-version`
- `uv.lock`
- `.venv`

### Fallback
A second metric environment if SummaC or another scoring package conflicts with the main stack.

---

## 5. Reproducibility rules

Always save:
- `uv.lock`
- `pip freeze`
- exact config files used
- dataset revision / model revision if pinned
- final artifact manifest
