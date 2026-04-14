# PROMPTS_INDEX

Use the prompt pack under `prompts/` when handing this repo, its packaged zip,
or selected output artifacts to a GPT-5.4 Pro ChatGPT session with extended
reasoning.

The prompt pack is intentionally detailed. It is designed to preserve project
context, enforce the course rubric and proposal constraints, and stop later
sessions from silently drifting away from the current CLI-first repo.

## Repo authority order

Every prompt in this pack should treat the repository authorities in this order:

1. `REPORT.md`
2. `docs/RUNBOOK.md`
3. `docs/planning/CODEX_EXECUTION_REQUIREMENTS.md`
4. `docs/RESULTS_SUMMARY.md`
5. `docs/CLAIMS_SAFE_TO_WRITE.md`
6. `README.md`
7. tracked manifests and files under `artifacts/` and `outputs/final/`
8. supporting docs such as `VERSIONS.md`, `VERSIONS_AND_ENVIRONMENT.md`,
   `NOTEBOOK_SKILL_INTEGRATION.md`, and `REFERENCES_FULL_URLS.md`
9. the course-facing guidance under `docs/guidelines/`

If any file disagrees with higher-priority authorities, the prompt user should report the mismatch
instead of silently averaging the sources together.

`PROMPTS_INDEX.md` is prompt-routing support only. It is not a competing
current-state handoff.

## Execution modes

Every prompt in this pack supports both of these modes:

- `live repo`: the session can inspect and run commands in the checkout
- `uploaded zip/files`: the session must reason from the uploaded directory tree and attached files

The prompt user should explicitly determine which mode applies before doing anything else.

## Prompt routing

### Start here

If you are opening a new GPT-5.4 Pro session for this repo, start with:

1. `prompts/PROMPT_00_ATTACHMENT_PROTOCOL.md`

Then choose the task-specific prompt:

1. `prompts/PROMPT_01_BUILD_REPO_AND_RUN_PIPELINE.md` for repo execution,
   repairs, reruns, refreshes, or implementation-sensitive work where ChatGPT
   should emit a Codex handoff file
2. `prompts/PROMPT_02_ANALYZE_RESULTS_AND_WRITE_REPORT.md` for report writing, interpretation, or
   presentation support
3. `prompts/PROMPT_03_FINAL_QA_SUBMISSION_REVIEW.md` for final submission QA and correction review

### If only one prompt will be sent

Use `PROMPT_00` first if possible. If the session will receive only one prompt:

- use `PROMPT_01` for implementation or rerun work that should end in a Codex
  handoff file
- use `PROMPT_02` for report drafting and slide support
- use `PROMPT_03` for final QA

## Use-case table

| Situation | Prompt | Expected outcome |
| --- | --- | --- |
| New session needs to ingest repo or zip correctly | `PROMPT_00` | file inventory, authority alignment, current-truth summary |
| Need to repair, rerun, extend, or refresh code/artifacts | `PROMPT_01` | one decision-complete Codex handoff file for implementation |
| Need to write the final report or presentation material | `PROMPT_02` | evidence-bounded report draft, slide outline, executive summary |
| Need strict final review before submission | `PROMPT_03` | correction list, rubric review, submission readiness verdict |

## Recommended attachment bundles

### Minimal core bundle

- repo zip or live repo access
- `REPORT.md`
- `README.md`
- `docs/RUNBOOK.md`
- `docs/planning/CODEX_EXECUTION_REQUIREMENTS.md`
- `docs/RESULTS_SUMMARY.md`
- `docs/CLAIMS_SAFE_TO_WRITE.md`

### Build or rerun bundle

- everything in the minimal core bundle
- `VERSIONS.md`
- `VERSIONS_AND_ENVIRONMENT.md`
- `docs/guidelines/FINAL_README.md`
- `docs/guidelines/FINAL_PROJECT_GUIDELINES.md`
- `docs/guidelines/FAQ.md`
- `docs/guidelines/FINAL_PROJECT_PROPOSAL.md`
- `REFERENCES_FULL_URLS.md`
- `NOTEBOOK_SKILL_INTEGRATION.md` if notebook work is actually in scope

### Report-writing bundle

- everything in the minimal core bundle
- `docs/SLIDES_OUTLINE.md`
- `outputs/final/system_card.md`
- `outputs/final/tables/report_tables.md`
- `outputs/final/manual_audit.csv`
- `outputs/final/manual_audit_summary.json`
- `docs/guidelines/FINAL_README.md`
- `docs/guidelines/FINAL_PROJECT_GUIDELINES.md`
- `docs/guidelines/FAQ.md`
- `docs/guidelines/FINAL_PROJECT_PROPOSAL.md`
- `REFERENCES_FULL_URLS.md`

### Final QA bundle

- final report draft
- slide outline or presentation notes
- everything in the report-writing bundle
- `docs/SUBMISSION_CHECKLIST.md`

## Non-negotiable prompt-pack policies

- The repo is CLI-first. Do not invent a scripts-first or `pipeline.py` workflow.
- Notebooks are secondary analysis and presentation surfaces, not the canonical execution path.
- The current tracked artifacts are bounded-run outputs unless a future session proves a broader run.
- The original proposal matters. Later sessions should compare proposal intent against current repo
  truth before making claims about completion.
- Newer research may inform next steps, but it must not be silently conflated with implemented repo
  behavior.
- Claims must stay within `docs/CLAIMS_SAFE_TO_WRITE.md`.
- For execution-sensitive work, ChatGPT should audit and decide, then emit a
  Codex handoff file instead of trying to implement the repo changes directly.
