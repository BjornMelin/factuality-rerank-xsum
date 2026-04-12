# REPORT

This file is the detailed rationale companion to `PLAN.md`.

Use it when a GPT-5.4 Pro session needs the reasoning context behind the repo’s current execution
contract, documentation authority, prompt-pack design, and claim boundaries.

## 1. Why this repo is CLI-first

The repo used to have a handoff shape that assumed numbered script wrappers and a monolithic
pipeline surface. That shape is no longer the implemented truth.

The current branch hard-cut to:

- `src/factuality_rerank_xsum/cli/main.py` as the canonical stage-entry surface
- domain-owned modules under `src/factuality_rerank_xsum/`
- generated report-facing docs that read tracked manifests and outputs
- a prompt pack that should describe the current repo, not a deleted scaffolding flow

This is the correct end state because:

- one stage surface is easier for an external agent to follow than mixed scripts plus wrappers
- the current CLI exactly matches the stage sequencing in the runbook and results summary
- a future repair or rerun session can verify the truth directly from code and tracked artifacts

## 2. Why public PyPI and public Hugging Face are the defaults

The branch moved away from a mirror-specific lockfile and away from offline-default placeholder
runtime behavior.

The current docs and manifests prove:

- package resolution is expected to work through public PyPI
- the environment stage records DNS reachability, HF CLI availability, and auth state
- dataset and model revisions are recorded in tracked manifests
- the repo is online-first, with explicit fallback still present only where the code records it

This matters for external GPT-5.4 Pro sessions because they need one clear story:

- install with `uv`
- inspect manifests
- trust tracked revisions
- avoid guessing which registry or asset source was intended

## 3. Why notebooks remain secondary

Notebooks still matter in this project, but only in the right role.

They are useful for:

- candidate inspection
- figure-oriented analysis
- qualitative example review
- audit review
- presentation support

They are not the authoritative place for:

- runtime execution
- score production
- final table generation
- claim ownership

This split is deliberate. It keeps the repo reproducible while still making notebook-driven analysis
easy for a strong external session.

## 4. Why the score-column names stay legacy-shaped

The pipeline keeps `summac_style_score` and `factcc_style_score` as downstream artifact column names
even though the implementations are now model-backed Hugging Face paths.

This is a pragmatic compatibility decision:

- downstream score tables and rerank configs already use those column names
- changing them would create unnecessary churn across tracked artifacts
- the docs can state the truth clearly without breaking the existing analysis surface

The important rule for report-writing and QA sessions is:

- treat the names as artifact compatibility labels
- treat the implementation truth as model-backed, as recorded in docs and manifests

## 5. Why the claim envelope is intentionally tight

The current tracked outputs are useful and real, but they are bounded-run artifacts.

The docs therefore deliberately enforce:

- no benchmark-scale XSum claims
- no stronger claim than the executed dataset mode and generator mode
- no strong human-annotation reliability claim from the current manual audit

This is not weakness. It is the right technical posture for a repo that already has:

- a bounded XSum subset configuration
- tracked metrics
- a packaged handoff
- report-facing docs that explicitly describe their limits

An external GPT-5.4 Pro session should inherit that discipline rather than inflate the narrative.

## 6. Why the detailed handoff pack still matters

The shortened docs I previously wrote were more accurate than the historical handoff, but they were
too thin for the real downstream use case:

- upload a repo zip and selected files into ChatGPT
- give GPT-5.4 Pro a high-context prompt and attachment bundle
- ask it to finish reruns, report writing, or submission QA

That workflow still needs:

- detailed attachment instructions
- explicit authority precedence
- dual-mode assumptions for live repo versus uploaded zip
- a precise separation between current repo truth and remaining tasks

So the correct design is not “minimal docs.” The correct design is:

- detailed docs
- current truth
- one deterministic authority order

## 7. Why `PLAN.md` is primary and `REPORT.md` is secondary

`PLAN.md` should answer:

- what this repo is
- what is already implemented
- what files and artifacts are authoritative
- what the next session should do
- what it must not do

`REPORT.md` should answer:

- why this architecture and runtime posture were chosen
- why the docs and prompts are shaped this way
- how to interpret the design tradeoffs

This division is better than distributed authority because an external GPT-5.4 Pro session can
follow one primary contract and still access deeper reasoning when needed.

## 8. Why the prompt pack is specialized for GPT-5.4 Pro

The prompt pack is intentionally specialized rather than generic because the real downstream task is
not “any LLM may maybe do some analysis.”

It is specifically:

- upload files and zip artifacts into ChatGPT
- use GPT-5.4 Pro with extended reasoning
- obtain a strong, evidence-bounded rerun, writing, or QA session

The prompt pack therefore needs:

- explicit file-ingestion protocol
- recommended attachment bundles
- role-specific instructions for execution, writing, and QA
- strong boundaries around unsupported claims

Generic prompts would be more portable but less effective for the actual workflow this repo needs.

## 9. Documentation authority design

The current active authority set is intentionally layered:

- `README.md` for fast repo orientation
- `PLAN.md` for the primary handoff contract
- `docs/RUNBOOK.md` for operator flow
- `docs/RESULTS_SUMMARY.md` for executed-run truth
- `docs/CLAIMS_SAFE_TO_WRITE.md` for claim ceilings
- `REPORT.md` for deep rationale
- `PROMPTS_INDEX.md` and `prompts/` for external GPT sessions

This gives enough detail without forcing every file to repeat every concept equally.

## 10. What a future session should preserve

Any future GPT-5.4 Pro session that modifies this repo should preserve these invariants:

- CLI-first execution remains canonical
- tracked manifests remain the runtime truth source
- prompts remain detailed and attachment-aware
- notebooks remain secondary
- the current bounded-run claim posture remains explicit unless a new rerun truly changes it
- docs, prompts, and tracked artifacts move together when execution truth changes

## 11. Final interpretation

The repo is no longer a speculative build bundle. It is an implemented bounded-run research repo
with:

- current code
- tracked outputs
- current generated docs
- and a detailed external-session handoff pack

That is the right shape for finishing the remaining work: reruns if needed, report writing, and
submission QA.
