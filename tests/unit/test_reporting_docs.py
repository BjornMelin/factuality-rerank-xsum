from __future__ import annotations

from typing import Any

import pandas as pd

from factuality_rerank_xsum.reporting.docs import (
    STAGE_COMMANDS,
    ReportContext,
    fenced_runtime_commands,
    ordered_runtime_commands,
    readme_lines,
    results_summary_lines,
    runbook_lines,
    submission_checklist_lines,
)


def make_report_context(
    *, dataset_mode: str = "online_hub", generator_mode: str = "huggingface_generation"
) -> ReportContext:
    metrics = pd.DataFrame(
        [
            {
                "split": "test_final",
                "system": "baseline_best_likelihood",
                "rougeLsum": 0.31,
                "factuality_composite": 0.44,
            },
            {
                "split": "test_final",
                "system": "best_balanced",
                "rougeLsum": 0.34,
                "factuality_composite": 0.58,
            },
        ]
    )
    runtime: dict[str, Any] = {
        "requested": {
            "dataset_name": "EdinburghNLP/xsum",
            "dataset_revision": "rev-ds",
            "generator_model": "facebook/bart-large-xsum",
            "generator_revision": "rev-gen",
            "factcc_model": "manueldeprada/FactCC",
            "factcc_revision": "rev-factcc",
            "nli_model": "microsoft/deberta-large-mnli",
            "nli_revision": "rev-nli",
        },
        "dataset_manifest": {
            "dataset_revision_requested": "rev-ds",
            "dataset_revision_resolved": "resolved-ds",
            "rows_available": 1024,
            "note": "dataset loaded from hub",
        },
        "model_manifest": {
            "baseline_revision_requested": "rev-gen",
            "baseline_revision_resolved": "resolved-gen",
            "factcc_revision_requested": "rev-factcc",
            "factcc_revision_resolved": "resolved-factcc",
            "nli_revision_requested": "rev-nli",
            "nli_revision_resolved": "resolved-nli",
            "reason": "generator loaded from transformers",
        },
        "env_report": {"mode": "online_hf_ready"},
        "dataset_mode": dataset_mode,
        "generator_mode": generator_mode,
    }
    return ReportContext(
        runtime=runtime,
        requested=runtime["requested"],
        dataset_manifest=runtime["dataset_manifest"],
        model_manifest=runtime["model_manifest"],
        env_report=runtime["env_report"],
        metrics=metrics,
        bootstrap={
            "rougeLsum": {"ci_low": -0.01, "ci_high": 0.05},
            "factuality_composite": {"ci_low": 0.04, "ci_high": 0.11},
        },
        audit_summary={
            "rows": 12,
            "baseline_consistent_rate": 0.42,
            "reranked_consistent_rate": 0.75,
        },
        best_config={
            "system": "best_balanced",
            "beam_size": 8,
            "normalization": "zscore",
            "weights": {"logprob": 0.4, "summac": 0.3, "factcc": 0.3},
        },
        selected=metrics.iloc[1],
        baseline=metrics.iloc[0],
    )


def test_runtime_command_helpers_keep_cli_only_contract() -> None:
    assert fenced_runtime_commands() == [
        "```bash",
        "uv sync --locked --dev",
        *STAGE_COMMANDS,
        "```",
    ]
    assert ordered_runtime_commands()[0] == "1. `uv sync --locked --dev`"
    assert ordered_runtime_commands()[-1] == "10. `uv run factuality-rerank-xsum package`"


def test_results_summary_lines_report_runtime_and_cli_commands() -> None:
    lines = results_summary_lines(make_report_context())
    rendered = "\n".join(lines)

    assert "Environment mode: `online_hf_ready`." in rendered
    assert "Dataset mode executed: `online_hub`." in rendered
    assert "Generator mode currently configured: `huggingface_generation`." in rendered
    assert "resolved to `resolved-gen`" in rendered
    assert "uv run factuality-rerank-xsum package" in rendered
    assert "scripts/14_make_tables_and_figures.py" not in rendered


def test_readme_lines_reflect_cli_first_authority() -> None:
    context = make_report_context()
    readme = "\n".join(readme_lines(context))

    assert "CLI-first stage pipeline" in readme
    assert "maintained prompt pack in `prompts/`" in readme
    assert "Preserved prompts, plans, and references from the handoff bundle." not in readme


def test_runbook_and_checklist_reflect_runtime_modes() -> None:
    runbook = "\n".join(runbook_lines())
    checklist = "\n".join(
        submission_checklist_lines(
            make_report_context(dataset_mode="fixture_preview", generator_mode="offline_surrogate")
        )
    )

    assert "1. `uv sync --locked --dev`" in runbook
    assert "10. `uv run factuality-rerank-xsum package`" in runbook
    assert "- [ ] Dataset stage executed in `online_hub` mode." in checklist
    assert "- [ ] Generator stage executed in `huggingface_generation` mode." in checklist
