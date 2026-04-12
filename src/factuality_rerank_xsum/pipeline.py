from __future__ import annotations

import importlib.metadata
import platform
import shutil
import socket
import subprocess
import zipfile
from pathlib import Path
from typing import Any

import pandas as pd

from factuality_rerank_xsum.audit.taxonomy import build_audit_rows
from factuality_rerank_xsum.data.fixtures import ids_for_split, load_dataset_table, prepare_dataset
from factuality_rerank_xsum.eval.bootstrap import bootstrap_difference
from factuality_rerank_xsum.eval.metrics import enrich_with_rouge, metrics_for_selection
from factuality_rerank_xsum.generation.offline import generate_for_examples
from factuality_rerank_xsum.rerank.fusion import (
    fuse_scores,
    named_weight_configs,
    pareto_frontier,
    select_top_candidate,
    weight_grid,
)
from factuality_rerank_xsum.scorers.entity_support import score_dataframe as entity_score_dataframe
from factuality_rerank_xsum.scorers.factcc_style import score_dataframe as factcc_score_dataframe
from factuality_rerank_xsum.scorers.summac_style import score_dataframe as summac_score_dataframe
from factuality_rerank_xsum.utils.io import read_json, read_yaml, write_json, write_text, write_yaml
from factuality_rerank_xsum.utils.paths import (
    artifact_path,
    config_path,
    data_path,
    docs_path,
    output_path,
    project_root,
)
from factuality_rerank_xsum.viz.plots import (
    make_pipeline_diagram,
    plot_beam_tradeoff,
    plot_component_ablation,
    plot_error_taxonomy,
    plot_metric_vs_human_scatter,
    plot_pareto,
)

BASELINE_SYSTEM = "baseline_best_likelihood"
BEST_BALANCED = "best_balanced"
BEST_FACTUALITY = "best_factuality"
BEST_SIMPLE = "best_simple"


def _package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _check_dns(hostname: str) -> dict[str, str | bool]:
    try:
        socket.gethostbyname(hostname)
        return {"host": hostname, "resolvable": True, "error": ""}
    except OSError as exc:
        return {"host": hostname, "resolvable": False, "error": str(exc)}


def _uv_version() -> str:
    result = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=False)
    return result.stdout.strip() or result.stderr.strip()


def _config_beams() -> list[dict[str, Any]]:
    beams: list[dict[str, Any]] = []
    for name in ["beams_4.yaml", "beams_8.yaml", "beams_16.yaml"]:
        beams.append(read_yaml(config_path("generate", name)))
    return beams


def _candidate_table_path(split: str, beam_size: int) -> Path:
    return artifact_path("generations", split, f"beam_{beam_size}", "candidates.parquet")


def _score_table_path(stage: str, split: str, beam_size: int) -> Path:
    return artifact_path("scores", stage, split, f"beam_{beam_size}.parquet")


def _merged_table_path(split: str, beam_size: int) -> Path:
    return artifact_path("scores", "merged", split, f"beam_{beam_size}.parquet")


def _selected_table_path(split: str, system: str) -> Path:
    return artifact_path("eval", f"{split}_{system}_selected.parquet")


def _comparison_table_path(split: str) -> Path:
    return artifact_path("eval", f"{split}_comparison_table.csv")


def _example_rows(split: str) -> list[dict[str, str]]:
    frame = load_dataset_table()
    rows = frame[frame["id"].isin(ids_for_split(split))].copy()
    rows = rows.sort_values("id").reset_index(drop=True)
    examples: list[dict[str, str]] = []
    for _, row in rows.iterrows():
        examples.append(
            {
                "id": str(row["id"]),
                "document": str(row["document"]),
                "summary": str(row["summary"]),
            }
        )
    return examples


def _integrity_report(frame: pd.DataFrame, requested_ids: list[str]) -> dict[str, Any]:
    grouped = frame.groupby("id", as_index=False).size()
    return {
        "requested_ids": len(requested_ids),
        "observed_ids": int(grouped["id"].nunique()),
        "missing_ids": sorted(set(requested_ids) - set(frame["id"].astype(str))),
        "rows": int(len(frame)),
        "min_candidates_per_example": int(grouped["size"].min()),
        "max_candidates_per_example": int(grouped["size"].max()),
        "non_empty_summaries": bool(frame["summary"].astype(str).str.len().gt(0).all()),
        "has_nan_scores": bool(
            frame[["sequence_score_hf", "token_logprob_sum", "token_logprob_avg"]]
            .isna()
            .any()
            .any()
        ),
    }


