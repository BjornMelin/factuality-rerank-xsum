# NOTEBOOK_SKILL_INTEGRATION.md

This file explains how to use the attached `jupyter-notebook.zip` skill in the implementation repo.

---

## 1. Why this exists

The project should be script-first, but notebooks are still valuable for:
- sanity checks,
- candidate inspection,
- figure regeneration,
- manual-audit review,
- and presentation-ready analysis.

The attached notebook skill provides a clean scaffolding path so the notebooks are structured, reproducible, and not hand-written raw JSON.

---

## 2. Recommended notebook set

Create or maintain these notebooks:

1. `notebooks/01_sanity_checks.ipynb`
2. `notebooks/02_candidate_analysis.ipynb`
3. `notebooks/03_final_figures.ipynb`
4. `notebooks/04_manual_audit_review.ipynb`

---

## 3. Skill setup

If the implementation chat has access to the attached skill files, it should follow the skill README / `SKILL.md` pattern.

Expected helper path pattern:
```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export JUPYTER_NOTEBOOK_CLI="$CODEX_HOME/skills/jupyter-notebook/scripts/new_notebook.py"
```

If the skill files are simply attached locally rather than installed under `$CODEX_HOME`, the build chat can call the local script path directly.

Example local pattern:
```bash
python /path/to/jupyter-notebook/scripts/new_notebook.py \
  --kind experiment \
  --title "XSum factual reranking experiment notebook" \
  --out notebooks/02_candidate_analysis.ipynb \
  --force
```

---

## 4. Notebook content policy

### 4.1 Keep notebooks lightweight
Notebooks should:
- read saved artifacts,
- summarize results,
- make plots,
- and support qualitative analysis.

They should **not** be the only place where the official experiment logic lives.

### 4.2 Scripts remain authoritative
All final outputs used by the paper must be reproducible from scripts:
- training / baseline
- candidate generation
- scoring
- reranking
- final evaluation
- figure generation

### 4.3 Safe notebook responsibilities
Good notebook jobs:
- inspect candidate diversity
- inspect top success and failure cases
- regenerate presentation figures
- summarize audit label distributions

---

## 5. Recommended notebook sections

### `01_sanity_checks.ipynb`
- environment snapshot
- dataset sample and split checks
- tokenizer sanity checks
- one-example generation demo
- candidate parquet schema check

### `02_candidate_analysis.ipynb`
- candidate count distributions
- beam-size comparisons
- score histograms
- score correlations
- candidate text inspection

### `03_final_figures.ipynb`
- main result tables
- Pareto frontier
- beam trade-off plot
- ablation chart
- metric-vs-human scatter

### `04_manual_audit_review.ipynb`
- audit bucket distributions
- error taxonomy chart
- selected examples for paper
- disagreement cases

---

## 6. Validation rule

A notebook is acceptable only if:
- it opens cleanly,
- it reads from saved repo artifacts,
- and it does not hide any unreproducible logic needed for the final paper.
