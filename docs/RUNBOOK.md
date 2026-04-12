# RUNBOOK

## Canonical install and runtime flow

1. `uv sync --locked --dev`
2. `uv run factuality-rerank-xsum env`
3. `uv run factuality-rerank-xsum data`
4. `uv run factuality-rerank-xsum train`
5. `uv run factuality-rerank-xsum generate`
6. `uv run factuality-rerank-xsum score`
7. `uv run factuality-rerank-xsum search`
8. `uv run factuality-rerank-xsum evaluate`
9. `uv run factuality-rerank-xsum audit`
10. `uv run factuality-rerank-xsum package`

## Runtime verification

- `hf` CLI availability and authentication are recorded in `artifacts/env/env_report.json`.
- Dataset and model revisions are recorded in `artifacts/data/dataset_manifest.json` and `artifacts/models/baseline_info.json`.
- Candidate generation uses the configured `facebook/bart-large-xsum` revision unless the model config explicitly changes mode.
- After runtime or config changes, rerun `generate`, `score`, `search`, and `evaluate` before treating metric artifacts as refreshed.

## Artifacts

- Candidate tables: `artifacts/generations/<split>/beam_<n>/candidates.parquet`
- Merged score tables: `artifacts/scores/merged/<split>/beam_<n>.parquet`
- Final outputs: `outputs/final/`