def _markdown_table(frame: pd.DataFrame) -> str:
    headers = list(frame.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in frame.iterrows():
        values = [str(row[column]) for column in headers]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _load_selection_config(name: str) -> dict[str, Any]:
    return read_yaml(artifact_path("search", f"{name}.yaml"))


def _apply_system(
    split: str, *, system_name: str, beam_size: int, weights: dict[str, float], normalization: str
) -> pd.DataFrame:
    merged = pd.read_parquet(_merged_table_path(split, beam_size))
    fused = fuse_scores(merged, weights, normalization)
    selected = select_top_candidate(fused)
    selected = enrich_with_rouge(selected)
    selected["factuality_composite"] = selected[
        ["summac_style_score", "factcc_style_score", "entity_support_score"]
    ].mean(axis=1)
    selected["system"] = system_name
    selected["beam_size"] = beam_size
    selected["normalization"] = normalization
    _selected_table_path(split, system_name).parent.mkdir(parents=True, exist_ok=True)
    selected.to_parquet(_selected_table_path(split, system_name), index=False)
    selected.to_csv(artifact_path("eval", f"{split}_{system_name}_selected.csv"), index=False)
    return selected


def run_env_check() -> dict[str, Any]:
    report: dict[str, Any] = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "uv_version": _uv_version(),
        "package_versions": {
            package: _package_version(package)
            for package in [
                "jsonlines",
                "matplotlib",
                "mypy",
                "numpy",
                "pandas",
                "pyarrow",
                "pytest",
                "rich",
                "rouge-score",
                "ruff",
                "scikit-learn",
                "transformers",
                "datasets",
                "evaluate",
                "summac",
            ]
        },
        "dns_checks": [_check_dns("huggingface.co"), _check_dns("pypi.org")],
        "online_runtime_ready": False,
        "mode": "offline_fixture_fallback",
        "requested_online_path": {
            "dataset": "EdinburghNLP/xsum",
            "model": "facebook/bart-large-xsum",
            "factcc": "manueldeprada/FactCC",
        },
    }
    write_json(artifact_path("env", "env_report.json"), report)
    versions_md = "# VERSIONS.md\n\n"
    versions_md += f"- Python: `{report['python_version']}`\n"
    versions_md += f"- uv: `{report['uv_version']}`\n"
    versions_md += "- Runtime mode: `offline_fixture_fallback`\n"
    versions_md += "- DNS checks:\n"
    for row in report["dns_checks"]:
        versions_md += f"  - {row['host']}: resolvable={row['resolvable']} error=`{row['error']}`\n"
    versions_md += "\n## Installed package snapshot\n\n"
    for package, version in report["package_versions"].items():
        versions_md += f"- {package}: `{version}`\n"
    write_text(project_root() / "VERSIONS.md", versions_md)
    return report


def run_prepare_dataset() -> dict[str, Any]:
    prepared = prepare_dataset()
    preview = prepared.frame[["id", "summary"]].head(8)
    preview.to_csv(artifact_path("data", "dataset_preview.csv"), index=False)
    return {
        "mode": prepared.mode,
        "revision": prepared.revision,
        "rows": int(len(prepared.frame)),
    }


def run_train_or_load_bart() -> dict[str, Any]:
    payload = {
        "requested_baseline": "facebook/bart-large-xsum",
        "requested_factcc_checkpoint": "manueldeprada/FactCC",
        "actual_mode": "offline_surrogate_generator",
        "reason": (
            "The runtime could not fetch Hugging Face model files, so the executed run used a deterministic "
            "headline-style offline candidate generator while preserving the online hooks and config surface."
        ),
    }
    write_json(artifact_path("models", "baseline_info.json"), payload)
    return payload


def run_generate_candidates() -> dict[str, Any]:
    beams = _config_beams()
    splits = ["dev_smoke", "dev_small", "val_tune", "val_full", "test_final"]
    summary: dict[str, Any] = {"splits": {}, "beam_sizes": [beam["num_beams"] for beam in beams]}
    for split in splits:
        split_rows = _example_rows(split)
        summary["splits"][split] = {"examples": len(split_rows)}
        requested_ids = [row["id"] for row in split_rows]
        for beam in beams:
            generated = generate_for_examples(
                split_rows,
                split=split,
                num_beams=int(beam["num_beams"]),
                length_penalty=float(beam["length_penalty"]),
                no_repeat_ngram_size=int(beam["no_repeat_ngram_size"]),
                max_new_tokens=int(beam["max_new_tokens"]),
                min_new_tokens=int(beam["min_new_tokens"]),
            )
            frame = pd.DataFrame(generated)
            target = _candidate_table_path(split, int(beam["num_beams"]))
            target.parent.mkdir(parents=True, exist_ok=True)
            frame.to_parquet(target, index=False)
            frame.to_csv(target.with_suffix(".csv"), index=False)
            report = _integrity_report(frame, requested_ids)
            write_json(target.parent / "integrity_report.json", report)
    write_json(artifact_path("generations", "generation_summary.json"), summary)
    return summary


