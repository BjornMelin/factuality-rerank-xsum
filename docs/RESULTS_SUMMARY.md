# RESULTS_SUMMARY

## What actually ran

- Implemented the repository stage surface end to end with public-PyPI and public-Hub defaults.
- Environment mode: `online_hf_ready`.
- Dataset mode executed: `online_hub`.
- Generator mode currently configured: `huggingface_generation`.
- Dataset rows available: 256.
- Dataset note: Dataset materialized from the public Hugging Face Hub.
- Generator note: Generation and scoring are configured against public Hugging Face assets. This stage records the requested and resolved checkpoints without training.
- Evaluation metrics below are sourced from the current artifacts on disk; rerun the full generation/scoring/evaluation chain to refresh them under any new runtime configuration.

## Requested assets and resolved revisions

- Dataset: `EdinburghNLP/xsum` requested at `7d4d486c2f8ef850b1a11aead99b894ff3dd7da9` resolved to `7d4d486c2f8ef850b1a11aead99b894ff3dd7da9`.
- Generator: `facebook/bart-large-xsum` requested at `2179ab81d3f133e639f2957aec5380e9d56b2783` resolved to `2179ab81d3f133e639f2957aec5380e9d56b2783`.
- FactCC scorer: `manueldeprada/FactCC` requested at `c7b3148015d4ddc263f6e2acb2689e90ac061669` resolved to `c7b3148015d4ddc263f6e2acb2689e90ac061669`.
- NLI scorer: `microsoft/deberta-base-mnli` requested at `a80a6eb013898011540b19bf1f64e21eb61e53d6` resolved to `a80a6eb013898011540b19bf1f64e21eb61e53d6`.
- Factuality score columns retain the legacy `summac_style_score` and `factcc_style_score` names for rerank compatibility, but the implementations are model-backed.

## Selected operating point

- Best-balanced search winner: `summac_plus_factcc`.
- Beam size: 16
- Normalization: `zscore`
- Weights: `{'token_logprob_avg': 0.0, 'summac_style_score': 0.5, 'factcc_style_score': 0.5, 'entity_support_score': 0.0}`

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
uv run factuality-rerank-xsum package
```

## Main test result

- Baseline ROUGE-Lsum: 0.1242
- Best-balanced ROUGE-Lsum: 0.1314
- Baseline factuality composite: 0.8218
- Best-balanced factuality composite: 0.9827
- Bootstrap ROUGE-Lsum delta CI: [-0.0150, 0.0364]
- Bootstrap factuality delta CI: [0.0977, 0.2409]

## Audit finding

- Audit rows: 8
- Baseline consistent rate: 0.5000
- Reranked consistent rate: 0.7500
- Dominant remaining failure buckets are listed in `outputs/final/manual_audit_summary.json`.

## Artifact map

- Summary doc: `docs/RESULTS_SUMMARY.md`
- Main metrics: `outputs/final/main_metrics.csv`
- Ablations: `outputs/final/ablation_metrics.csv`
- Pareto points: `outputs/final/pareto_points.csv`
- Manual audit: `outputs/final/manual_audit.csv`
- Figures: `outputs/final/figures/`
- Tables: `outputs/final/tables/`
- Packaged repo: `../factuality-rerank-xsum.zip`

## Limits on claims

- The manifests now prove public-PyPI installability and public-Hub readiness, but metric freshness still depends on rerunning generate/score/search/evaluate after runtime changes.
- Do not interpret the bounded split configuration as a full benchmark-scale XSum sweep without explicitly increasing the configured limits and rerunning the full pipeline.
- The assistant-generated manual audit is useful for error slicing, not for strong human-annotation claims.
