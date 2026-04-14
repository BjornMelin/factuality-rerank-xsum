# System card

- Configured study: XSum factuality-aware reranking with public Hugging Face assets.
- Requested assets: dataset `EdinburghNLP/xsum`, generator `facebook/bart-large-xsum`, FactCC `manueldeprada/FactCC`, NLI `microsoft/deberta-base-mnli`.
- Executed dataset mode: `online_hub`.
- Requested generator mode: `huggingface_generation`.
- Executed generator mode: `huggingface_generation`.
- Active generator label: `bart_xsum_finetuned`.
- Bounded split materialization: dev_small=16, dev_smoke=4, test_final=128, train_finetune=128, val_full=128, val_tune=64.
- Public `facebook/bart-large-xsum` remains the explicit baseline comparator.
- Audit provenance is Codex / AI-assisted expert adjudication, not human annotation.
- MiniCheck subset evidence, when present, is bounded audit-subset validation rather than a main test-set metric.
- Intended use: reproducible reranking runs, artifact inspection, report writing, and submission QA over tracked outputs.
- The repository is configured for the public Hugging Face runtime path.