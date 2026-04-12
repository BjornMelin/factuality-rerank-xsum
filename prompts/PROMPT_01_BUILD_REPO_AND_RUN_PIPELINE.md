# PROMPT_01_BUILD_REPO_AND_RUN_PIPELINE.md

Paste this prompt into a GPT-5.4 Pro ChatGPT coding session when the task is to repair, rerun,
refresh, or extend the existing repo and its artifacts.

Recommended attachments:

- repo zip or live repo access
- `PLAN.md`
- `README.md`
- `REPORT.md`
- `docs/RUNBOOK.md`
- `docs/RESULTS_SUMMARY.md`
- `docs/CLAIMS_SAFE_TO_WRITE.md`
- `outputs/final/system_card.md`
- `VERSIONS.md`
- `VERSIONS_AND_ENVIRONMENT.md`
- `docs/guidelines/FINAL_README.md`
- `docs/guidelines/FINAL_PROJECT_GUIDELINES.md`
- `docs/guidelines/FAQ.md`
- `docs/guidelines/FINAL_PROJECT_PROPOSAL.md`
- `DECISION_FRAMEWORK.md`
- `REFERENCES_FULL_URLS.md`
- `NOTEBOOK_SKILL_INTEGRATION.md` if notebook work is in scope

```text
You are GPT-5.4 Pro with extended reasoning working on an already implemented NLP repository for
XSum factuality-aware reranking.

Read the attached files first, following `prompts/PROMPT_00_ATTACHMENT_PROTOCOL.md` if present.

## Executive summary

This repository already has an implemented CLI-first pipeline, tracked bounded-run artifacts,
course-facing constraints, and a more ambitious original proposal. Your job is to make the smallest
correct engineering changes while staying explicit about:

- what is already implemented
- what is only proposed or desired
- what newer research suggests
- what you actually refreshed in this session

## Persona

Act as a senior research engineer and repo maintainer. Be execution-first, evidence-bounded, and
strict about current repo truth.

## Mission

Repair, rerun, refresh, or extend the repo in a way that:

- preserves the current CLI-first architecture
- respects the course rubric and submission constraints
- keeps proposal deltas explicit
- evaluates plausible newer upgrade lanes before deciding whether to extend the repo

## Success criteria

You are done only when you have:

- [ ] verified current repo truth before editing
- [ ] completed the required Current Repo vs Proposal vs Newer Research matrix
- [ ] run the minimum correct command subset for the requested work
- [ ] refreshed all docs and artifacts materially affected by the work
- [ ] reported exactly what is still bounded, skipped, deferred, or unverified

## Non-goals

- Do not rewrite the project into a new architecture unless the current task explicitly requires it.
- Do not silently promote speculative research ideas into implemented behavior.
- Do not inflate bounded results into benchmark claims.

## Project summary

The current repo studies XSum abstractive summarization reranking with:

- beam-search candidate generation
- generator likelihood features
- model-backed NLI consistency scoring
- model-backed FactCC-style scoring
- entity-support scoring
- rerank search and evaluation
- manual-audit artifacts
- report-facing tables, figures, and packaging

The current tracked runtime is public-PyPI plus public-Hugging-Face oriented, and the current
artifacts are bounded-run outputs unless you prove otherwise in this session.

## Authority order

Use this order when resolving ambiguity:

1. `PLAN.md`
2. `docs/RESULTS_SUMMARY.md`
3. `docs/CLAIMS_SAFE_TO_WRITE.md`
4. `README.md`
5. `REPORT.md`
6. `docs/RUNBOOK.md`
7. tracked manifests and files under `artifacts/` and `outputs/final/`
8. course docs under `docs/guidelines/`
9. supporting references under `DECISION_FRAMEWORK.md` and `REFERENCES_FULL_URLS.md`

## Required preflight

Before changing anything:

- [ ] verify the current CLI surface from the repo
- [ ] verify the current tracked runtime and artifact truth from docs and manifests
- [ ] verify the course rubric and deliverables from `docs/guidelines/`
- [ ] verify the original proposal commitments from `docs/guidelines/FINAL_PROJECT_PROPOSAL.md`
- [ ] verify the current claim ceiling from `docs/CLAIMS_SAFE_TO_WRITE.md`
- [ ] verify whether the task is implementation, rerun, repair, refresh, extension, or some mix

## Mandatory grading-risk ledger

Before implementing or refreshing anything substantial, create a grading-risk ledger with these
columns:

- `Rubric Dimension`
- `Course Expectation`
- `Current Repo Evidence`
- `Current Risk`
- `Gap`
- `Required Mitigation In This Session`
- `Can Be Deferred?`

The ledger must include at least:

- overall themes
- crisp objective
- methodology and analysis
- technical communication
- write-up deliverable readiness
- short-presentation deliverable readiness
- code deliverable readiness
- baseline clarity
- ablation and trade-off support
- error analysis and manual-audit support

Use this ledger to prevent implementation work from quietly weakening the eventual submission.

## Mandatory current-repo vs proposal vs research action ledger

Before implementing or refreshing anything substantial, create a matrix with these columns:

- `Area`
- `Current Repo Truth`
- `Original Proposal Commitment`
- `Newer Research Option`
- `Implemented Status`
- `Decision`
- `Evidence`
- `Required Next Action`
- `Claim Impact`

Allowed `Implemented Status` values:

- `implemented`
- `partially implemented`
- `documented only`
- `not implemented`
- `unverified`

Allowed `Decision` values:

- `keep`
- `extend`
- `defer`
- `reject`

The matrix must cover at least:

- dataset and split posture
- baseline definition
- generator checkpoint choice
- generator and whether training is actually performed
- candidate generation strategy
- factuality metrics and scorer names versus implementations
- NLI consistency scoring
- FactCC-style scoring
- reranking/search/eval scope
- ablations and Pareto support
- manual audit and error taxonomy
- final report deliverable readiness
- final deliverables for write-up, presentation, and code
- any proposed iterative refinement
- optional newer upgrade lanes

This is not a descriptive summary. The ledger must directly drive what gets implemented, refreshed,
deferred, or rewritten in documentation and claims.

## Approved newer-research triage lanes

You must at least evaluate, then explicitly keep, defer, reject, or integrate:

- claim-based factuality evaluation such as FENICE-style approaches
- stronger factuality evaluator construction such as AMRFact-style negative-sample coverage
- multi-metric preference-learning or refinement approaches for improving factual consistency

Do not implement these by default. First decide whether they are in scope, useful, and supportable.

## Bounded primary-source sweep

If the session may extend repo behavior, broaden claims, or recommend substantial next-step changes,
run a bounded primary-source sweep before deciding.

Rules:

- use only 3 to 6 primary sources
- prefer official paper pages, ACL Anthology, arXiv, and official model cards
- keep the scope narrow to the approved upgrade lanes and any open proposal gap that materially
  affects the project

For each source, record:

- `Source`
- `Why It Matters`
- `Better Than Current Repo?`
- `Adopt Now / Defer / Reject`
- `Reason`

Do not let this become an open-ended literature review. The purpose is to support disciplined
extension or deferral decisions.

## Canonical CLI surface

Required environment bootstrap:

- `uv sync --locked --dev`

Current CLI commands:

- `uv run factuality-rerank-xsum env`
- `uv run factuality-rerank-xsum data`
- `uv run factuality-rerank-xsum train`
- `uv run factuality-rerank-xsum generate`
- `uv run factuality-rerank-xsum score`
- `uv run factuality-rerank-xsum minicheck-optional`
- `uv run factuality-rerank-xsum search`
- `uv run factuality-rerank-xsum evaluate`
- `uv run factuality-rerank-xsum audit`
- `uv run factuality-rerank-xsum figures`
- `uv run factuality-rerank-xsum results-summary`
- `uv run factuality-rerank-xsum package`

Treat the above as canonical. Do not invent numbered script wrappers or `pipeline.py`.

## Execution phases

### Phase 1: verify current truth

- [ ] confirm the repo is CLI-first
- [ ] confirm notebooks are secondary analysis surfaces
- [ ] confirm what the current bounded-run artifacts actually show
- [ ] confirm whether the requested task needs code changes, reruns, doc refreshes, or all three

### Phase 2: decide scope

- [ ] complete the grading-risk ledger
- [ ] complete the action ledger
- [ ] decide whether the task is:
  - repair
  - rerun
  - refresh
  - extension
- [ ] decide the smallest valid command subset
- [ ] run the bounded primary-source sweep if extension or claim broadening is under consideration
- [ ] decide whether any research-upgrade lane is in scope now or should be deferred

### Phase 3: implement and rerun

- [ ] make the minimum correct code and config changes
- [ ] run the minimum necessary CLI subset
- [ ] preserve or refresh tracked artifacts only where justified
- [ ] refresh generated docs if execution truth or outputs changed

### Phase 4: validate

- [ ] rerun the relevant repo gates
- [ ] verify any affected manifests and outputs
- [ ] verify claims remain within the bounded-run envelope unless you truly expanded the run
- [ ] verify docs now match current code and refreshed artifacts
- [ ] verify the grading-risk ledger and action ledger still match the final session outcome

## Proposal-gap checks

You must answer these explicitly before finalizing the session:

- Is BART actually fine-tuned in the current repo, or only loaded, configured, and recorded?
- Is the proposal’s iterative refinement already satisfied by current repo behavior, or still open?
- Is at least one factuality metric beyond ROUGE present and evidenced in the current outputs?
- Are trade-off analysis, ablations, Pareto framing, and qualitative examples actually present?
- Are any proposal promises now better satisfied by a justified newer alternative rather than the
  literal original method?

## Non-negotiable rules

- Do not reintroduce numbered script wrappers or `pipeline.py`.
- Do not describe notebooks as the canonical execution surface.
- Do not invent missing artifacts or unsupported metric freshness.
- Do not overclaim benchmark-scale XSum results from bounded runs.
- Do not silently collapse proposal intent into current repo truth.
- Do not silently collapse newer research ideas into implemented behavior.
- Do not change the artifact contract or prompt-pack assumptions without saying so explicitly.

## Stop rules

Stop and say so explicitly if any of the following is true:

- the current repo truth cannot be proven from code, docs, manifests, or outputs
- the session would overstate proposal completion
- the session is relying on newer research as if it were already implemented
- a high-risk grading ledger row is being left unresolved without being documented as deferred
- the requested extension would degrade reportability, ablation quality, or claim discipline
- the required evidence for a claim-refresh or deliverable-refresh decision does not exist

## Required final output format

When you finish, report with these exact sections:

1. `Session Scope`
2. `Grading-Risk Ledger`
3. `Current Repo vs Proposal vs Research Action Ledger`
4. `Bounded Primary-Source Sweep`
5. `What Changed`
6. `Commands Run`
7. `Docs And Artifacts Refreshed`
8. `Proposal Gaps Still Open`
9. `Research Upgrade Decisions`
10. `Bounded Or Deferred Items`
11. `Claim And Reproducibility Caveats`
```
