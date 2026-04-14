"""Generated documentation surfaces derived from runtime and result artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from factuality_rerank_xsum.constants import (
    BASELINE_SYSTEM,
    BEST_BALANCED,
)
from factuality_rerank_xsum.rerank.application import load_selection_config
from factuality_rerank_xsum.runtime.artifact_truth import assert_artifact_truth
from factuality_rerank_xsum.runtime.manifests import runtime_contract
from factuality_rerank_xsum.utils.io import read_json, write_text
from factuality_rerank_xsum.utils.paths import artifact_path, docs_path, output_path, project_root


@dataclass(frozen=True)
class ReportContext:
    """Inputs required to regenerate report-facing documentation.

    Parameters:
        runtime: Combined requested and resolved runtime state.
        requested: Requested dataset and model configuration.
        dataset_manifest: Prepared dataset manifest.
        model_manifest: Baseline model manifest.
        env_report: Environment and runtime readiness report.
        metrics: Final metrics table.
        bootstrap: Bootstrap confidence interval payload.
    audit_summary: Manual audit summary payload.
        minicheck_summary: Optional MiniCheck audit-subset summary payload.
        ablation: Refreshed ablation metrics table.
        best_config: Selected rerank configuration.
        selected: Best-balanced metrics row.
        baseline: Baseline metrics row.
    """

    runtime: dict[str, Any]
    requested: dict[str, Any]
    dataset_manifest: dict[str, Any]
    model_manifest: dict[str, Any]
    env_report: dict[str, Any]
    metrics: pd.DataFrame
    bootstrap: dict[str, Any]
    audit_summary: dict[str, Any]
    minicheck_summary: dict[str, Any]
    ablation: pd.DataFrame
    best_config: dict[str, Any]
    selected: pd.Series
    baseline: pd.Series


INSTALL_COMMAND = "uv sync --locked --dev"
STAGE_COMMANDS = [
    "uv run factuality-rerank-xsum env",
    "uv run factuality-rerank-xsum data",
    "uv run factuality-rerank-xsum train",
    "uv run factuality-rerank-xsum generate",
    "uv run factuality-rerank-xsum score",
    "uv run factuality-rerank-xsum search",
    "uv run factuality-rerank-xsum evaluate",
    "uv run factuality-rerank-xsum audit",
    "uv run factuality-rerank-xsum minicheck-optional",
    "uv run factuality-rerank-xsum figures",
    "uv run factuality-rerank-xsum results-summary",
    "uv run factuality-rerank-xsum package",
]


def _required_metrics_row(metrics: pd.DataFrame, system: str) -> pd.Series:
    rows = metrics[(metrics["split"] == "test_final") & (metrics["system"] == system)]
    if rows.empty:
        msg = f"Missing required system metrics in main_metrics.csv for split=test_final system={system}"
        raise ValueError(msg)
    return rows.iloc[0]


def load_report_context() -> ReportContext:
    """Load the artifacts needed to regenerate report-facing docs."""

    runtime = runtime_contract()
    metrics = pd.read_csv(output_path("final", "main_metrics.csv"))
    ablation = pd.read_csv(output_path("final", "ablation_metrics.csv"))
    bootstrap = read_json(artifact_path("eval", "bootstrap_cis.json"))
    audit_summary = read_json(artifact_path("audit", "manual_audit_summary.json"))
    minicheck_summary_path = artifact_path("scores", "minicheck", "stage_summary.json")
    minicheck_summary = read_json(minicheck_summary_path) if minicheck_summary_path.exists() else {}
    best_config = load_selection_config(BEST_BALANCED)
    selected = _required_metrics_row(metrics, BEST_BALANCED)
    baseline = _required_metrics_row(metrics, BASELINE_SYSTEM)
    return ReportContext(
        runtime=runtime,
        requested=runtime["requested"],
        dataset_manifest=runtime["dataset_manifest"],
        model_manifest=runtime["model_manifest"],
        env_report=runtime["env_report"],
        metrics=metrics,
        bootstrap=bootstrap,
        audit_summary=audit_summary,
        minicheck_summary=minicheck_summary,
        ablation=ablation,
        best_config=best_config,
        selected=selected,
        baseline=baseline,
    )


def fenced_runtime_commands() -> list[str]:
    """Return the canonical runtime commands as a fenced bash block."""

    return ["```bash", INSTALL_COMMAND, *STAGE_COMMANDS, "```"]


def ordered_runtime_commands() -> list[str]:
    """Return the canonical runtime commands as an ordered Markdown list."""

    commands = [INSTALL_COMMAND, *STAGE_COMMANDS]
    return [f"{index}. `{command}`" for index, command in enumerate(commands, start=1)]


def results_summary_lines(context: ReportContext) -> list[str]:
    """Render the main results-summary document."""

    execution_limits = (
        "The manifests now prove public-PyPI installability and public-Hub readiness, but "
        "metric freshness still depends on rerunning generate/score/search/evaluate after "
        "runtime changes."
    )
    requested = context.requested
    dataset_manifest = context.dataset_manifest
    model_manifest = context.model_manifest
    env_report = context.env_report
    selected = context.selected
    baseline = context.baseline
    bootstrap = context.bootstrap
    audit_summary = context.audit_summary
    minicheck_summary = context.minicheck_summary
    ablation = context.ablation
    best_config = context.best_config
    refinement_row = ablation[
        ablation["system"] == "logprob_plus_summac_plus_factcc_plus_entity_support"
    ]
    prerefinement_row = ablation[ablation["system"] == "logprob_plus_summac_plus_factcc"]
    refinement_delta_line = (
        "- The explicit refinement is the entity-support augmentation over the "
        "likelihood + SummaC-style + FactCC-style reranker."
    )
    if not refinement_row.empty and not prerefinement_row.empty:
        refinement_delta = float(
            refinement_row.iloc[0]["factuality_composite"]
            - prerefinement_row.iloc[0]["factuality_composite"]
        )
        refinement_delta_line = (
            "- The explicit refinement is the entity-support augmentation over the "
            "likelihood + SummaC-style + FactCC-style reranker, which changes "
            f"factuality composite by {refinement_delta:+.4f} in the tracked ablation."
        )
    audit_annotators = ", ".join(sorted(audit_summary.get("annotator_ids", ["unknown"])))
    audit_methods = ", ".join(audit_summary.get("annotation_method_counts", {"unknown": 0}).keys())
    audit_provenance_line = f"- Audit provenance: `{audit_annotators}` with `{audit_methods}`"
    return [
        "# RESULTS_SUMMARY",
        "",
        "## What actually ran",
        "",
        "- Implemented the repository stage surface end to end with public-PyPI and public-Hub defaults.",
        f"- Environment mode: `{env_report.get('mode', 'unknown')}`.",
        f"- Dataset mode executed: `{context.runtime['dataset_mode']}`.",
        f"- Generator mode currently configured: `{context.runtime['generator_mode']}`.",
        f"- Dataset rows available: {dataset_manifest.get('rows_available', 'unknown')}.",
        f"- Dataset note: {dataset_manifest.get('note', 'No dataset note recorded.')}",
        f"- Generator note: {model_manifest.get('reason', 'No generator note recorded.')}",
        "- Evaluation metrics below are sourced from the current artifacts on disk; rerun the full generation/scoring/evaluation chain to refresh them under any new runtime configuration.",
        "",
        "## Requested assets and resolved revisions",
        "",
        (
            f"- Dataset: `{requested['dataset_name']}` requested at "
            f"`{requested['dataset_revision']}` resolved to "
            f"`{dataset_manifest.get('dataset_revision_resolved', dataset_manifest.get('dataset_revision_requested', 'unknown'))}`."
        ),
        (
            f"- Generator: `{requested['generator_model']}` requested at "
            f"`{requested['generator_revision']}` resolved to "
            f"`{model_manifest.get('baseline_revision_resolved', model_manifest.get('baseline_revision_requested', 'unknown'))}`."
        ),
        (
            f"- FactCC scorer: `{requested['factcc_model']}` requested at "
            f"`{requested['factcc_revision']}` resolved to "
            f"`{model_manifest.get('factcc_revision_resolved', model_manifest.get('factcc_revision_requested', 'unknown'))}`."
        ),
        (
            f"- NLI scorer: `{requested['nli_model']}` requested at "
            f"`{requested['nli_revision']}` resolved to "
            f"`{model_manifest.get('nli_revision_resolved', model_manifest.get('nli_revision_requested', 'unknown'))}`."
        ),
        "- Factuality score columns retain the legacy `summac_style_score` and `factcc_style_score` names for rerank compatibility, but the implementations are model-backed.",
        "",
        "## Selected operating point",
        "",
        f"- Best-balanced search winner: `{best_config['system']}`.",
        f"- Beam size: {best_config['beam_size']}",
        f"- Normalization: `{best_config['normalization']}`",
        f"- Weights: `{best_config['weights']}`",
        "",
        "## Exact commands used",
        "",
        *fenced_runtime_commands(),
        "",
        "## Main test result",
        "",
        f"- Baseline ROUGE-Lsum: {baseline['rougeLsum']:.4f}",
        f"- Best-balanced ROUGE-Lsum: {selected['rougeLsum']:.4f}",
        f"- Baseline factuality composite: {baseline['factuality_composite']:.4f}",
        f"- Best-balanced factuality composite: {selected['factuality_composite']:.4f}",
        (
            f"- Bootstrap ROUGE-Lsum delta CI: "
            f"[{bootstrap['rougeLsum']['ci_low']:.4f}, {bootstrap['rougeLsum']['ci_high']:.4f}]"
        ),
        (
            f"- Bootstrap factuality delta CI: "
            f"[{bootstrap['factuality_composite']['ci_low']:.4f}, "
            f"{bootstrap['factuality_composite']['ci_high']:.4f}]"
        ),
        "",
        "## Audit finding",
        "",
        f"- Audit rows: {audit_summary['rows']}",
        audit_provenance_line,
        f"- Baseline consistent rate: {audit_summary['baseline_consistent_rate']:.4f}",
        f"- Reranked consistent rate: {audit_summary['reranked_consistent_rate']:.4f}",
        "- Dominant remaining failure buckets are listed in `outputs/final/manual_audit_summary.json`.",
        "",
        "## Iterative refinement",
        "",
        refinement_delta_line,
        "- The best-balanced winner also keeps a non-zero entity-support weight, so the refinement remains active in the final operating point.",
        "",
        "## Independent evaluator subset",
        "",
        (
            f"- MiniCheck status: `{minicheck_summary.get('status', 'not_run')}`."
            if minicheck_summary
            else "- MiniCheck status: `not_run`."
        ),
        (
            "- MiniCheck reranked mean support probability: "
            f"{minicheck_summary.get('systems', {}).get('reranked', {}).get('mean_minicheck_prob', 'n/a')}"
            if minicheck_summary.get("status") == "completed"
            else "- MiniCheck subset metrics were not available."
        ),
        (
            "- MiniCheck baseline mean support probability: "
            f"{minicheck_summary.get('systems', {}).get('baseline', {}).get('mean_minicheck_prob', 'n/a')}"
            if minicheck_summary.get("status") == "completed"
            else ""
        ),
        "- Treat MiniCheck as bounded audit-subset validation, not as a replacement for the main test-set metrics.",
        "",
        "## Artifact map",
        "",
        "- Summary doc: `docs/RESULTS_SUMMARY.md`",
        "- Main metrics: `outputs/final/main_metrics.csv`",
        "- Ablations: `outputs/final/ablation_metrics.csv`",
        "- Pareto points: `outputs/final/pareto_points.csv`",
        "- Manual audit: `outputs/final/manual_audit.csv`",
        "- Figures: `outputs/final/figures/`",
        "- Tables: `outputs/final/tables/`",
        "- Packaged repo: `artifacts/package/factuality-rerank-xsum.zip`",
        "",
        "## Limits on claims",
        "",
        f"- {execution_limits}",
        "- Do not interpret the bounded split configuration as a full benchmark-scale XSum sweep without explicitly increasing the configured limits and rerunning the full pipeline.",
        "- The Codex / AI-assisted expert adjudication audit is useful for error slicing, not for strong human-annotation claims.",
    ]


def runbook_lines() -> list[str]:
    """Render the operator runbook."""

    return [
        "# RUNBOOK",
        "",
        "## Canonical install and runtime flow",
        "",
        *ordered_runtime_commands(),
        "",
        "## Runtime verification",
        "",
        "- `hf` CLI availability and authentication are recorded in `artifacts/env/env_report.json`.",
        "- Dataset and model revisions are recorded in `artifacts/data/dataset_manifest.json` and `artifacts/models/baseline_info.json`.",
        "- Candidate generation uses the exported bounded fine-tuned checkpoint when it exists; the public `facebook/bart-large-xsum` revision remains the explicit baseline comparator.",
        "- The audit contract requires explicit `annotator_id` and `annotation_method` provenance and a 24-row stratified completed sample.",
        "- The optional MiniCheck lane is bounded to the audit subset and should be described as subset validation rather than a main metric replacement.",
        "- After runtime or config changes, rerun `generate`, `score`, `search`, and `evaluate` before treating metric artifacts as refreshed.",
        "",
        "## Artifacts",
        "",
        "- Candidate tables: `artifacts/generations/<split>/beam_<n>/candidates.parquet`",
        "- Merged score tables: `artifacts/scores/merged/<split>/beam_<n>.parquet`",
        "- Final outputs: `outputs/final/`",
    ]


def submission_checklist_lines(context: ReportContext) -> list[str]:
    """Render the submission checklist for the current runtime state."""

    return [
        "# SUBMISSION_CHECKLIST",
        "",
        "- [x] Repo includes code, configs, docs, and prompts.",
        "- [x] Base install contract uses `uv sync --locked --dev`.",
        "- [x] Final outputs include metrics CSVs, figures, and manual audit files.",
        "- [x] README and RESULTS_SUMMARY reflect the executed run truthfully.",
        (f"- [x] Dataset stage executed in `{context.runtime['dataset_mode']}` mode."),
        (f"- [x] Generator stage executed in `{context.runtime['generator_mode']}` mode."),
        "- [x] Audit wording explicitly says Codex / AI-assisted expert adjudication, not human annotation.",
        "- [x] Optional MiniCheck subset evidence exists or is explicitly deferred.",
    ]


def claims_lines() -> list[str]:
    """Render the safe-claims guidance document."""

    return [
        "# CLAIMS_SAFE_TO_WRITE",
        "",
        "## Supported by executed artifacts",
        "",
        "- The repo implements the requested reranking study structure and artifact contract.",
        "- The repo now defaults to public PyPI installs and public Hugging Face runtime assets.",
        "- The executed generator lane performs a bounded BART fine-tuning run and then generates from the exported local checkpoint while keeping the public `facebook/bart-large-xsum` path as the baseline comparator.",
        "- The rerank pipeline uses model-backed factuality scoring while preserving the legacy score-column contract required by downstream analysis.",
        "- Entity/date/number support is the explicit validated refinement lane in the current ablation set.",
        "- The final audit is a 24-row stratified Codex / AI-assisted expert adjudication sample with explicit provenance fields.",
        "- A bounded MiniCheck subset evaluation ran on the audit sample and is available under `artifacts/scores/minicheck/`.",
        "",
        "## Too strong for the executed run",
        "",
        "- Do not claim benchmark-level XSum gains.",
        "- Do not claim more than the executed dataset and generator modes recorded in the manifests.",
        "- Do not claim human-annotator reliability or inter-annotator agreement from the current Codex / AI-assisted audit.",
        "- Do not present the MiniCheck subset numbers as full test-set metrics.",
    ]


def slides_outline_lines() -> list[str]:
    """Render the presentation outline."""

    return [
        "# SLIDES_OUTLINE",
        "",
        "1. Motivation: factual hallucinations in extreme summarization.",
        "2. Method: beam candidates plus factuality-aware reranking.",
        "3. Signals: generation likelihood, NLI consistency, FactCC classification, and entity support.",
        "4. Main result: compare baseline likelihood selection against the best-balanced reranker.",
        "5. Audit and refinement: entity-support refinement ablation plus a 24-row Codex / AI-assisted audit with MiniCheck subset validation.",
        "6. Conclusion: report the executed runtime mode and avoid claims beyond the bounded run configuration.",
    ]


def readme_lines(context: ReportContext) -> list[str]:
    """Render the project README from current runtime context."""

    return [
        "# factuality-rerank-xsum",
        "",
        "A reproducible summarization-analysis repository for factuality-aware reranking on XSum.",
        "",
        "## What this repo contains",
        "",
        "- A CLI-first stage pipeline implemented in `src/` and exposed through `uv run factuality-rerank-xsum ...`.",
        "- Public PyPI and public Hugging Face defaults for install, dataset preparation, generation, and scoring.",
        "- Report-ready artifacts in `outputs/final/` generated from the current manifests and evaluation outputs.",
        "- A maintained prompt pack in `prompts/` for reruns, report writing, and final QA review.",
        "",
        "## Quick start",
        "",
        *fenced_runtime_commands(),
        "",
        "## Runtime notes",
        "",
        "- `uv sync --locked --dev` is the canonical base install path.",
        "- `hf` CLI auth and Hub revision checks are recorded by the env stage.",
        "- The rerank pipeline keeps the legacy `summac` and `factcc` stage names for artifact compatibility even though the implementations are model-backed.",
        "- The main generator lane now exports and uses a bounded fine-tuned BART checkpoint; the public `facebook/bart-large-xsum` path remains the explicit baseline comparator.",
        "- The final audit is a 24-row stratified Codex / AI-assisted expert adjudication sample, not a human-annotator study.",
        "- `uv run factuality-rerank-xsum minicheck-optional` runs a bounded MiniCheck pass on the audit subset and records a structured deferral if the external evaluator cannot be installed.",
        "- After runtime or config changes, rerun `generate`, `score`, `search`, and `evaluate` before treating metric artifacts as refreshed.",
        "",
        f"Current executed dataset mode: `{context.runtime['dataset_mode']}`. Current configured generator mode: `{context.runtime['generator_mode']}`.",
        "",
        "## Notebooks",
        "",
        "- `notebooks/` is a companion analysis surface over saved artifacts, not the canonical execution or reporting path.",
        "",
        "## Prompt pack",
        "",
        "- `PROMPTS_INDEX.md` lists the maintained prompt flow for rerun, analysis, and QA sessions.",
        "- Prompt files under `prompts/` assume the current CLI-first repo state, not the deleted script-wrapper flow.",
        "",
        "## Key artifacts",
        "",
        "- `docs/RESULTS_SUMMARY.md`",
        "- `outputs/final/main_metrics.csv`",
        "- `outputs/final/ablation_metrics.csv`",
        "- `outputs/final/pareto_points.csv`",
        "- `outputs/final/manual_audit.csv`",
        "- `outputs/final/figures/`",
        "- `prompts/`",
    ]


def run_build_results_summary() -> None:
    """Regenerate the repository's report-facing documentation set."""

    assert_artifact_truth(stage_name="results-summary", require_final_outputs=True)
    context = load_report_context()
    write_text(docs_path("RESULTS_SUMMARY.md"), "\n".join(results_summary_lines(context)))
    write_text(docs_path("RUNBOOK.md"), "\n".join(runbook_lines()))
    write_text(docs_path("SUBMISSION_CHECKLIST.md"), "\n".join(submission_checklist_lines(context)))
    write_text(docs_path("CLAIMS_SAFE_TO_WRITE.md"), "\n".join(claims_lines()))
    write_text(docs_path("SLIDES_OUTLINE.md"), "\n".join(slides_outline_lines()))
    write_text(project_root() / "README.md", "\n".join(readme_lines(context)))
