"""Final reporting artifacts: figures, tables, and system card."""

from __future__ import annotations

import shutil
from typing import Any

import pandas as pd

from factuality_rerank_xsum.artifacts.layout import comparison_table_path
from factuality_rerank_xsum.constants import (
    BASELINE_SYSTEM,
    BEST_BALANCED,
    BEST_FACTUALITY,
    BEST_SIMPLE,
)
from factuality_rerank_xsum.runtime.manifests import runtime_contract
from factuality_rerank_xsum.utils.io import write_text
from factuality_rerank_xsum.utils.paths import artifact_path, output_path
from factuality_rerank_xsum.viz.plots import (
    make_pipeline_diagram,
    plot_beam_tradeoff,
    plot_component_ablation,
    plot_error_taxonomy,
    plot_metric_vs_human_scatter,
    plot_pareto,
)


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a small dataframe as a Markdown table.

    Args:
        frame: Tabular values to serialize as a compact Markdown table.

    Returns:
        The Markdown table string with one header row and one row per record.
    """

    headers = list(frame.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in frame.iterrows():
        values = [str(row[column]) for column in headers]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def qualitative_case_lines(title: str, frame: pd.DataFrame) -> list[str]:
    """Render qualitative examples for report markdown files.

    Args:
        title: Markdown heading used for the examples section.
        frame: Qualitative example rows with IDs, summaries, and deltas.

    Returns:
        The Markdown lines for the rendered examples section.
    """

    lines = [f"# {title}", ""]
    for _, row in frame.iterrows():
        lines.extend(
            [
                f"## {row['id']}",
                f"- Reference: {row['reference']}",
                f"- Baseline: {row['baseline_summary']}",
                f"- Reranked: {row['reranked_summary']}",
                f"- Factuality delta: {row['factuality_delta']:.4f}",
                "",
            ]
        )
    return lines


def system_card_lines(runtime: dict[str, Any]) -> list[str]:
    """Render the final system card from the runtime contract.

    Args:
        runtime: Runtime contract payload containing requested assets, executed
            modes, and online-execution status.

    Returns:
        The Markdown lines for the final system card.
    """

    requested = runtime["requested"]
    execution_note = (
        "The repository is configured for the public Hugging Face runtime path."
        if runtime["online_execution"]
        else (
            "Current outputs should be read together with the executed dataset and configured "
            "generator modes in the manifests."
        )
    )
    return [
        "# System card",
        "",
        "- Configured study: XSum factuality-aware reranking with public Hugging Face assets.",
        (
            f"- Requested assets: dataset `{requested['dataset_name']}`, generator "
            f"`{requested['generator_model']}`, FactCC `{requested['factcc_model']}`, "
            f"NLI `{requested['nli_model']}`."
        ),
        f"- Executed dataset mode: `{runtime['dataset_mode']}`.",
        f"- Requested generator mode: `{requested['generator_mode']}`.",
        f"- Executed generator mode: `{runtime['generator_mode']}`.",
        (
            "- Intended use: reproducible reranking runs, artifact inspection, "
            "report writing, and submission QA over tracked outputs."
        ),
        f"- {execution_note}",
    ]


def run_make_tables_and_figures() -> None:
    """Build report-ready tables, figures, examples, and system card outputs."""

    final_root = output_path("final")
    final_root.mkdir(parents=True, exist_ok=True)
    metrics = pd.read_csv(artifact_path("eval", "system_metrics.csv"))
    main_metrics = metrics[
        metrics["system"].isin([BASELINE_SYSTEM, BEST_BALANCED, BEST_FACTUALITY, BEST_SIMPLE])
    ].copy()
    main_metrics.to_csv(output_path("final", "main_metrics.csv"), index=False)

    ablation_order = [
        "logprob_only_beam_4",
        "logprob_only_beam_8",
        "logprob_only_beam_16",
        "summac_only",
        "factcc_only",
        "logprob_plus_summac",
        "logprob_plus_factcc",
        "summac_plus_factcc",
        "logprob_plus_summac_plus_factcc",
        "logprob_plus_summac_plus_factcc_plus_entity_support",
    ]
    ablation = metrics[
        (metrics["split"] == "test_final") & (metrics["system"].isin(ablation_order))
    ].copy()
    ablation = (
        ablation.set_index("system")
        .loc[[name for name in ablation_order if name in set(ablation["system"])]]
        .reset_index()
    )
    ablation.to_csv(output_path("final", "ablation_metrics.csv"), index=False)

    pareto = pd.read_csv(artifact_path("search", "pareto_points.csv"))
    pareto.to_csv(output_path("final", "pareto_points.csv"), index=False)
    shutil.copy2(
        artifact_path("eval", "bootstrap_cis.json"),
        output_path("final", "bootstrap_cis.json"),
    )

    audit = pd.read_csv(artifact_path("audit", "manual_audit_completed.csv"))
    audit_summary = pd.read_csv(artifact_path("audit", "audit_taxonomy_table.csv"))
    audit.to_csv(output_path("final", "manual_audit.csv"), index=False)
    shutil.copy2(
        artifact_path("audit", "manual_audit_summary.json"),
        output_path("final", "manual_audit_summary.json"),
    )

    make_pipeline_diagram(output_path("final", "figures", "pipeline_diagram.png"))
    plot_pareto(pareto, output_path("final", "figures", "pareto_frontier.png"))

    beam_tradeoff = metrics[
        (metrics["split"] == "test_final")
        & (
            metrics["system"].isin(
                ["logprob_only_beam_4", "logprob_only_beam_8", "logprob_only_beam_16"]
            )
        )
    ].copy()
    beam_tradeoff["beam_size"] = (
        beam_tradeoff["system"].str.extract(r"(\d+)", expand=False).astype(int)
    )
    plot_beam_tradeoff(
        beam_tradeoff[["beam_size", "rougeLsum", "factuality_composite"]],
        output_path("final", "figures", "beam_tradeoff.png"),
    )
    plot_component_ablation(ablation, output_path("final", "figures", "component_ablation.png"))
    plot_error_taxonomy(audit_summary, output_path("final", "figures", "error_taxonomy.png"))

    comparison = pd.read_csv(comparison_table_path("test_final"))
    scatter_frame = audit.merge(
        comparison[["id", "reranked_factcc_style_score"]], on="id", how="left"
    )
    plot_metric_vs_human_scatter(
        scatter_frame,
        output_path("final", "figures", "metric_vs_human_scatter.png"),
    )

    report_tables = [
        "# Report-ready tables",
        "",
        "## Main metrics",
        "",
        markdown_table(main_metrics.round(4)),
        "",
        "## Ablation metrics",
        "",
        markdown_table(ablation.round(4)),
        "",
        "## Audit taxonomy",
        "",
        markdown_table(audit_summary),
    ]
    write_text(output_path("final", "tables", "report_tables.md"), "\n".join(report_tables))

    gains = comparison.copy()
    gains["factuality_delta"] = (
        gains["reranked_factuality_composite"] - gains["baseline_factuality_composite"]
    )
    qualitative = gains.sort_values("factuality_delta", ascending=False)
    qualitative[
        [
            "id",
            "reference",
            "baseline_summary",
            "reranked_summary",
            "baseline_factuality_composite",
            "reranked_factuality_composite",
            "factuality_delta",
        ]
    ].to_csv(output_path("final", "tables", "qualitative_examples.csv"), index=False)
    audit_summary.to_csv(output_path("final", "tables", "audit_taxonomy_table.csv"), index=False)

    success_lines = qualitative_case_lines("Success cases", qualitative.head(3))
    failure_lines = qualitative_case_lines("Failure cases", qualitative.tail(3))
    write_text(output_path("final", "examples_success.md"), "\n".join(success_lines))
    write_text(output_path("final", "examples_failures.md"), "\n".join(failure_lines))

    runtime = runtime_contract()
    write_text(output_path("final", "system_card.md"), "\n".join(system_card_lines(runtime)))