def _run_score_stage(stage: str) -> None:
    for split in ["dev_smoke", "dev_small", "val_tune", "val_full", "test_final"]:
        for beam in [4, 8, 16]:
            candidate_path = _candidate_table_path(split, beam)
            frame = pd.read_parquet(candidate_path)
            if stage == "summac":
                scored = summac_score_dataframe(frame)
            elif stage == "factcc":
                scored = factcc_score_dataframe(frame)
            elif stage == "entity_support":
                scored = entity_score_dataframe(frame)
            else:
                raise ValueError(stage)
            target = _score_table_path(stage, split, beam)
            target.parent.mkdir(parents=True, exist_ok=True)
            scored.to_parquet(target, index=False)
            scored.to_csv(target.with_suffix(".csv"), index=False)


def run_score_candidates_summac() -> None:
    _run_score_stage("summac")


def run_score_candidates_factcc() -> None:
    _run_score_stage("factcc")


def run_score_candidates_entity_support() -> None:
    _run_score_stage("entity_support")


def run_optional_minicheck_placeholder() -> None:
    write_text(
        artifact_path("scores", "minicheck", "NOT_RUN.md"),
        "# MiniCheck optional stage not executed\n\nThe executed run stayed on the required path.\n",
    )


def run_merge_candidate_scores() -> None:
    for split in ["dev_smoke", "dev_small", "val_tune", "val_full", "test_final"]:
        for beam in [4, 8, 16]:
            base = pd.read_parquet(_candidate_table_path(split, beam))
            summac = pd.read_parquet(_score_table_path("summac", split, beam))
            factcc = pd.read_parquet(_score_table_path("factcc", split, beam))
            entity = pd.read_parquet(_score_table_path("entity_support", split, beam))
            merged = (
                base.merge(summac, on=["id", "candidate_hash"])
                .merge(factcc, on=["id", "candidate_hash"])
                .merge(entity, on=["id", "candidate_hash"])
            )
            target = _merged_table_path(split, beam)
            target.parent.mkdir(parents=True, exist_ok=True)
            merged.to_parquet(target, index=False)
            merged.to_csv(target.with_suffix(".csv"), index=False)


def run_search_weights() -> pd.DataFrame:
    results: list[dict[str, Any]] = []
    normalization = "zscore"
    named = named_weight_configs()
    for beam in [4, 8, 16]:
        frame = pd.read_parquet(_merged_table_path("val_tune", beam))
        configs = list(named.items()) + [
            (f"custom_{index:04d}", weights)
            for index, weights in enumerate(weight_grid(step=0.25), start=1)
        ]
        for system_name, weights in configs:
            fused = fuse_scores(frame, weights, normalization)
            selected = select_top_candidate(fused)
            selected = enrich_with_rouge(selected)
            metrics = metrics_for_selection(selected)
            results.append(
                {
                    "system": system_name,
                    "split": "val_tune",
                    "beam_size": beam,
                    "normalization": normalization,
                    **{f"weight_{key}": value for key, value in weights.items()},
                    **metrics,
                }
            )
    result_frame = pd.DataFrame(results).sort_values(
        ["factuality_composite", "rougeLsum"], ascending=[False, False]
    )
    target = artifact_path("search", "grid_results.csv")
    target.parent.mkdir(parents=True, exist_ok=True)
    result_frame.to_csv(target, index=False)
    baseline_row = (
        result_frame.query("system == 'logprob_only' and beam_size == 8")
        .sort_values("factuality_composite", ascending=False)
        .iloc[0]
    )
    rouge_tolerance = float(
        read_yaml(config_path("rerank", "weight_grid.yaml"))["rouge_lsum_tolerance"]
    )
    balanced_candidates = result_frame[
        result_frame["rougeLsum"] >= float(baseline_row["rougeLsum"]) - rouge_tolerance
    ]
    best_balanced = balanced_candidates.sort_values(
        ["factuality_composite", "rougeLsum"], ascending=[False, False]
    ).iloc[0]
    best_factuality = result_frame.iloc[0]
    simple_candidates = result_frame[
        result_frame["system"].isin(
            ["logprob_plus_summac", "logprob_plus_factcc", "summac_only", "factcc_only"]
        )
    ]
    best_simple = simple_candidates.sort_values(
        ["factuality_composite", "rougeLsum"], ascending=[False, False]
    ).iloc[0]
    for name, row in [
        (BEST_BALANCED, best_balanced),
        (BEST_FACTUALITY, best_factuality),
        (BEST_SIMPLE, best_simple),
    ]:
        payload = {
            "system": str(row["system"]),
            "beam_size": int(row["beam_size"]),
            "normalization": str(row["normalization"]),
            "weights": {
                "token_logprob_avg": float(row["weight_token_logprob_avg"]),
                "summac_style_score": float(row["weight_summac_style_score"]),
                "factcc_style_score": float(row["weight_factcc_style_score"]),
                "entity_support_score": float(row["weight_entity_support_score"]),
            },
            "metrics": {
                "rougeLsum": float(row["rougeLsum"]),
                "factuality_composite": float(row["factuality_composite"]),
            },
        }
        write_yaml(artifact_path("search", f"{name}.yaml"), payload)
    pareto = pareto_frontier(
        result_frame[["system", "beam_size", "rougeLsum", "factuality_composite"]],
        "rougeLsum",
        "factuality_composite",
    )
    pareto.to_csv(artifact_path("search", "pareto_points.csv"), index=False)
    write_yaml(
        config_path("rerank", "final_selection.yaml"),
        read_yaml(artifact_path("search", f"{BEST_BALANCED}.yaml")),
    )
    return result_frame


