# REFERENCES_FULL_URLS.md

This file contains the canonical research papers, official documentation, model cards, repositories, and package pages referenced by the final merged handoff.

---

## 1. Core project papers

### Dataset and baseline summarization

- Narayan, Shashi, Shay B. Cohen, and Mirella Lapata. 2018. **Don’t Give Me the Details, Just the Summary! Topic-Aware Convolutional Neural Networks for Extreme Summarization.** EMNLP 2018.  
  <https://aclanthology.org/D18-1206/>

- Lewis, Mike, Yinhan Liu, Naman Goyal, et al. 2020. **BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension.** ACL 2020.  
  <https://aclanthology.org/2020.acl-main.703/>

### Factuality metrics and evaluation

- Kryscinski, Wojciech, Bryan McCann, Caiming Xiong, and Richard Socher. 2020. **Evaluating the Factual Consistency of Abstractive Text Summarization.** EMNLP 2020.  
  <https://aclanthology.org/2020.emnlp-main.750/>

- Wang, Alex, Kyunghyun Cho, and Mike Lewis. 2020. **Asking and Answering Questions to Evaluate the Factual Consistency of Summaries.** ACL 2020.  
  <https://aclanthology.org/2020.acl-main.450/>

- Laban, Philippe, Tobias Schnabel, Paul N. Bennett, and Marti A. Hearst. 2022. **SummaC: Re-Visiting NLI-based Models for Inconsistency Detection in Summarization.** TACL 2022.  
  <https://aclanthology.org/2022.tacl-1.10/>

- Pagnoni, Artidoro, Vidhisha Balachandran, and Yulia Tsvetkov. 2021. **Understanding Factuality in Abstractive Summarization with FRANK: A Benchmark for Factuality Metrics.** NAACL 2021.  
  <https://aclanthology.org/2021.naacl-main.383/>

- Honovich, Or, Uri Shaham, Samuel R. Bowman, and Omer Levy. 2022. **TRUE: Re-evaluating Factual Consistency Evaluation.** DialDoc 2022.  
  <https://aclanthology.org/2022.dialdoc-1.19/>

- Tang, Liyan, Tanya Goyal, Alex Fabbri, Philippe Laban, Jiacheng Xu, Semih Yavuz, Wojciech Kryscinski, Justin Rousseau, and Greg Durrett. 2023. **Understanding Factual Errors in Summarization: Errors, Summarizers, Datasets, Error Detectors.** ACL 2023.  
  <https://aclanthology.org/2023.acl-long.650/>

- Scirè, Alessandro, Karim Ghonim, and Roberto Navigli. 2024. **FENICE: Factuality Evaluation of Summarization Based on Natural Language Inference and Claim Extraction.** Findings of ACL 2024.  
  <https://aclanthology.org/2024.findings-acl.841/>

- Zha, Yuheng, Yichi Yang, Ruichen Li, and Zhiting Hu. 2023. **AlignScore: Evaluating Factual Consistency with a Unified Alignment Function.** ACL 2023.  
  <https://aclanthology.org/2023.acl-long.634/>

- Tang, Liyan, Philippe Laban, and Greg Durrett. 2024. **MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents.** EMNLP 2024.  
  <https://aclanthology.org/2024.emnlp-main.499/>

### Factuality improvement / related methods

- Cao, Shuyang, and Lu Wang. 2021. **CLIFF: Contrastive Learning for Improving Faithfulness and Factuality in Abstractive Summarization.** EMNLP 2021.  
  <https://aclanthology.org/2021.emnlp-main.532/>

- Cao, Meng, et al. 2023. **Hallucinated but Factual! Inspecting the Factuality of Hallucinations in Abstractive Summarization.** ACL 2023.  
  <https://aclanthology.org/2023.acl-long.276/>

- Zhong, Yang and Diane Litman. 2025. **A Tale of Evaluating Factual Consistency: Case Study on Long Document Summarization Evaluation.** Findings of ACL 2025.  
  <https://aclanthology.org/2025.findings-acl.648/>

### Evaluation metric

- Lin, Chin-Yew. 2004. **ROUGE: A Package for Automatic Evaluation of Summaries.** Workshop on Text Summarization Branches Out.  
  <https://aclanthology.org/W04-1013/>

---

## 2. Official dataset and model cards

- XSum dataset card  
  <https://huggingface.co/datasets/EdinburghNLP/xsum>

- `facebook/bart-large-xsum` model card  
  <https://huggingface.co/facebook/bart-large-xsum>

- `manueldeprada/FactCC` model card  
  <https://huggingface.co/manueldeprada/FactCC>

- `FacebookAI/roberta-large-mnli` model card  
  <https://huggingface.co/FacebookAI/roberta-large-mnli>

- `microsoft/deberta-large-mnli` model card  
  <https://huggingface.co/microsoft/deberta-large-mnli>

- `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli` model card  
  <https://huggingface.co/MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli>

---

## 3. Official documentation

### Hugging Face

- Summarization task guide  
  <https://huggingface.co/docs/transformers/tasks/summarization>

- Trainer docs  
  <https://huggingface.co/docs/transformers/en/main_classes/trainer>

- Text generation docs  
  <https://huggingface.co/docs/transformers/main_classes/text_generation>

- Evaluate docs  
  <https://huggingface.co/docs/evaluate/index>

- Datasets loading docs  
  <https://huggingface.co/docs/datasets/loading>

### `uv`

- Working on projects  
  <https://docs.astral.sh/uv/guides/projects/>

- Locking and syncing  
  <https://docs.astral.sh/uv/concepts/projects/sync/>

### PyTorch

- Get started locally  
  <https://pytorch.org/get-started/locally/>

---

## 4. Official or primary repositories

- Hugging Face summarization example script  
  <https://github.com/huggingface/transformers/blob/main/examples/pytorch/summarization/run_summarization.py>

- Hugging Face summarization example README  
  <https://github.com/huggingface/transformers/blob/main/examples/pytorch/summarization/README.md>

- SummaC repository  
  <https://github.com/tingofurro/summac>

- FactCC original repository (archived)  
  <https://github.com/salesforce/factCC>

- QAGS repository  
  <https://github.com/W4ngatang/qags>

- MiniCheck repository  
  <https://github.com/Liyan06/MiniCheck>

- FENICE repository  
  <https://github.com/Babelscape/FENICE>

- AlignScore repository  
  <https://github.com/yuh-zha/AlignScore>

---

## 5. Package pages

- transformers  
  <https://pypi.org/project/transformers/>

- datasets  
  <https://pypi.org/project/datasets/>

- accelerate  
  <https://pypi.org/project/accelerate/>

- evaluate  
  <https://pypi.org/project/evaluate/>

- peft  
  <https://pypi.org/project/peft/>

- sentencepiece  
  <https://pypi.org/project/sentencepiece/>

- summac  
  <https://pypi.org/project/summac/>

---

## 6. spaCy docs

- spaCy usage  
  <https://spacy.io/usage>

- spaCy models  
  <https://spacy.io/usage/models>

---

## 7. Notes for the build chat

The build chat should use this references file in three ways:

1. as the source of truth for current official docs and model cards,
2. as the bibliography seed for proposal/final-report references,
3. as the fallback location for package/repo verification if any implementation choice is unclear.
