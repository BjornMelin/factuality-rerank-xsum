# PLAN

This file is the primary authority for handing this repository to a new GPT-5.4 Pro session in
ChatGPT with extended reasoning. Use it together with the prompt pack under `prompts/`.

It is written for two valid execution contexts:

1. a live local checkout of this repository
2. an uploaded repository zip plus selected supporting files in ChatGPT

The repo is already implemented. The next session should treat this file as a current-state
execution and deliverables contract, not as a greenfield build prompt.

For implementation-sensitive work, the preferred external workflow is now:

1. ChatGPT inspects the repo snapshot and attached docs.
2. ChatGPT audits current repo truth against proposal, rubric, and bounded
   primary-source research.
3. ChatGPT emits one decision-complete markdown handoff file for a fresh Codex
   session.
4. Codex inspects live repo state, verifies only critical assumptions, then
   implements and validates the settled plan.

Do not default to having ChatGPT directly implement or rerun the repo when the
goal is code, experiment, or artifact changes.

## 1. Project anchor

This project is a factuality-aware reranking study for XSum summarization.

Keep the task framed as:

- baseline generator: `facebook/bart-large-xsum`
- candidate generation: beam search
- candidate scoring: generator likelihood, NLI-style consistency, FactCC-style scoring, and entity
  support
- main contribution: reranking trade-offs, ablations, manual audit, and submission-ready analysis

Do not drift into:

- a new summarizer architecture project
- RL or preference optimization
- LLM-judge-centric evaluation
- a large benchmark zoo
- unsupported benchmark-scale claims beyond the tracked run

## 2. Current implemented repo state

The repository currently implements a CLI-first pipeline through:

- `uv run factuality-rerank-xsum env`
- `uv run factuality-rerank-xsum data`
- `uv run factuality-rerank-xsum train`
- `uv run factuality-rerank-xsum generate`
- `uv run factuality-rerank-xsum score`
- `uv run factuality-rerank-xsum search`
- `uv run factuality-rerank-xsum evaluate`
- `uv run factuality-rerank-xsum audit`
- `uv run factuality-rerank-xsum package`

Important architectural facts:

- numbered script wrappers were deleted
- `src/factuality_rerank_xsum/pipeline.py` was deleted
- the Typer CLI in `src/factuality_rerank_xsum/cli/main.py` is the only canonical stage-entry
  surface
- durable behavior lives in `src/factuality_rerank_xsum/`
- notebooks are secondary analysis surfaces only

## 3. Active authority order

When an external GPT-5.4 Pro session sees multiple docs, use this precedence:

1. `PLAN.md`
2. `README.md`
3. `docs/RUNBOOK.md`
4. `docs/RESULTS_SUMMARY.md`
5. `docs/CLAIMS_SAFE_TO_WRITE.md`
6. `REPORT.md`
7. `PROMPTS_INDEX.md`
8. `VERSIONS.md`
9. `VERSIONS_AND_ENVIRONMENT.md`
10. `DECISION_FRAMEWORK.md`
11. `REFERENCES_FULL_URLS.md`

If a file disagrees with tracked artifacts or manifests, prefer the tracked artifacts and manifests.

## 4. Validated runtime truth

Use the tracked manifests and current docs as the source of truth:

- runtime mode: `online_hf_ready`
- executed dataset mode: `online_hub`
- configured generator mode: `huggingface_generation`
- canonical install contract: `uv sync --locked --dev`
- packaged handoff zip: `../factuality-rerank-xsum.zip`

Requested and resolved online assets:

- dataset: `EdinburghNLP/xsum` @ `7d4d486c2f8ef850b1a11aead99b894ff3dd7da9`
- generator: `facebook/bart-large-xsum` @ `2179ab81d3f133e639f2957aec5380e9d56b2783`
- FactCC scorer: `manueldeprada/FactCC` @ `c7b3148015d4ddc263f6e2acb2689e90ac061669`
- NLI scorer: `microsoft/deberta-base-mnli` @ `a80a6eb013898011540b19bf1f64e21eb61e53d6`

