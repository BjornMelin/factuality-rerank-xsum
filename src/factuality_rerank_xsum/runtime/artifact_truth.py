"""Artifact-truth and provenance validation for report-facing surfaces."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import pandas as pd

from factuality_rerank_xsum.artifacts.layout import (
    candidate_table_path,
    comparison_table_path,
    selected_table_path,
)
from factuality_rerank_xsum.constants import (
    BASELINE_SYSTEM,
    BEAM_SIZES,
    BEST_BALANCED,
    BEST_FACTUALITY,
    BEST_SIMPLE,
    PIPELINE_SPLITS,
)
from factuality_rerank_xsum.utils.io import read_json, write_json
from factuality_rerank_xsum.utils.paths import (
    artifact_path,
    data_path,
    output_path,
)

if TYPE_CHECKING:
    from pathlib import Path

AUDIT_PROVENANCE_COLUMNS = ["annotator_id", "annotation_method"]
FINAL_REPORT_SPLITS = ["val_full", "test_final"]
MAIN_OUTPUT_SYSTEMS = {
    BASELINE_SYSTEM,
    BEST_BALANCED,
    BEST_FACTUALITY,
    BEST_SIMPLE,
}
REQUIRED_GENERATION_COLUMNS = {
    "id",
    "split",
    "summary",
    "candidate_strategy",
    "generator_mode",
    "requested_model",
    "requested_revision",
}


def _required_json(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    if not isinstance(payload, dict):
        msg = f"Expected JSON object at {path}"
        raise ValueError(msg)
    return payload


def _read_table(parquet_path: Path) -> pd.DataFrame:
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    csv_path = parquet_path.with_suffix(".csv")
    if csv_path.exists():
        return pd.read_csv(csv_path)
    msg = f"Missing required artifact table: {parquet_path}"
    raise FileNotFoundError(msg)


def _split_ids(split: str) -> list[str]:
    split_path = data_path("processed", "splits", f"{split}_ids.txt")
    if not split_path.exists():
        msg = f"Missing split-id file for {split}: {split_path}"
        raise FileNotFoundError(msg)
    return [line.strip() for line in split_path.read_text(encoding="utf-8").splitlines() if line]


def _record_error(errors: list[str], message: str) -> None:
    errors.append(message)


def _sorted_ids(frame: pd.DataFrame) -> list[str]:
    if "id" not in frame.columns:
        return []
    return sorted(frame["id"].astype(str).tolist())


def _validate_candidate_frame(
    frame: pd.DataFrame,
    *,
    split: str,
    beam_size: int,
    expected_ids: list[str],
    generator_mode: str,
    errors: list[str],
) -> dict[str, Any]:
    missing_columns = sorted(REQUIRED_GENERATION_COLUMNS - set(frame.columns))
    if missing_columns:
        _record_error(
            errors,
            (
                f"Generation artifact {split}/beam_{beam_size} is missing required columns: "
                f"{missing_columns}"
            ),
        )
    observed_ids = _sorted_ids(frame)
    expected_sorted = sorted(expected_ids)
    if observed_ids and observed_ids != sorted(expected_sorted * beam_size):
        grouped = frame["id"].astype(str).value_counts().to_dict()
        _record_error(
            errors,
            (
                f"Generation artifact {split}/beam_{beam_size} does not match requested split IDs. "
                f"Observed unique IDs={len(set(observed_ids))}, expected unique IDs={len(expected_ids)}, "
                f"per-id counts sample={dict(list(grouped.items())[:3])}"
            ),
        )
    expected_rows = len(expected_ids) * beam_size
    if len(frame) != expected_rows:
        _record_error(
            errors,
            (
                f"Generation artifact {split}/beam_{beam_size} has {len(frame)} rows; "
                f"expected {expected_rows}."
            ),
        )
    if generator_mode == "huggingface_generation":
        if "offline_generator_noise" in frame.columns:
            _record_error(
                errors,
                (
                    f"Generation artifact {split}/beam_{beam_size} still exposes "
                    "`offline_generator_noise` under huggingface_generation mode."
                ),
            )
        if (
            "generator_mode" in frame.columns
            and not frame["generator_mode"].astype(str).eq("huggingface_generation").all()
        ):
            _record_error(
                errors,
                (
                    f"Generation artifact {split}/beam_{beam_size} has non-HF generator_mode values "
                    "inside a huggingface_generation run."
                ),
            )
        if (
            "requested_model" in frame.columns
            and frame["requested_model"].astype(str).str.strip().eq("").any()
        ):
            _record_error(
                errors,
                f"Generation artifact {split}/beam_{beam_size} has blank requested_model values.",
            )
        if (
            "candidate_strategy" in frame.columns
            and not frame["candidate_strategy"].astype(str).str.fullmatch(r"hf_beam_\d+").all()
        ):
            _record_error(
                errors,
                (
                    f"Generation artifact {split}/beam_{beam_size} has non-HF candidate_strategy "
                    "values in a huggingface_generation run."
                ),
            )
    return {
        "rows": len(frame),
        "expected_rows": expected_rows,
        "unique_ids": int(frame["id"].astype(str).nunique()) if "id" in frame.columns else 0,
    }


def _validate_selected_or_comparison(
    frame: pd.DataFrame,
    *,
    label: str,
    expected_ids: list[str],
    errors: list[str],
) -> dict[str, Any]:
    observed_ids = sorted(frame["id"].astype(str).tolist()) if "id" in frame.columns else []
    if observed_ids != sorted(expected_ids):
        _record_error(
            errors,
            (
                f"{label} does not match the configured split IDs. "
                f"Observed rows={len(frame)}, expected rows={len(expected_ids)}."
            ),
        )
    return {"rows": len(frame), "expected_rows": len(expected_ids)}


def build_artifact_truth_report(*, stage_name: str, require_final_outputs: bool) -> dict[str, Any]:
    """Build and persist the current artifact-truth report."""

    errors: list[str] = []
    dataset_manifest = _required_json(artifact_path("data", "dataset_manifest.json"))
    generation_summary = _required_json(artifact_path("generations", "generation_summary.json"))
    split_sampling = dataset_manifest.get("split_sampling", {})
    if not isinstance(split_sampling, dict):
        msg = "dataset_manifest split_sampling must be a JSON object."
        raise ValueError(msg)

    split_checks: dict[str, Any] = {}
    expected_ids_by_split: dict[str, list[str]] = {}
    for split, details in split_sampling.items():
        if not isinstance(details, dict):
            _record_error(
                errors,
                f"dataset_manifest split_sampling entry for {split} is not an object.",
            )
            continue
        expected_ids = _split_ids(split)
        expected_ids_by_split[split] = expected_ids
        manifest_rows = int(details.get("rows_selected", -1))
        if manifest_rows != len(expected_ids):
            _record_error(
                errors,
                (
                    f"dataset_manifest split {split} reports rows_selected={manifest_rows}, "
                    f"but split-id file has {len(expected_ids)} IDs."
                ),
            )
        split_checks[split] = {
            "requested_rows": manifest_rows,
            "split_id_rows": len(expected_ids),
        }

    generation_beams = generation_summary.get("beam_sizes")
    if generation_beams != BEAM_SIZES:
        _record_error(
            errors,
            f"generation_summary beam_sizes={generation_beams} does not match expected {BEAM_SIZES}.",
        )
    generator_mode = str(generation_summary.get("generator_mode") or "")
    if not generator_mode:
        _record_error(errors, "generation_summary is missing generator_mode.")
    if not generation_summary.get("generator_model"):
        _record_error(errors, "generation_summary is missing generator_model.")
    generation_checks: dict[str, Any] = {}
    split_summaries = generation_summary.get("splits", {})
    if not isinstance(split_summaries, dict):
        _record_error(errors, "generation_summary splits must be a JSON object.")
        split_summaries = {}
    for split in PIPELINE_SPLITS:
        split_expected_ids = expected_ids_by_split.get(split)
        if split_expected_ids is None:
            _record_error(
                errors,
                f"Missing expected split IDs for generation split {split}.",
            )
            continue
        expected_ids = split_expected_ids
        split_summary = split_summaries.get(split)
        if not isinstance(split_summary, dict):
            _record_error(
                errors,
                f"generation_summary is missing a split entry for {split}.",
            )
            split_summary = {}
        observed_examples = int(split_summary.get("examples", -1))
        if observed_examples != len(expected_ids):
            _record_error(
                errors,
                (
                    f"generation_summary split {split} reports examples={observed_examples}, "
                    f"expected {len(expected_ids)}."
                ),
            )
        generation_checks[split] = {"examples": observed_examples, "beams": {}}
        for beam_size in BEAM_SIZES:
            frame = _read_table(candidate_table_path(split, beam_size))
            generation_checks[split]["beams"][str(beam_size)] = _validate_candidate_frame(
                frame,
                split=split,
                beam_size=beam_size,
                expected_ids=expected_ids,
                generator_mode=generator_mode,
                errors=errors,
            )

    eval_checks: dict[str, Any] = {}
    for split in FINAL_REPORT_SPLITS:
        expected_ids_for_split = expected_ids_by_split.get(split)
        if expected_ids_for_split is None:
            _record_error(errors, f"Missing expected split IDs for report split {split}.")
            continue
        baseline = pd.read_parquet(selected_table_path(split, BASELINE_SYSTEM))
        reranked = pd.read_parquet(selected_table_path(split, BEST_BALANCED))
        comparison = pd.read_csv(comparison_table_path(split))
        eval_checks[split] = {
            BASELINE_SYSTEM: _validate_selected_or_comparison(
                baseline,
                label=f"{split} {BASELINE_SYSTEM}",
                expected_ids=expected_ids_for_split,
                errors=errors,
            ),
            BEST_BALANCED: _validate_selected_or_comparison(
                reranked,
                label=f"{split} {BEST_BALANCED}",
                expected_ids=expected_ids_for_split,
                errors=errors,
            ),
            "comparison": _validate_selected_or_comparison(
                comparison,
                label=f"{split} comparison table",
                expected_ids=expected_ids_for_split,
                errors=errors,
            ),
        }

    audit_frame = pd.read_csv(artifact_path("audit", "manual_audit_completed.csv"))
    audit_summary = _required_json(artifact_path("audit", "manual_audit_summary.json"))
    missing_audit_columns = sorted(set(AUDIT_PROVENANCE_COLUMNS) - set(audit_frame.columns))
    if missing_audit_columns:
        _record_error(
            errors,
            f"manual_audit_completed.csv is missing provenance columns: {missing_audit_columns}.",
        )
    if len(audit_frame) < 24:
        _record_error(
            errors,
            f"manual_audit_completed.csv has {len(audit_frame)} rows; at least 24 are required.",
        )
    if int(audit_summary.get("rows", -1)) != len(audit_frame):
        _record_error(
            errors,
            (
                f"manual_audit_summary.json reports rows={audit_summary.get('rows')}; "
                f"manual_audit_completed.csv has {len(audit_frame)}."
            ),
        )

    final_output_checks: dict[str, Any] = {}
    if require_final_outputs:
        final_audit = pd.read_csv(output_path("final", "manual_audit.csv"))
        final_summary = _required_json(output_path("final", "manual_audit_summary.json"))
        main_metrics = pd.read_csv(output_path("final", "main_metrics.csv"))
        if len(final_audit) != len(audit_frame):
            _record_error(
                errors,
                (
                    f"outputs/final/manual_audit.csv has {len(final_audit)} rows; "
                    f"artifact audit has {len(audit_frame)}."
                ),
            )
        if final_summary != audit_summary:
            _record_error(
                errors,
                "outputs/final/manual_audit_summary.json does not match artifacts/audit/manual_audit_summary.json.",
            )
        observed_systems = set(main_metrics["system"].astype(str).tolist())
        if observed_systems != MAIN_OUTPUT_SYSTEMS:
            _record_error(
                errors,
                (
                    f"outputs/final/main_metrics.csv systems={sorted(observed_systems)} do not match "
                    f"expected {sorted(MAIN_OUTPUT_SYSTEMS)}."
                ),
            )
        observed_splits = set(main_metrics["split"].astype(str).tolist())
        if observed_splits != set(FINAL_REPORT_SPLITS):
            _record_error(
                errors,
                (
                    f"outputs/final/main_metrics.csv splits={sorted(observed_splits)} do not match "
                    f"expected {sorted(FINAL_REPORT_SPLITS)}."
                ),
            )
        final_output_checks = {
            "final_audit_rows": len(final_audit),
            "final_main_metrics_rows": len(main_metrics),
        }

    report = {
        "ok": not errors,
        "stage": stage_name,
        "checked_at_utc": datetime.now(UTC).isoformat(),
        "require_final_outputs": require_final_outputs,
        "dataset_splits": split_checks,
        "generation": {
            "generator_mode": generator_mode or None,
            "beam_sizes": generation_beams,
            "splits": generation_checks,
        },
        "evaluation": eval_checks,
        "audit": {
            "rows": len(audit_frame),
            "summary_rows": audit_summary.get("rows"),
            "missing_provenance_columns": missing_audit_columns,
        },
        "final_outputs": final_output_checks,
        "errors": errors,
    }
    write_json(artifact_path("validation", "artifact_truth_report.json"), report)
    return report


def assert_artifact_truth(*, stage_name: str, require_final_outputs: bool) -> dict[str, Any]:
    """Raise when report-facing artifacts are stale, inconsistent, or under-provenanced."""

    report = build_artifact_truth_report(
        stage_name=stage_name,
        require_final_outputs=require_final_outputs,
    )
    if report["ok"]:
        return report
    joined = "\n".join(f"- {message}" for message in report["errors"])
    msg = f"Artifact truth validation failed for {stage_name}:\n{joined}"
    raise ValueError(msg)
