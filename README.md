# factuality-rerank-xsum

A reproducible summarization-analysis repository for factuality-aware reranking on XSum.

## What this repo contains

- A full stage-by-stage pipeline from environment check through packaging.
- An executed offline fallback run that generated the report-ready artifacts in `outputs/final/`.
- Preserved prompts, plans, and references from the handoff bundle.

## Quick start

```bash
uv sync
uv run python scripts/00_env_check.py
uv run python scripts/01_prepare_xsum.py
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

## Online public-data path

Install PyTorch with the official selector first. For a real public-data rerun, use separate online and metrics environments because the legacy SummaC dependency conflicts with the modern Hugging Face stack.

```bash
uv sync --dev
```

The executed session could not reach Hugging Face, so the generated outputs document the offline fixture fallback rather than a full benchmark run.

## Key artifacts

- `docs/RESULTS_SUMMARY.md`
- `outputs/final/main_metrics.csv`
- `outputs/final/ablation_metrics.csv`
- `outputs/final/pareto_points.csv`
- `outputs/final/manual_audit.csv`
- `outputs/final/figures/`