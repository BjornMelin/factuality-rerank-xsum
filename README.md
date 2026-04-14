# factuality-rerank-xsum

A reproducible summarization-analysis repository for factuality-aware reranking on XSum.

## Canonical docs

- `REPORT.md`: canonical current-state handoff.
- `docs/RUNBOOK.md`: canonical operator flow.
- `docs/planning/CODEX_EXECUTION_REQUIREMENTS.md`: checked-in execution checklist for future zero-context Codex sessions.
- `docs/RESULTS_SUMMARY.md`: artifact-backed results snapshot.
- `docs/CLAIMS_SAFE_TO_WRITE.md`: claim ceiling.

## What this repo contains

- A CLI-first stage pipeline implemented in `src/` and exposed through `uv run factuality-rerank-xsum ...`.
- Public PyPI and public Hugging Face defaults for install, dataset preparation, generation, and scoring.
- Report-ready artifacts in `outputs/final/` generated from the current manifests and evaluation outputs.
- A maintained prompt pack in `prompts/` for reruns, report writing, and final QA review.

## Quick start

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

## Runtime notes

- `uv sync --locked --dev` is the canonical base install path.
- `hf` CLI auth and Hub revision checks are recorded by the env stage.
- The rerank pipeline keeps the legacy `summac` and `factcc` stage names for artifact compatibility even though the implementations are model-backed.
- The main generator lane now exports and uses a bounded fine-tuned BART checkpoint; the public `facebook/bart-large-xsum` path remains the explicit baseline comparator.
- The final audit is a 24-row stratified Codex / AI-assisted expert adjudication sample, not a human-annotator study.
- `uv run factuality-rerank-xsum minicheck-optional` runs a bounded MiniCheck pass on the audit subset and records a structured deferral if the external evaluator cannot be installed.
- After runtime or config changes, rerun `generate`, `score`, `search`, and `evaluate` before treating metric artifacts as refreshed.

Current executed dataset mode: `online_hub`. Current executed generator mode: `huggingface_generation`.

## Notebooks

- `notebooks/` is a companion analysis surface over saved artifacts, not the canonical execution or reporting path.

## Prompt pack

- `PROMPTS_INDEX.md` lists the maintained external ChatGPT prompt-routing flow.
- Prompt files under `prompts/` assume the current CLI-first repo state, not the deleted script-wrapper flow.

## Key artifacts

- `docs/RESULTS_SUMMARY.md`
- `outputs/final/main_metrics.csv`
- `outputs/final/ablation_metrics.csv`
- `outputs/final/pareto_points.csv`
- `outputs/final/manual_audit.csv`
- `outputs/final/figures/`
- `prompts/`