def run_rerank_and_eval() -> pd.DataFrame:
    systems: list[tuple[str, dict[str, Any]]] = [
        (
            BASELINE_SYSTEM,
            {
                "beam_size": 8,
                "normalization": "zscore",
                "weights": named_weight_configs()["logprob_only"],
            },
        ),
        (BEST_BALANCED, _load_selection_config(BEST_BALANCED)),
        (BEST_FACTUALITY, _load_selection_config(BEST_FACTUALITY)),
        (BEST_SIMPLE, _load_selection_config(BEST_SIMPLE)),
    ]
    for beam in [4, 8, 16]:
        systems.append(
            (
                f"logprob_only_beam_{beam}",
                {
                    "beam_size": beam,
                    "normalization": "zscore",
                    "weights": named_weight_configs()["logprob_only"],
                },
            )
        )
    for name in [
        "summac_only",
        "factcc_only",
        "logprob_plus_summac",
        "logprob_plus_factcc",
        "summac_plus_factcc",
        "logprob_plus_summac_plus_factcc",
        "logprob_plus_summac_plus_factcc_plus_entity_support",
    ]:
        systems.append(
            (
                name,
                {
                    "beam_size": 8,
                    "normalization": "zscore",
                    "weights": named_weight_configs()[name],
                },
            )
        )
    metrics_rows: list[dict[str, Any]] = []
    for split in ["val_full", "test_final"]:
        for system_name, config in systems:
            selected = _apply_system(
                split,
                system_name=system_name,
                beam_size=int(config["beam_size"]),
                weights=dict(config["weights"]),
                normalization=str(config["normalization"]),
            )
            row = {
                "split": split,
                "system": system_name,
                "beam_size": int(config["beam_size"]),
                "normalization": str(config["normalization"]),
                **metrics_for_selection(selected),
            }
            metrics_rows.append(row)
    metrics_frame = pd.DataFrame(metrics_rows)
    metrics_frame.to_csv(artifact_path("eval", "system_metrics.csv"), index=False)
    for split in ["val_full", "test_final"]:
        baseline = pd.read_parquet(_selected_table_path(split, BASELINE_SYSTEM))
        reranked = pd.read_parquet(_selected_table_path(split, BEST_BALANCED))
        comparison = baseline.merge(
            reranked,
            on="id",
            suffixes=("_baseline", "_reranked"),
        )
        comparison = comparison.rename(
            columns={
                "split_baseline": "split",
                "document_baseline": "document",
                "reference_baseline": "reference",
                "summary_baseline": "baseline_summary",
                "summary_reranked": "reranked_summary",
                "rouge1_baseline": "baseline_rouge1",
                "rouge1_reranked": "reranked_rouge1",
                "rouge2_baseline": "baseline_rouge2",
                "rouge2_reranked": "reranked_rouge2",
                "rougeL_baseline": "baseline_rougeL",
                "rougeL_reranked": "reranked_rougeL",
                "rougeLsum_baseline": "baseline_rougeLsum",
                "rougeLsum_reranked": "reranked_rougeLsum",
                "factcc_style_score_baseline": "baseline_factcc_style_score",
                "factcc_style_score_reranked": "reranked_factcc_style_score",
                "summac_style_score_baseline": "baseline_summac_style_score",
                "summac_style_score_reranked": "reranked_summac_style_score",
                "entity_support_score_baseline": "baseline_entity_support_score",
                "entity_support_score_reranked": "reranked_entity_support_score",
                "factuality_composite_baseline": "baseline_factuality_composite",
                "factuality_composite_reranked": "reranked_factuality_composite",
            }
        )
        keep_columns = [
            "id",
            "split",
            "document",
            "reference",
            "baseline_summary",
            "reranked_summary",
            "baseline_rouge1",
            "reranked_rouge1",
            "baseline_rouge2",
            "reranked_rouge2",
            "baseline_rougeL",
            "reranked_rougeL",
            "baseline_rougeLsum",
            "reranked_rougeLsum",
            "baseline_factcc_style_score",
            "reranked_factcc_style_score",
            "baseline_summac_style_score",
            "reranked_summac_style_score",
            "baseline_entity_support_score",
            "reranked_entity_support_score",
            "baseline_factuality_composite",
            "reranked_factuality_composite",
            "candidate_strategy_baseline",
            "candidate_strategy_reranked",
        ]
        comparison[keep_columns].to_csv(_comparison_table_path(split), index=False)
    return metrics_frame