Current bounded dataset materialization:

- `dev_smoke`: 4 rows
- `dev_small`: 16 rows
- `val_tune`: 64 rows
- `val_full`: 128 rows
- `test_final`: 128 rows
- dataset rows available in current artifact: 256

Current claim envelope:

- public-PyPI installability and public-HF readiness are supported by manifests
- current metrics are bounded-run artifacts, not a full-scale XSum benchmark claim
- manual audit artifacts are useful for error slicing, not strong human-annotation reliability claims

## 5. Canonical operator flow

For live-repo execution, use this exact stage order unless the task explicitly narrows scope:

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
uv run factuality-rerank-xsum package
```

Supporting commands:

```bash
uv run factuality-rerank-xsum figures
uv run factuality-rerank-xsum results-summary
uv run factuality-rerank-xsum minicheck-optional
```

Meaning of the stages:

- `env`: records environment, package, DNS, HF CLI, auth, and requested/resolved online assets
- `data`: materializes the bounded XSum dataset artifact and split IDs
- `train`: records configured generator/scorer checkpoints and revisions; this stage does not train a
  new model in the current branch
- `generate`: creates bounded candidate artifacts
- `score`: runs NLI consistency, FactCC-style, entity-support scoring, then merges the score tables
- `search`: selects rerank operating points on the validation side
- `evaluate`: applies rerank systems and bootstrap metrics
- `audit`: produces manual-audit samples and summary artifacts
- `package`: rebuilds figures, README/docs surfaces, and the packaged repo zip

## 6. Canonical artifact contract

The tracked final outputs are:

```text
outputs/final/
├── main_metrics.csv
├── ablation_metrics.csv
├── pareto_points.csv
├── bootstrap_cis.json
├── manual_audit.csv
├── manual_audit_summary.json
├── examples_success.md
├── examples_failures.md
├── figures/
│   ├── beam_tradeoff.png
│   ├── component_ablation.png
│   ├── error_taxonomy.png
│   ├── metric_vs_human_scatter.png
│   ├── pareto_frontier.png
│   └── pipeline_diagram.png
├── tables/
│   ├── audit_taxonomy_table.csv
│   ├── qualitative_examples.csv
│   └── report_tables.md
└── system_card.md
```

The active operator/submission docs are:

```text
docs/
├── RUNBOOK.md
├── RESULTS_SUMMARY.md
├── SUBMISSION_CHECKLIST.md
├── SLIDES_OUTLINE.md
└── CLAIMS_SAFE_TO_WRITE.md
```

The handoff is not complete unless:

- the packaged zip
- `docs/RESULTS_SUMMARY.md`
- `outputs/final/`
- and the prompt pack assumptions

all tell the same story.

## 7. Current metrics and selected operating point

Use the current tracked outputs as the default baseline for report-writing and QA sessions unless a
new rerun explicitly refreshed them.

Current selected operating point from `docs/RESULTS_SUMMARY.md`:

- best-balanced system: `summac_plus_factcc`
- beam size: `16`
- normalization: `zscore`
- weights:
  - `token_logprob_avg`: `0.0`
  - `summac_style_score`: `0.5`
  - `factcc_style_score`: `0.5`
  - `entity_support_score`: `0.0`

Current bounded-run headline values:

- baseline ROUGE-Lsum: `0.1242`
- best-balanced ROUGE-Lsum: `0.1314`
- baseline factuality composite: `0.8218`
- best-balanced factuality composite: `0.9827`
- audit rows: `8`
- baseline consistent rate: `0.5000`
- reranked consistent rate: `0.7500`

Treat these as current tracked artifact values, not benchmark-level results.

## 8. Remaining work categories for the next GPT-5.4 Pro session

The next external session should first identify which of these categories it is actually being asked
to perform:

### A. Repo refresh or repair

Use when code, configs, docs, or artifacts need to be repaired or rerun.

Expectations:

- verify repo truth first
- use CLI stages only
- refresh generated docs if execution story changes
- keep claims and prompts aligned in the same pass

### B. Report writing

Use when the main task is to write the final paper or report from the tracked artifacts.

Expectations:

- inspect `docs/RESULTS_SUMMARY.md`, `docs/CLAIMS_SAFE_TO_WRITE.md`, and `outputs/final/`
- identify supported claims only
- prioritize methodology, ablations, audit, and limitations over hype

### C. Final QA and submission review

Use when the report draft and slide materials already exist.

Expectations:

- review claims against artifacts
- check rubric coverage
- produce the smallest correction list needed before submission

### D. Optional bounded rerun

Use only if a new task explicitly requires refreshing metrics or artifacts.

Expectations:

- rerun the necessary stages
- update generated docs
- distinguish new outputs from the current bounded-run artifacts

## 9. Dual-mode handoff instructions

### Live local repo mode

Use this mode when the external session has shell access to the repository.

Required files to inspect first:

- `README.md`
- `PLAN.md`
- `docs/RUNBOOK.md`
- `docs/RESULTS_SUMMARY.md`
- `docs/CLAIMS_SAFE_TO_WRITE.md`
- `REPORT.md`

Then run only the minimum commands needed for the assigned task.

### Uploaded zip and file-bundle mode

Use this mode in ChatGPT when the session receives:

- the packaged repo zip
- and selected Markdown files as attachments

Required attachment set for a high-context handoff:

- `README.md`
- `PLAN.md`
- `REPORT.md`
- `docs/RUNBOOK.md`
- `docs/RESULTS_SUMMARY.md`
- `docs/CLAIMS_SAFE_TO_WRITE.md`
- `PROMPTS_INDEX.md`
- `VERSIONS.md`
- `DECISION_FRAMEWORK.md`
- `REFERENCES_FULL_URLS.md`

If notebook work is in scope, also attach:

- `NOTEBOOK_SKILL_INTEGRATION.md`

When using zip mode:

- inspect the file inventory first
- confirm which artifacts actually exist in the zip
- do not assume shell access
- do not assume metrics are fresher than the tracked docs claim
- explicitly separate current tracked state from any recommended next steps

## 10. Notebook policy

Notebooks remain secondary to the CLI and tracked outputs.

Allowed notebook jobs:

- sanity checks
- candidate inspection
- figure regeneration from saved artifacts
- qualitative example review
- manual-audit inspection
- presentation-oriented analysis

Not allowed:

- moving required experiment logic into notebooks only
- using notebooks as the sole source of tables or claims
- describing notebooks as the canonical execution surface

Use `NOTEBOOK_SKILL_INTEGRATION.md` for the detailed secondary workflow.

## 11. Prompt-pack contract

The prompt pack under `prompts/` is specialized for GPT-5.4 Pro with extended reasoning in
ChatGPT.

Its role is:

- `PROMPT_00`: attachment-ingestion and authority alignment
- `PROMPT_01`: repo refresh, rerun, or repair execution
- `PROMPT_02`: report writing from tracked evidence
- `PROMPT_03`: final QA against the tracked evidence

Use `PROMPTS_INDEX.md` for recommended attachment bundles.

## 12. Non-negotiable do-not-do rules

- Do not reintroduce numbered script wrappers.
- Do not reintroduce `pipeline.py`.
- Do not invent a script-based execution story in prompts or docs.
- Do not describe notebooks as canonical execution.
- Do not invent missing artifacts.
- Do not overclaim benchmark-scale XSum performance from the current bounded run.
- Do not ignore `docs/CLAIMS_SAFE_TO_WRITE.md`.
- Do not treat historical planning language as current repo truth.

## 13. Verification expectations for future sessions

If a future session changes execution, artifacts, docs, or prompts, it should at minimum:

- verify referenced files exist
- verify prompts and docs still match the current stage names
- rerun the relevant generated-doc path if runtime truth changed
- keep tracked artifacts, docs, and prompts aligned in one pass

For repo-mutating work, the canonical local gate set remains:

```bash
uv run ruff check --fix
uv run ruff format
uv run mypy .
uv run ty check
uv run pytest
```
