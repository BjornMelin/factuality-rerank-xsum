# RESULTS_SUMMARY

## What actually ran

- Implemented the repository stage surface end to end with public-PyPI and public-Hub defaults.
- Environment mode: `online_hf_ready`.
- Dataset mode executed: `online_hub`.
- Generator mode executed: `huggingface_generation`.
- Dataset rows available: 384.
- Dataset note: Dataset materialized from the public Hugging Face Hub.
- Generator note: Train stage executed a bounded Hugging Face seq2seq fine-tuning run and exported the best local checkpoint for downstream generation.
- Evaluation metrics below are sourced from the current artifacts on disk; rerun the full generation/scoring/evaluation chain to refresh them under any new runtime configuration.

## Requested assets and resolved revisions

- Dataset: `EdinburghNLP/xsum` requested at `7d4d486c2f8ef850b1a11aead99b894ff3dd7da9` resolved to `7d4d486c2f8ef850b1a11aead99b894ff3dd7da9`.
- Generator: `facebook/bart-large-xsum` requested at `2179ab81d3f133e639f2957aec5380e9d56b2783` resolved to `2179ab81d3f133e639f2957aec5380e9d56b2783`.
- FactCC scorer: `manueldeprada/FactCC` requested at `c7b3148015d4ddc263f6e2acb2689e90ac061669` resolved to `c7b3148015d4ddc263f6e2acb2689e90ac061669`.
- NLI scorer: `microsoft/deberta-base-mnli` requested at `a80a6eb013898011540b19bf1f64e21eb61e53d6` resolved to `a80a6eb013898011540b19bf1f64e21eb61e53d6`.
- Factuality score columns retain the legacy `summac_style_score` and `factcc_style_score` names for rerank compatibility, but the implementations are model-backed.

## Selected operating point

- Best-balanced search winner: `custom_0097`.
- Beam size: 16
- Normalization: `zscore`
- Weights: `{'token_logprob_avg': 0.0, 'summac_style_score': 0.75, 'factcc_style_score': 1.0, 'entity_support_score': 0.5}`

## Exact commands used

```bash
uv sync --locked --dev
uv run factuality-rerank-xsum env
uv run factuality-rerank-xsum data
uv run factuality-rerank-xsum train
uv run factuality-rerank-xsum generate
uv run factuality-rerank-xsum score
uv run factuality-rerank-xsum search
uv run factuality-rerank-xsum evaluate
uv run factuality-rerank-xsum audit
uv run factuality-rerank-xsum minicheck-optional
uv run factuality-rerank-xsum figures
uv run factuality-rerank-xsum results-summary
uv run factuality-rerank-xsum package
```

## Main test result

- Baseline ROUGE-Lsum: 0.3592
- Best-balanced ROUGE-Lsum: 0.3393
- Baseline factuality composite: 0.3310
- Best-balanced factuality composite: 0.4337
- Bootstrap ROUGE-Lsum delta CI: [-0.0333, -0.0057]
- Bootstrap factuality delta CI: [0.0825, 0.1250]

## Audit finding

- Audit rows: 24
- Audit provenance: `codex` with `ai-assisted expert adjudication`
- Baseline consistent rate: 0.0000
- Reranked consistent rate: 0.0417
- Dominant remaining failure buckets are listed in `outputs/final/manual_audit_summary.json`.

## Iterative refinement

- The explicit refinement is the entity-support augmentation over the likelihood + SummaC-style + FactCC-style reranker, which changes factuality composite by +0.0069 in the tracked ablation.
- The best-balanced winner also keeps a non-zero entity-support weight, so the refinement remains active in the final operating point.

## Independent evaluator subset

- MiniCheck status: `completed`.
- MiniCheck reranked mean support probability: 0.423064
- MiniCheck baseline mean support probability: 0.359398
- Treat MiniCheck as bounded audit-subset validation, not as a replacement for the main test-set metrics.

## Artifact map

- Summary doc: `docs/RESULTS_SUMMARY.md`
- Main metrics: `outputs/final/main_metrics.csv`
- Ablations: `outputs/final/ablation_metrics.csv`
- Pareto points: `outputs/final/pareto_points.csv`
- Manual audit: `outputs/final/manual_audit.csv`
- Figures: `outputs/final/figures/`
- Tables: `outputs/final/tables/`
- Packaged repo: `artifacts/package/factuality-rerank-xsum.zip`

## Limits on claims

- The manifests now prove public-PyPI installability and public-Hub readiness, but metric freshness still depends on rerunning generate/score/search/evaluate after runtime changes.
- Do not interpret the bounded split configuration as a full benchmark-scale XSum sweep without explicitly increasing the configured limits and rerunning the full pipeline.
- The Codex / AI-assisted expert adjudication audit is useful for error slicing, not for strong human-annotation claims.