def run_bootstrap_metrics() -> dict[str, Any]:
    baseline = pd.read_parquet(_selected_table_path("test_final", BASELINE_SYSTEM))
    contender = pd.read_parquet(_selected_table_path("test_final", BEST_BALANCED))
    payload = {
        "rougeLsum": bootstrap_difference(baseline, contender, metric_col="rougeLsum"),
        "factcc_style_score": bootstrap_difference(
            baseline, contender, metric_col="factcc_style_score"
        ),
        "factuality_composite": bootstrap_difference(
            baseline, contender, metric_col="factuality_composite"
        ),
    }
    write_json(artifact_path("eval", "bootstrap_cis.json"), payload)
    return payload


def run_sample_manual_audit() -> pd.DataFrame:
    comparison = pd.read_csv(_comparison_table_path("test_final"))
    template_columns = [
        "id",
        "split",
        "document",
        "reference",
        "baseline_summary",
        "reranked_summary",
        "selected_system",
        "baseline_consistent",
        "reranked_consistent",
        "primary_error_type",
        "secondary_error_type",
        "world_knowledge_addition",
        "notes",
    ]
    comparison[
        ["id", "split", "document", "reference", "baseline_summary", "reranked_summary"]
    ].assign(
        selected_system="",
        baseline_consistent="",
        reranked_consistent="",
        primary_error_type="",
        secondary_error_type="",
        world_knowledge_addition="",
        notes="",
    )[template_columns].to_csv(data_path("audit", "manual_audit_template.csv"), index=False)
    audit = build_audit_rows(comparison)
    audit.to_csv(artifact_path("audit", "manual_audit_completed.csv"), index=False)
    audit.to_csv(artifact_path("audit", "audit_examples_for_paper.csv"), index=False)
    return audit


def run_summarize_manual_audit() -> dict[str, Any]:
    audit = pd.read_csv(artifact_path("audit", "manual_audit_completed.csv"))
    summary_frame = (
        audit.groupby("primary_error_type", as_index=False)
        .size()
        .rename(columns={"size": "count"})
        .sort_values("count", ascending=False)
        .rename(columns={"primary_error_type": "primary_error_type"})
    )
    summary_frame.to_csv(artifact_path("audit", "audit_taxonomy_table.csv"), index=False)
    payload = {
        "rows": int(len(audit)),
        "baseline_consistent_rate": round(
            float(audit["baseline_consistent"].astype(bool).mean()), 6
        ),
        "reranked_consistent_rate": round(
            float(audit["reranked_consistent"].astype(bool).mean()), 6
        ),
        "selected_system_counts": audit["selected_system"].value_counts().to_dict(),
        "error_counts": dict(
            zip(summary_frame["primary_error_type"], summary_frame["count"], strict=True)
        ),
    }
    write_json(artifact_path("audit", "manual_audit_summary.json"), payload)
    return payload


