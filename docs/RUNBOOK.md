# RUNBOOK

This is the canonical operator flow for the live repository.

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
10. `uv run factuality-rerank-xsum minicheck-optional`
11. `uv run factuality-rerank-xsum figures`
12. `uv run factuality-rerank-xsum results-summary`
13. `uv run factuality-rerank-xsum package`

## Runtime verification

- `hf` CLI availability and authentication are recorded in `artifacts/env/env_report.json`.
- Dataset and model revisions are recorded in `artifacts/data/dataset_manifest.json` and `artifacts/models/baseline_info.json`.
- Candidate generation uses the exported bounded fine-tuned checkpoint when it exists; the public `facebook/bart-large-xsum` revision remains the explicit baseline comparator.
- The audit contract requires explicit `annotator_id` and `annotation_method` provenance and a 24-row stratified completed sample.
- The optional MiniCheck lane is bounded to the audit subset and should be described as subset validation rather than a main metric replacement.
- After runtime or config changes, rerun the affected stages plus `figures`, `results-summary`, and `package` before treating docs or packaged outputs as refreshed.
- Do not treat report/package surfaces as current unless `artifacts/validation/artifact_truth_report.json` passes.

## Artifacts

- Candidate tables: `artifacts/generations/<split>/beam_<n>/candidates.parquet`
- Merged score tables: `artifacts/scores/merged/<split>/beam_<n>.parquet`
- Final outputs: `outputs/final/`
- Package copy: `artifacts/package/factuality-rerank-xsum.zip`