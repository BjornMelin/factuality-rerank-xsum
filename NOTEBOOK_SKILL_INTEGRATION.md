# NOTEBOOK_SKILL_INTEGRATION

This file explains how to use notebook workflows in this repository without letting notebooks
become the canonical execution surface.

The repo is CLI-first. Notebooks are allowed and useful, but only as secondary analysis surfaces
over tracked artifacts.

## 1. Why this file exists

An external GPT-5.4 Pro session may receive:

- a live repository checkout
- a packaged repo zip
- selected Markdown files
- a request to explore, debug, or present results with notebooks

That session still needs clear notebook guidance for:

- how notebooks fit into the repo
- which notebooks are worth creating or maintaining
- how to scaffold them safely
- what is allowed in notebooks versus what must stay in the CLI and `src/`

## 2. Canonical notebook policy

Notebooks are secondary to:

- `uv run factuality-rerank-xsum ...`
- tracked outputs under `artifacts/` and `outputs/final/`
- generated report-facing docs under `docs/`

Notebooks should:

- read saved artifacts
- inspect candidates and metrics
- regenerate presentation-oriented figures from tracked outputs
- support qualitative analysis and manual-audit review

Notebooks should not:

- become the only place where official experiment logic lives
- become the only place where final tables or figures can be recreated
- replace the canonical CLI stage flow

## 3. When to use the `jupyter-notebook` skill

Use the `jupyter-notebook` skill when the task is to:

- create a new notebook under `notebooks/`
- clean up an existing `.ipynb`
- scaffold a notebook with a stable structure instead of editing raw JSON

The skill is especially useful in external-session or zip-upload workflows because it reduces the
chance of hand-editing notebook JSON poorly.

## 4. Recommended notebook set

If notebooks are being created or refreshed, these are the preferred notebook roles:

1. `notebooks/01_sanity_checks.ipynb`
2. `notebooks/02_candidate_analysis.ipynb`
3. `notebooks/03_final_figures.ipynb`
4. `notebooks/04_manual_audit_review.ipynb`

Suggested responsibilities:

- `01_sanity_checks`
  - environment snapshot
  - dataset sample and split checks
  - candidate schema checks
  - quick one-example generation/score inspection using saved artifacts

- `02_candidate_analysis`
  - candidate-count distributions
  - beam-size comparisons
  - score distributions
  - score-correlation inspection
  - qualitative candidate text review

- `03_final_figures`
  - report-table inspection
  - Pareto and beam trade-off figure regeneration from saved outputs
  - presentation-oriented visual review

- `04_manual_audit_review`
  - audit bucket distributions
  - selected examples
  - disagreement review
  - paper/presentation candidate examples

## 5. Setup and helper-path guidance

If the notebook skill is installed in the normal Codex location, the typical helper-path pattern is:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export JUPYTER_NOTEBOOK_CLI="$CODEX_HOME/skills/jupyter-notebook/scripts/new_notebook.py"
```

If the helper is available through a plugin or local checkout instead, adapt the script path but
keep the same behavior: use the helper to scaffold a clean notebook file rather than writing raw
JSON.

Example pattern:

```bash
python "$JUPYTER_NOTEBOOK_CLI" \
  --kind experiment \
  --title "XSum factual reranking analysis" \
  --out notebooks/02_candidate_analysis.ipynb \
  --force
```

## 6. Notebook input policy

Prefer reading these tracked sources:

- `artifacts/data/dataset.parquet`
- `artifacts/generations/...`
- `artifacts/scores/...`
- `artifacts/search/...`
- `artifacts/eval/...`
- `artifacts/audit/...`
- `outputs/final/...`

Do not build notebooks around:

- ad hoc local files outside the repo contract
- one-off CSV exports with no tracked provenance
- a separate notebook-only execution path

## 7. Validation rule

A notebook is acceptable only if:

- it opens cleanly
- it reads tracked repo artifacts
- it does not replace a canonical CLI stage
- it does not become the sole source of report claims
- it remains understandable to another engineer or external GPT-5.4 Pro session

## 8. Guidance for uploaded-zip sessions

If a GPT-5.4 Pro session is working from an uploaded repo zip rather than a live checkout:

- inspect which notebooks are already present before creating new ones
- prefer notebooks that consume `outputs/final/` when shell execution is unavailable
- avoid instructions that assume direct kernel execution unless the environment clearly supports it
- keep notebook guidance subordinate to the tracked docs and artifacts in the zip