def run_make_tables_and_figures() -> None:
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
        artifact_path("eval", "bootstrap_cis.json"), output_path("final", "bootstrap_cis.json")
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
    beam_tradeoff["beam_size"] = beam_tradeoff["system"].str.extract(r"(\d+)").astype(int)
    plot_beam_tradeoff(
        beam_tradeoff[["beam_size", "rougeLsum", "factuality_composite"]],
        output_path("final", "figures", "beam_tradeoff.png"),
    )
    plot_component_ablation(ablation, output_path("final", "figures", "component_ablation.png"))
    plot_error_taxonomy(audit_summary, output_path("final", "figures", "error_taxonomy.png"))
    comparison = pd.read_csv(_comparison_table_path("test_final"))
    scatter_frame = audit.merge(
        comparison[["id", "reranked_factcc_style_score"]],
        on="id",
        how="left",
    )
    plot_metric_vs_human_scatter(
        scatter_frame, output_path("final", "figures", "metric_vs_human_scatter.png")
    )
    report_tables = [
        "# Report-ready tables",
        "",
        "## Main metrics",
        "",
        _markdown_table(main_metrics.round(4)),
        "",
        "## Ablation metrics",
        "",
        _markdown_table(ablation.round(4)),
        "",
        "## Audit taxonomy",
        "",
        _markdown_table(audit_summary),
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
    success = qualitative.head(3)
    failure = qualitative.tail(3)
    success_lines = ["# Success cases", ""]
    for _, row in success.iterrows():
        success_lines.extend(
            [
                f"## {row['id']}",
                f"- Reference: {row['reference']}",
                f"- Baseline: {row['baseline_summary']}",
                f"- Reranked: {row['reranked_summary']}",
                f"- Factuality delta: {row['factuality_delta']:.4f}",
                "",
            ]
        )
    failure_lines = ["# Failure cases", ""]
    for _, row in failure.iterrows():
        failure_lines.extend(
            [
                f"## {row['id']}",
                f"- Reference: {row['reference']}",
                f"- Baseline: {row['baseline_summary']}",
                f"- Reranked: {row['reranked_summary']}",
                f"- Factuality delta: {row['factuality_delta']:.4f}",
                "",
            ]
        )
    write_text(output_path("final", "examples_success.md"), "\n".join(success_lines))
    write_text(output_path("final", "examples_failures.md"), "\n".join(failure_lines))
    system_card = [
        "# System card",
        "",
        "- Requested study: XSum factuality-aware reranking with BART, SummaC, and FactCC-style scoring.",
        "- Executed run: offline fixture fallback with deterministic surrogate generator and heuristic factuality scorers.",
        "- Intended use: repository scaffolding, analysis pipeline demonstration, and handoff artifact generation.",
        "- Not suitable for claiming benchmark-level XSum improvements from the executed run.",
    ]
    write_text(output_path("final", "system_card.md"), "\n".join(system_card))


def run_build_results_summary() -> None:
    dataset_manifest = read_json(artifact_path("data", "dataset_manifest.json"))
    metrics = pd.read_csv(output_path("final", "main_metrics.csv"))
    bootstrap = read_json(artifact_path("eval", "bootstrap_cis.json"))
    audit_summary = read_json(artifact_path("audit", "manual_audit_summary.json"))
    best_config = _load_selection_config(BEST_BALANCED)
    selected = metrics[
        (metrics["split"] == "test_final") & (metrics["system"] == BEST_BALANCED)
    ].iloc[0]
    baseline = metrics[
        (metrics["split"] == "test_final") & (metrics["system"] == BASELINE_SYSTEM)
    ].iloc[0]
    results_summary = [
        "# RESULTS_SUMMARY",
        "",
        "## What actually ran",
        "",
        "- Implemented the full repository and stage-by-stage script surface from the handoff plan.",
        "- Executed the offline fixture fallback because the runtime could not resolve Hugging Face hosts.",
        f"- Fixture rows available: {dataset_manifest['rows_available']}.",
        "",
        "## Requested online path vs executed path",
        "",
        "- Requested dataset: `EdinburghNLP/xsum`.",
        "- Requested generator: `facebook/bart-large-xsum`.",
        "- Requested factuality models: `SummaCConv` and `manueldeprada/FactCC`.",
        "- Executed generator: deterministic headline-style offline surrogate.",
        (
            "- Executed factuality metrics: heuristic SummaC-style score, heuristic "
            "FactCC-style score, and entity/date/number support."
        ),
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
        "```bash",
        "uv sync --dev",
        "uv run python scripts/00_env_check.py",
        "uv run python scripts/01_prepare_xsum.py",
        "uv run python scripts/02_train_or_load_bart.py",
        "uv run python scripts/03_generate_candidates.py",
        "uv run python scripts/04_score_candidates_summac.py",
        "uv run python scripts/05_score_candidates_factcc.py",
        "uv run python scripts/06_score_candidates_entity_support.py",
        "uv run python scripts/08_merge_candidate_scores.py",
        "uv run python scripts/09_search_weights.py",
        "uv run python scripts/10_rerank_and_eval.py",
        "uv run python scripts/11_bootstrap_metrics.py",
        "uv run python scripts/12_sample_manual_audit.py",
        "uv run python scripts/13_summarize_manual_audit.py",
        "uv run python scripts/14_make_tables_and_figures.py",
        "uv run python scripts/15_build_results_summary.py",
        "uv run python scripts/16_package_repo.py",
        "```",
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
        f"- Baseline consistent rate: {audit_summary['baseline_consistent_rate']:.4f}",
        f"- Reranked consistent rate: {audit_summary['reranked_consistent_rate']:.4f}",
        "- Dominant remaining failure buckets are listed in `outputs/final/manual_audit_summary.json`.",
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
        "- Packaged repo: `../factuality-rerank-xsum.zip`",
        "",
        "## Limits on claims",
        "",
        "- The executed numbers describe the offline fixture fallback only.",
        "- The repo preserves the online public-data path, but those runs were not executed in this environment.",
        "- The assistant-generated manual audit is useful for error slicing, not for strong human-annotation claims.",
    ]
    write_text(docs_path("RESULTS_SUMMARY.md"), "\n".join(results_summary))
    runbook = [
        "# RUNBOOK",
        "",
        "## Fast path used in this session",
        "",
        "1. `uv sync`",
        "2. `uv run python scripts/00_env_check.py`",
        "3. `uv run python scripts/01_prepare_xsum.py`",
        "4. `uv run python scripts/02_train_or_load_bart.py`",
        "5. `uv run python scripts/03_generate_candidates.py`",
        "6. `uv run python scripts/04_score_candidates_summac.py`",
        "7. `uv run python scripts/05_score_candidates_factcc.py`",
        "8. `uv run python scripts/06_score_candidates_entity_support.py`",
        "9. `uv run python scripts/08_merge_candidate_scores.py`",
        "10. `uv run python scripts/09_search_weights.py`",
        "11. `uv run python scripts/10_rerank_and_eval.py`",
        "12. `uv run python scripts/11_bootstrap_metrics.py`",
        "13. `uv run python scripts/12_sample_manual_audit.py`",
        "14. `uv run python scripts/13_summarize_manual_audit.py`",
        "15. `uv run python scripts/14_make_tables_and_figures.py`",
        "16. `uv run python scripts/15_build_results_summary.py`",
        "17. `uv run python scripts/16_package_repo.py`",
        "",
        "## Online public-data path",
        "",
        "- Install PyTorch with the official selector before attempting a full public-data rerun.",
        "- Because `summac==0.0.4` conflicts with the modern Hugging Face stack used by the requested online path, use separate `online` and `metrics` environments for a full rerun.",
        "",
        "## Artifacts",
        "",
        "- Candidate tables: `artifacts/generations/<split>/beam_<n>/candidates.parquet`",
        "- Merged score tables: `artifacts/scores/merged/<split>/beam_<n>.parquet`",
        "- Final outputs: `outputs/final/`",
    ]
    write_text(docs_path("RUNBOOK.md"), "\n".join(runbook))
    checklist = [
        "# SUBMISSION_CHECKLIST",
        "",
        "- [x] Repo includes code, configs, docs, and prompts.",
        "- [x] Final outputs include metrics CSVs, figures, and manual audit files.",
        "- [x] README and RESULTS_SUMMARY reflect the executed run truthfully.",
        "- [ ] Full online XSum/BART/SummaC/FactCC run remains to be executed in a network-enabled environment.",
    ]
    write_text(docs_path("SUBMISSION_CHECKLIST.md"), "\n".join(checklist))
    claims = [
        "# CLAIMS_SAFE_TO_WRITE",
        "",
        "## Supported by executed artifacts",
        "",
        "- The repo implements the requested reranking study structure and artifact contract.",
        "- The executed offline fixture run shows that factuality-aware reranking can improve a surrogate factuality composite on the local fixture.",
        "- Entity/date/number support is useful as a targeted refinement in the executed fallback setting.",
        "",
        "## Too strong for the executed run",
        "",
        "- Do not claim benchmark-level XSum gains.",
        "- Do not claim that BART or real SummaC / FactCC checkpoints were executed in this environment.",
        "- Do not claim human-annotator reliability beyond a single-pass assistant audit.",
    ]
    write_text(docs_path("CLAIMS_SAFE_TO_WRITE.md"), "\n".join(claims))
    slides = [
        "# SLIDES_OUTLINE",
        "",
        "1. Motivation: factual hallucinations in extreme summarization.",
        "2. Method: beam candidates plus factuality-aware reranking.",
        "3. Signals: generator prior, SummaC-style support, FactCC-style consistency, entity support.",
        "4. Main result: offline fixture best-balanced reranker versus baseline.",
        "5. Audit and refinement: entity / number / relation failure buckets.",
        "6. Conclusion: repo complete; online public-data rerun is the next step.",
    ]
    write_text(docs_path("SLIDES_OUTLINE.md"), "\n".join(slides))
    readme = [
        "# factuality-rerank-xsum",
        "",
        "A reproducible summarization-analysis repository for factuality-aware reranking on XSum.",
        "",
        "## What this repo contains",
        "",
        "- A full stage-by-stage pipeline from environment check through packaging.",
        "- An executed offline fallback run that generated the report-ready artifacts in `outputs/final/`.",
        "- Preserved prompts, plans, and references from the handoff bundle.",
        "",
        "## Quick start",
        "",
        "```bash",
        "uv sync",
        "uv run python scripts/00_env_check.py",
        "uv run python scripts/01_prepare_xsum.py",
        "uv run python scripts/03_generate_candidates.py",
        "uv run python scripts/04_score_candidates_summac.py",
        "uv run python scripts/05_score_candidates_factcc.py",
        "uv run python scripts/06_score_candidates_entity_support.py",
        "uv run python scripts/08_merge_candidate_scores.py",
        "uv run python scripts/09_search_weights.py",
        "uv run python scripts/10_rerank_and_eval.py",
        "uv run python scripts/11_bootstrap_metrics.py",
        "uv run python scripts/12_sample_manual_audit.py",
        "uv run python scripts/13_summarize_manual_audit.py",
        "uv run python scripts/14_make_tables_and_figures.py",
        "uv run python scripts/15_build_results_summary.py",
        "uv run python scripts/16_package_repo.py",
        "```",
        "",
        "## Online public-data path",
        "",
        "Install PyTorch with the official selector first. For a real public-data rerun, use separate online and metrics environments because the legacy SummaC dependency conflicts with the modern Hugging Face stack.",
        "",
        "```bash",
        "uv sync --dev",
        "```",
        "",
        "The executed session could not reach Hugging Face, so the generated outputs document the offline fixture fallback rather than a full benchmark run.",
        "",
        "## Key artifacts",
        "",
        "- `docs/RESULTS_SUMMARY.md`",
        "- `outputs/final/main_metrics.csv`",
        "- `outputs/final/ablation_metrics.csv`",
        "- `outputs/final/pareto_points.csv`",
        "- `outputs/final/manual_audit.csv`",
        "- `outputs/final/figures/`",
    ]
    write_text(project_root() / "README.md", "\n".join(readme))
    original_plan = (project_root() / "PLAN.original.md").read_text(encoding="utf-8")
    refreshed_plan = "\n".join(
        [
            "# PLAN.md",
            "",
            "## Execution refresh",
            "",
            "- The repository was implemented to match the merged handoff structure.",
            "- The executed run used the offline preview-fixture fallback because model and dataset downloads were not reachable from the runtime.",
            "- Final artifacts were written to `outputs/final/` and packaged.",
            "",
            "## Original implementation handoff",
            "",
            original_plan,
        ]
    )
    write_text(project_root() / "PLAN.md", refreshed_plan)


def run_package_repo() -> Path:
    final_path = project_root().parent / "factuality-rerank-xsum.zip"
    if final_path.exists():
        final_path.unlink()
    excluded_parts = {
        ".git",
        ".venv",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
    }
    with zipfile.ZipFile(final_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in project_root().rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(project_root())
            if any(part in excluded_parts for part in relative.parts):
                continue
            if relative.parts[:2] == ("artifacts", "package") and path.suffix == ".zip":
                continue
            archive.write(path, arcname=str(Path(project_root().name) / relative))
    artifact_copy = artifact_path("package", final_path.name)
    shutil.copy2(final_path, artifact_copy)
    write_json(
        artifact_path("package", "artifact_manifest.json"),
        {
            "repo_zip": str(final_path),
            "artifact_copy": str(artifact_copy),
            "final_outputs": sorted(
                str(path.relative_to(project_root()))
                for path in output_path("final").rglob("*")
                if path.is_file()
            ),
        },
    )
    return final_path
