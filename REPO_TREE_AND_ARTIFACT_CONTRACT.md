# REPO_TREE_AND_ARTIFACT_CONTRACT

This file summarizes the active repo surfaces and the tracked artifact contract.

## Active top-level authorities

- `README.md`
- `PLAN.md`
- `REPORT.md`
- `PROMPTS_INDEX.md`
- `AGENTS.md`
- `VERSIONS.md`
- `VERSIONS_AND_ENVIRONMENT.md`
- `DECISION_FRAMEWORK.md`
- `REFERENCES_FULL_URLS.md`

## Active operator and submission docs

- `docs/RUNBOOK.md`
- `docs/RESULTS_SUMMARY.md`
- `docs/SUBMISSION_CHECKLIST.md`
- `docs/SLIDES_OUTLINE.md`
- `docs/CLAIMS_SAFE_TO_WRITE.md`

## Prompt pack

- `prompts/PROMPT_00_ATTACHMENT_PROTOCOL.md`
- `prompts/PROMPT_01_BUILD_REPO_AND_RUN_PIPELINE.md`
- `prompts/PROMPT_02_ANALYZE_RESULTS_AND_WRITE_REPORT.md`
- `prompts/PROMPT_03_FINAL_QA_SUBMISSION_REVIEW.md`

## Canonical stage surface

Run stages through the Typer CLI:

1. `uv run factuality-rerank-xsum env`
2. `uv run factuality-rerank-xsum data`
3. `uv run factuality-rerank-xsum train`
4. `uv run factuality-rerank-xsum generate`
5. `uv run factuality-rerank-xsum score`
6. `uv run factuality-rerank-xsum search`
7. `uv run factuality-rerank-xsum evaluate`
8. `uv run factuality-rerank-xsum audit`
9. `uv run factuality-rerank-xsum package`

Optional companion commands:

- `uv run factuality-rerank-xsum figures`
- `uv run factuality-rerank-xsum results-summary`
- `uv run factuality-rerank-xsum minicheck-optional`

## Required tracked outputs

- `outputs/final/main_metrics.csv`
- `outputs/final/ablation_metrics.csv`
- `outputs/final/pareto_points.csv`
- `outputs/final/bootstrap_cis.json`
- `outputs/final/manual_audit.csv`
- `outputs/final/manual_audit_summary.json`
- `outputs/final/figures/*`
- `outputs/final/tables/*`
- `outputs/final/system_card.md`

## Packaging requirement

The final handoff is not complete until the packaged zip, `docs/RESULTS_SUMMARY.md`, and
`outputs/final/` tell the same story.
