# Repository Guidelines

## Overview

This repository studies factuality-aware reranking for XSum summarization. It generates candidate summaries, scores them with factuality and quality signals, reranks them, and packages evaluation, audit, and reporting artifacts for reproducible analysis. The codebase is organized as a research pipeline with durable outputs, submission-facing docs, and offline fallback paths when full online model execution is unavailable.

## Project Structure & Module Organization

Implementation code lives in `src/factuality_rerank_xsum/`, organized by pipeline area: `generation/`, `scoring/`, `rerank/`, `search/`, `evaluation/`, `audit/`, `reporting/`, `packaging/`, `viz/`, `data/`, `runtime/`, `utils/`, and `cli/`. Use the Typer CLI in `src/factuality_rerank_xsum/cli/` as the canonical stage surface and keep durable behavior in `src/`. Tests live in `tests/unit/`, configs in `configs/`, research docs in `docs/`, notebooks in `notebooks/`, and tracked outputs in `artifacts/`, `outputs/final/`, `data/processed/splits/`, and `VERSIONS.md`.

## Build, Test, and Development Commands

Use `uv` for all environment and execution work.

- `uv sync --locked --dev`: install the exact CI dependency set.
- `make env`, `make smoke`, `make data`, `make train`, `make generate`, `make score`, `make search`, `make eval`, `make audit`, `make figures`, `make results-summary`, `make package`: run the canonical stage flow through the CLI.
- `uv run factuality-rerank-xsum <command>`: use the repo CLI for targeted stages such as `generate`, `score`, `figures`, `results-summary`, or `package`.
- `uv run ruff check && uv run ruff format --check && uv run mypy . && uv run pytest`: run the full local gate set used by CI.

## Environment & Validation Contract

Use Python `3.12` for the local `uv` `.venv`. CI also supports `3.11` and `3.13`. Treat `uv` as required. For a full online rerun, split `online` and `metrics` environments because legacy SummaC conflicts with the modern Hugging Face stack.

- Before acting on local GPU, CUDA, training, or local inference tasks, consult `~/.codex/LOCAL_WORKSTATION.md` first.

## Plugin, MCP, and Tool Routing

Default stack for work in this repo: `$python-expert` + `$hugging-face` + `$github`.

- Route every Python task through `$python-expert` first. Use it as the front-door router, then bias the work toward one lane: core architecture and typing, API and contract design, async and concurrency, testing, toolchain and packaging, or performance and profiling.
- Use `$hugging-face` for model, dataset, paper, Hub, Space, Transformers, TRL, training, inference, evaluation, and ML research work. Prefer it for experiment planning, model-facing implementation, and result interpretation.
- Use `$github` for repository metadata, issues, PRs, review threads, Actions, release flows, and `gh`-driven collaboration or publish tasks.
- Use `$technical-writing` for `README.md`, `docs/`, runbooks, system cards, results summaries, specs, and submission-facing documentation.
- Use `$root-cause-finder` for debugging and code review. Prove the intended path, identify the first unintended side effect, and prefer upstream logic fixes over permissive downstream contract changes.
- Use `$opensrc-inspect` when docs and types are not enough and source-level dependency or upstream inspection changes the recommendation. Cite exact versions and local source paths.
- Use `$agents-md-maintainer` after durable workflow, tooling, contract, or output changes to decide whether `AGENTS.md` needs the smallest valid repo-wide update.

## Research, Search, and Delegation

- Prefer official docs first. Use `context7` for version-specific library and framework docs, `exa` for fresh multi-source external research, and `zen` for structured analysis on high-impact or ambiguous decisions.
- Use `web.run` for live web lookup, source attribution, and latest-state verification. Search first, then `open`, `find`, and `click` only as needed.
- Use `functions.exec_command` with `rg` for local codebase discovery. Use `git grep` only when git-tracked scope matters.
- For nontrivial work, keep a short explicit plan with `functions.update_plan`.
- Use `functions.request_user_input` only when assumptions are risky, breaking, or hard to reverse.
- Spawn subagents only for bounded, disjoint tasks. Give each one explicit ownership, concrete outputs, and clear do and do not constraints.
- Use `functions.send_message` or `functions.followup_task` to continue an active agent instead of spawning overlapping work.
- Use `functions.wait_agent` and `functions.close_agent` to finish and clean up delegation. Do not synthesize or finalize until every active subagent has finished or been explicitly closed.
- Integrate returned subagent results before delegating overlapping follow-up work.

## Coding Style & Naming Conventions

Target Python `3.11+` with 4-space indentation, explicit typing, and small, composable functions. Ruff enforces style and import order with a `100` character line length; mypy runs in strict mode. Use snake_case for modules, functions, config files, YAML keys, and CLI helper functions.

## Testing Guidelines

Write deterministic `pytest` unit tests in `tests/unit/test_*.py`. Prefer direct coverage of fusion, scorer, fixture, and pipeline helpers over notebook-only validation. Keep tests offline-safe where possible; the checked-in workflow depends on fixture-backed fallback paths when networked model access is unavailable.

## Research Workflow & Artifact Rules

This repository intentionally tracks generated research outputs. Do not hand-edit or casually regenerate files under `artifacts/`, `outputs/final/`, `data/processed/splits/`, or `VERSIONS.md`; if regeneration is required, mention it explicitly in the PR. The `uv run factuality-rerank-xsum minicheck-optional` stage is optional and is not part of the main `make` scoring path. The current checked-in results reflect an offline fallback run, not a full online XSum benchmark.

Required final deliverables live under `outputs/final/`, including `main_metrics.csv`, `ablation_metrics.csv`, `pareto_points.csv`, `bootstrap_cis.json`, `manual_audit.csv`, `manual_audit_summary.json`, `figures/`, `tables/`, and `system_card.md`. The packaged handoff is not complete until those outputs, the packaged zip, and the summary docs all agree.

Notebooks are secondary analysis surfaces. Use them to inspect saved artifacts and regenerate figures, but keep required experiment logic in the CLI and `src/`.

## Documentation & Claims

Keep claims aligned with `docs/CLAIMS_SAFE_TO_WRITE.md`. If a change affects generated outputs or the execution story, update `README.md`, `docs/RESULTS_SUMMARY.md`, and `docs/SUBMISSION_CHECKLIST.md` in the same pass. If the run used the offline fixture fallback, say so plainly and avoid benchmark-level claims.

## Commit & Pull Request Guidelines

Use scoped conventional commits and semantically group uncommitted changes into reviewable commits, and use semantic scoped conventional commit/SEMVER style PR titles. PRs should state the problem, and call out any changes to tracked outputs, docs claims, or pipeline stages and describe the commits. Keep claims aligned with `docs/CLAIMS_SAFE_TO_WRITE.md`; do not overstate benchmark or model-execution results.
