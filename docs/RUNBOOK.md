# RUNBOOK

## Fast path used in this session

1. `uv sync`
2. `uv run python scripts/00_env_check.py`
3. `uv run python scripts/01_prepare_xsum.py`
4. `uv run python scripts/02_train_or_load_bart.py`
5. `uv run python scripts/03_generate_candidates.py`
6. `uv run python scripts/04_score_candidates_summac.py`
7. `uv run python scripts/05_score_candidates_factcc.py`
8. `uv run python scripts/06_score_candidates_entity_support.py`
9. `uv run python scripts/08_merge_candidate_scores.py`
10. `uv run python scripts/09_search_weights.py`
11. `uv run python scripts/10_rerank_and_eval.py`
12. `uv run python scripts/11_bootstrap_metrics.py`
13. `uv run python scripts/12_sample_manual_audit.py`
14. `uv run python scripts/13_summarize_manual_audit.py`
15. `uv run python scripts/14_make_tables_and_figures.py`
16. `uv run python scripts/15_build_results_summary.py`
17. `uv run python scripts/16_package_repo.py`

## Online public-data path

- Install PyTorch with the official selector before attempting a full public-data rerun.
- Because `summac==0.0.4` conflicts with the modern Hugging Face stack used by the requested online path, use separate `online` and `metrics` environments for a full rerun.

## Artifacts

- Candidate tables: `artifacts/generations/<split>/beam_<n>/candidates.parquet`
- Merged score tables: `artifacts/scores/merged/<split>/beam_<n>.parquet`
- Final outputs: `outputs/final/`