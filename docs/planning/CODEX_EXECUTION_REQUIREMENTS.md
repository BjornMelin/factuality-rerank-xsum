# Codex Execution Requirements

Updated: 2026-04-13

This file is the checked-in execution checklist for future zero-context Codex
sessions. Read it after `AGENTS.md`, `REPORT.md`, and `docs/RUNBOOK.md`.

## Overview

Use this file when the task requires live repo implementation, doc refresh,
artifact refresh, or validation against the proposal and course rubric.

This is not the current-state narrative handoff. That role belongs to
`REPORT.md`.

## Read First

1. `AGENTS.md`
2. `REPORT.md`
3. `docs/RUNBOOK.md`
4. `docs/RESULTS_SUMMARY.md`
5. `docs/CLAIMS_SAFE_TO_WRITE.md`
6. this file
7. `docs/planning/GRADING_RISK_LEDGER.md`
8. `docs/planning/PROPOSAL_ALIGNMENT.md`
9. `docs/planning/PROPOSAL_REPO_RESEARCH_ACTION_LEDGER.md`
10. `docs/guidelines/FINAL_PROJECT_GUIDELINES.md`
11. `docs/guidelines/FINAL_PROJECT_PROPOSAL.md`

Prefer tracked manifests and tracked outputs over prose when they disagree.

## Confirmed Current State

- The repo is CLI-first.
- `train` performs a bounded BART fine-tuning run and exports a local best
  checkpoint.
- The public `facebook/bart-large-xsum` path remains the explicit baseline
  comparator.
- The current bounded rerun includes:
  `env`, `data`, `train`, `generate`, `score`, `search`, `evaluate`, `audit`,
  `minicheck-optional`, `figures`, `results-summary`, and `package`.
- Artifact truth is enforced before `results-summary` and `package`.
- The final audit is a 24-row stratified Codex / AI-assisted expert
  adjudication sample.
- MiniCheck is available as bounded audit-subset validation only.

## What Has Been Completed

- Proposal-critical implementation gaps were closed for bounded fine-tuning,
  checkpoint-backed generation, refreshed scoring/search/evaluation, and audit
  provenance.
- Final outputs and package were regenerated on the refreshed run.
- Report-facing docs were aligned around bounded-run claims and explicit audit
  wording.
- Submission-facing artifacts now exist in-repo: a final report PDF, editable
  slide deck, slide PDF, and speaker notes.
- The repo now has planning ledgers under `docs/planning/`.

## What Remains

Treat these as the default remaining-work buckets for future sessions:

1. Doc and prompt maintenance when runtime truth changes.
2. Final QA against the rubric and proposal after any future rerun or doc change.
3. Optional bounded extensions only if they do not break claim discipline.

## Proposal And Rubric Validation Matrix

| Area | Current repo truth | Proposal / rubric expectation | Current status | Evidence |
| --- | --- | --- | --- | --- |
| Fine-tuned summarizer | Bounded BART fine-tune exists | Fine-tune BART on XSum | complete at bounded scale | `artifacts/models/training_manifest.json` |
| Candidate generation | Beam search candidates generated | Multiple candidates per article | complete | `artifacts/generations/` |
| Factuality reranking | Likelihood + SummaC-style + FactCC-style + entity support | Factuality-aware reranking | complete | `src/factuality_rerank_xsum/scoring/`, `outputs/final/` |
| Main metrics | ROUGE + factuality composite + audit + MiniCheck subset | Clear objective and evaluation | complete within bounded scope | `docs/RESULTS_SUMMARY.md` |
| Trade-off analysis | Search, ablations, Pareto outputs exist | Methodology and analysis depth | complete within bounded scope | `outputs/final/pareto_points.csv`, `ablation_metrics.csv` |
| Error analysis | 24-row stratified audit with taxonomy summary | Annotated error analysis | complete with AI-assisted provenance | `outputs/final/manual_audit.csv` |
| Iterative refinement | Entity-support augmentation is explicit | At least one improvement iteration | complete | `outputs/final/ablation_metrics.csv` |
| Communication | Final report, deck, slide PDF, and notes exist in repo | Write-up and presentation readiness | complete within bounded scope | `docs/final-report/`, `outputs/final/submission/` |

## Open Decisions

- Whether to broaden the bounded run beyond the current split sizes.
- Whether to add a second independent evaluator beyond MiniCheck.
- Whether any future extension belongs in repo scope or should remain future
  work in the paper.

## Research To Perform

Only perform fresh research when it materially affects a decision.

- Use primary sources only.
- Keep the sweep bounded.
- Prefer official docs, model cards, ACL Anthology, arXiv, and trusted primary
  repos.
- Record adopt / defer / reject decisions explicitly.

## Execution Tasks

### For repo implementation or refresh

1. Inspect the live repo and read the documents listed above.
2. Verify the requested task against current artifact truth.
3. Make the smallest coherent code/doc change.
4. Refresh any generated outputs required by the change.
5. Update docs and prompts in the same pass if execution truth changed.
6. Re-run the relevant validations.

### For doc-only or report-support work

1. Reconfirm the current tracked metrics and bounded-run caveats.
2. Keep the public baseline vs final system framing explicit.
3. Keep audit wording exact.
4. Do not inflate MiniCheck into a main metric.

## Validation

### Canonical rerun chain

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

### Repo gates

```bash
uv run ruff check
uv run ruff format --check
uv run mypy .
uv run ty check
uv run pytest
```

### Doc/reporting validations

- `artifacts/validation/artifact_truth_report.json` must pass.
- `docs/RESULTS_SUMMARY.md`, `outputs/final/`, and the packaged zip must agree.
- `docs/CLAIMS_SAFE_TO_WRITE.md` must remain compatible with the refreshed run.

## Success Criteria

- A new Codex session can start from zero context by reading the declared
  authority chain.
- No parallel authority order remains.
- Runtime truth, prompts, package contents, and report-facing docs agree.
- Proposal/rubric coverage is explicit and bounded honestly.
- Validation commands relevant to the change have passed.

## Allowed Tools, Skills, Plugins

- Use `rg` first for local discovery.
- Use `$agents-md-maintainer` for any durable `AGENTS.md` update.
- Use `$technical-writing` for docs, runbooks, specs, and prompt surfaces.
- Use `$hard-cut`, `$reducing-entropy`, and `$clean-code` when reducing or
  tightening parallel guidance.
- Use `$python-expert`, `$hugging-face`, and `$github` when those lanes
  materially improve correctness.
- Use read-only subagents for broad documentation or comment audits.

## Files And Context To Load

- `artifacts/data/dataset_manifest.json`
- `artifacts/env/env_report.json`
- `artifacts/models/training_manifest.json`
- `artifacts/validation/artifact_truth_report.json`
- `outputs/final/main_metrics.csv`
- `outputs/final/ablation_metrics.csv`
- `outputs/final/manual_audit.csv`
- `outputs/final/manual_audit_summary.json`

## Rules To Enforce

- Keep the repo CLI-first.
- Keep one current-state canonical handoff.
- Keep one canonical operator flow.
- Keep claims conservative and bounded.
- Do not describe the audit as human annotation.
- Do not describe MiniCheck as a full test-set metric.
- Keep docs, prompts, outputs, manifests, and package surfaces aligned.

## Blocked / Deferred

- Full-benchmark-scale XSum claims remain deferred.
- A second independent evaluator remains deferred.
- Any large architecture changes remain deferred unless the task explicitly
  requires them.
