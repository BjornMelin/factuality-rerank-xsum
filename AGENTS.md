# Repository Guidelines

## Overview

Repo studies factuality-aware reranking for XSum summarization. Generates candidate summaries, scores with factuality + quality signals, reranks, packages evaluation / audit / reporting artifacts for reproducible analysis. Research pipeline: durable outputs, submission docs, offline fallback when full online model execution unavailable.

## Project Structure & Module Organization

Code in `src/factuality_rerank_xsum/` by area: `generation/`, `scoring/`, `rerank/`, `search/`, `evaluation/`, `audit/`, `reporting/`, `packaging/`, `viz/`, `data/`, `runtime/`, `utils/`, `cli/`. Typer CLI in `src/factuality_rerank_xsum/cli/` = canonical stage surface; keep durable behavior in `src/`. Tests `tests/unit/`, configs `configs/`, docs `docs/`, notebooks `notebooks/`, tracked outputs `artifacts/`, `outputs/final/`, `data/processed/splits/`, `VERSIONS.md`.

## Build, Test, and Development Commands

`uv` for all env + execution.

- `uv sync --locked --dev`: install exact CI dependency set.
- `make env`, `make smoke`, `make data`, `make train`, `make generate`, `make score`, `make search`, `make eval`, `make audit`, `make figures`, `make results-summary`, `make package`: canonical stage flow via CLI.
- `uv run factuality-rerank-xsum <command>`: repo CLI for stages like `generate`, `score`, `figures`, `results-summary`, `package`.
- `uv run ruff check --fix && uv run ruff format && uv run mypy . && uv run ty check && uv run pytest`: full local gate set (CI).

## Environment & Validation Contract

Python `3.12` for local `uv` `.venv`. CI: `3.11`, `3.12`, `3.13`. `uv` required; one canonical project env unless task proves separate env needed.

- Before local GPU, CUDA, training, inference: read `~/.codex/LOCAL_WORKSTATION.md` first.

## Plugin, MCP, and Tool Routing

Default stack: `$python-expert` + `$hugging-face` + `$github`.

- Route Python tasks through `$python-expert` first; front-door router, then bias lane: core architecture + typing, API + contracts, async + concurrency, testing, toolchain + packaging, performance + profiling.
- `$hugging-face`: model, dataset, paper, Hub, Space, Transformers, TRL, training, inference, evaluation, ML research; experiment planning, model-facing work, result interpretation.
- `$github`: repo metadata, issues, PRs, review threads, Actions, releases, `gh` collaboration / publish.
- `$technical-writing`: `README.md`, `docs/`, runbooks, system cards, results summaries, specs, submission docs.
- `$root-cause-finder`: debug + review. Prove intended path, find first unintended side effect; prefer upstream logic fixes over permissive downstream contract changes.
- `opensrc` / `$opensrc-inspect` when docs + types insufficient and source-level dependency inspection changes recommendation. Cite exact versions + local source paths.
- `$agents-md-maintainer` after durable workflow, tooling, contract, or output changes: smallest valid repo-wide `AGENTS.md` update if needed.

## Research, Search, and Delegation

- Official docs first. `context7` for version-specific library + framework docs; `exa` for fresh multi-source research; `zen` for structured analysis on high-impact or ambiguous decisions.
- `web.run` for live web lookup, attribution, latest-state verification. Search first; `open`, `find`, `click` only as needed.
- `functions.exec_command` + `rg` for local codebase discovery. `git grep` when git-tracked scope matters.
- Nontrivial work: explicit plan via `functions.update_plan`.
- `functions.request_user_input` when assumptions risky, breaking, or hard to reverse.
- Subagents: bounded, disjoint tasks only; explicit ownership, concrete outputs, clear do / don't constraints.
- `functions.send_message` or `functions.followup_task` to continue active agent; avoid overlapping spawns.
- `functions.wait_agent` + `functions.close_agent` to finish delegation. No synthesize / finalize until every active subagent finished or explicitly closed.
- Integrate subagent results before overlapping follow-up delegation.

## Coding Style & Naming Conventions

Python `3.11+`, 4-space indent, explicit typing, small composable functions. Ruff: style + import order, `100` char line; mypy + ty strict. snake_case: modules, functions, config files, YAML keys, CLI helpers.

## Testing Guidelines

Deterministic `pytest` in `tests/unit/test_*.py`. Prefer fusion, scorer, fixture, runtime, reporting helpers over notebook-only validation. Offline-safe tests where possible; checked-in workflow supports fixture fallback when networked model access unavailable.

## Research Workflow & Artifact Rules

Generated research outputs tracked. Do not hand-edit or casually regenerate `artifacts/`, `outputs/final/`, `data/processed/splits/`, `VERSIONS.md`; regeneration → call out in PR. `uv run factuality-rerank-xsum minicheck-optional` optional; not on main `make` scoring path. Checked-in results = bounded-run artifacts; read `docs/RESULTS_SUMMARY.md` + tracked manifests before benchmark-scale claims.

Final deliverables under `outputs/final/`: `main_metrics.csv`, `ablation_metrics.csv`, `pareto_points.csv`, `bootstrap_cis.json`, `manual_audit.csv`, `manual_audit_summary.json`, `figures/`, `tables/`, `system_card.md`. Handoff incomplete until those outputs, packaged zip, summary docs agree.

Notebooks: secondary; inspect artifacts, regen figures; required experiment logic stays in CLI + `src/`.

## Documentation & Claims

Align with `docs/CLAIMS_SAFE_TO_WRITE.md`. Changes to generated outputs or execution story → same-pass updates to `README.md`, `docs/RESULTS_SUMMARY.md`, `docs/SUBMISSION_CHECKLIST.md`. Offline fixture fallback → state plainly; no benchmark-level claims.

## Commit & Pull Request Guidelines

Scoped conventional commits; group changes into reviewable commits; semantic scoped conventional commit/SEMVER style PR titles. PR: problem statement; call out tracked outputs, doc claims, pipeline stages; describe commits. Align with `docs/CLAIMS_SAFE_TO_WRITE.md`; no overstated benchmark or model-execution results.
