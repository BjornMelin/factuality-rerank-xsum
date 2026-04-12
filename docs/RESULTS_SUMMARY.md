# RESULTS_SUMMARY

## What actually ran

- Implemented the full repository and stage-by-stage script surface from the handoff plan.
- Executed the offline fixture fallback because the runtime could not resolve Hugging Face hosts.
- Fixture rows available: 16.

## Requested online path vs executed path

- Requested dataset: `EdinburghNLP/xsum`.
- Requested generator: `facebook/bart-large-xsum`.
- Requested factuality models: `SummaCConv` and `manueldeprada/FactCC`.
- Executed generator: deterministic headline-style offline surrogate.
- Executed factuality metrics: heuristic SummaC-style score, heuristic FactCC-style score, and entity/date/number support.

## Selected operating point

- Best-balanced search winner: `summac_plus_factcc`.
- Beam size: 16
- Normalization: `zscore`
- Weights: `{'token_logprob_avg': 0.0, 'summac_style_score': 0.5, 'factcc_style_score': 0.5, 'entity_support_score': 0.0}`

## Exact commands used

```bash
uv sync --dev
uv run python scripts/00_env_check.py
uv run python scripts/01_prepare_xsum.py
uv run python scripts/02_train_or_load_bart.py
uv run python scripts/03_generate_candidates.py
uv run python scripts/04_score_candidates_summac.py
uv run python scripts/05_score_candidates_factcc.py
uv run python scripts/06_score_candidates_entity_support.py
uv run python scripts/08_merge_candidate_scores.py
uv run python scripts/09_search_weights.py
uv run python scripts/10_rerank_and_eval.py
uv run python scripts/11_bootstrap_metrics.py
uv run python scripts/12_sample_manual_audit.py
uv run python scripts/13_summarize_manual_audit.py
uv run python scripts/14_make_tables_and_figures.py
uv run python scripts/15_build_results_summary.py
uv run python scripts/16_package_repo.py
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

- The executed numbers describe the offline fixture fallback only.
- The repo preserves the online public-data path, but those runs were not executed in this environment.
- The assistant-generated manual audit is useful for error slicing, not for strong human-annotation claims.