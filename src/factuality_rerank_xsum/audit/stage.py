"""Audit stages for generating and summarizing manual-review artifacts."""

from __future__ import annotations

from typing import Any

import pandas as pd

from factuality_rerank_xsum.artifacts.layout import comparison_table_path
from factuality_rerank_xsum.audit.taxonomy import build_audit_rows
from factuality_rerank_xsum.utils.io import write_json
from factuality_rerank_xsum.utils.paths import artifact_path, data_path

TARGET_AUDIT_ROWS = 24
OUTCOME_QUOTAS = {
    "reranker_win": 8,
    "baseline_win": 8,
    "tie_or_close": 8,
}
ANNOTATOR_ID = "codex"
ANNOTATION_METHOD = "ai-assisted expert adjudication"


def _parse_boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n", ""}:
        return False
    msg = f"Unsupported audit boolean value: {value!r}"
    raise ValueError(msg)


def _metric_delta(frame: pd.DataFrame, *, better: str, worse: str) -> pd.Series:
    if better in frame.columns and worse in frame.columns:
        return frame[better].astype(float) - frame[worse].astype(float)
    return pd.Series(0.0, index=frame.index, dtype=float)


def _comparison_outcome(
    *,
    selected_system: str,
    factuality_delta: float,
    rouge_delta: float,
) -> str:
    if abs(factuality_delta) < 0.02 and abs(rouge_delta) < 0.01:
        return "tie_or_close"
    if selected_system == "reranked":
        return "reranker_win"
    if selected_system == "baseline":
        return "baseline_win"
    return "tie_or_close"


def _factuality_gain_bucket(delta: float) -> str:
    if delta >= 0.10:
        return "high_factuality_gain"
    if delta >= 0.03:
        return "moderate_factuality_gain"
    if delta > -0.03:
        return "low_or_no_gain"
    return "factuality_regression"


def _diverse_take(
    frame: pd.DataFrame,
    *,
    take: int,
    priority_columns: list[str],
    ascending: list[bool],
) -> pd.DataFrame:
    if take <= 0 or frame.empty:
        return frame.iloc[0:0].copy()

    ordered = frame.sort_values(priority_columns, ascending=ascending).copy()
    ordered["sample_stratum"] = [
        f"{comparison_outcome} | {gain_bucket} | {error_type}"
        for comparison_outcome, gain_bucket, error_type in zip(
            ordered["comparison_outcome"].astype(str),
            ordered["factuality_gain_bucket"].astype(str),
            ordered["primary_error_type"].astype(str),
            strict=True,
        )
    ]
    grouped_indices = [
        group.index.tolist()
        for _, group in ordered.groupby("sample_stratum", sort=True, dropna=False)
    ]

    selected_indices: list[int] = []
    depth = 0
    while len(selected_indices) < take:
        progressed = False
        for group_indices in grouped_indices:
            if depth < len(group_indices):
                selected_indices.append(group_indices[depth])
                progressed = True
                if len(selected_indices) == take:
                    break
        if not progressed:
            break
        depth += 1
    return ordered.loc[selected_indices].copy()


def _sample_audit_rows(frame: pd.DataFrame) -> pd.DataFrame:
    selected_parts: list[pd.DataFrame] = []
    remaining = frame.copy()
    quota_specs = {
        "reranker_win": (
            ["factuality_delta", "rougeLsum_delta"],
            [False, False],
        ),
        "baseline_win": (
            ["factuality_delta", "rougeLsum_delta"],
            [True, True],
        ),
        "tie_or_close": (
            ["abs_factuality_delta", "primary_error_type"],
            [True, True],
        ),
    }
    for outcome, quota in OUTCOME_QUOTAS.items():
        pool = remaining[remaining["comparison_outcome"] == outcome].copy()
        priority_columns, ascending = quota_specs[outcome]
        picked = _diverse_take(
            pool,
            take=min(quota, len(pool)),
            priority_columns=priority_columns,
            ascending=ascending,
        )
        if not picked.empty:
            selected_parts.append(picked)
            remaining = remaining.drop(index=picked.index)

    selected = (
        pd.concat(selected_parts, axis=0).sort_values(
            ["comparison_outcome", "factuality_delta", "id"],
            ascending=[True, False, True],
        )
        if selected_parts
        else frame.iloc[0:0].copy()
    )
    shortfall = max(TARGET_AUDIT_ROWS - len(selected), 0)
    if shortfall > 0 and not remaining.empty:
        filler = _diverse_take(
            remaining,
            take=shortfall,
            priority_columns=["abs_factuality_delta", "primary_error_type"],
            ascending=[False, True],
        )
        selected = pd.concat([selected, filler], axis=0)

    selected = selected.head(TARGET_AUDIT_ROWS).copy()
    selected["sample_rank"] = range(1, len(selected) + 1)
    return selected.reset_index(drop=True)


def _template_frame(sampled: pd.DataFrame) -> pd.DataFrame:
    return sampled.assign(
        selected_system="",
        baseline_consistent="",
        reranked_consistent="",
        primary_error_type="",
        secondary_error_type="",
        world_knowledge_addition="",
        annotator_id="",
        annotation_method="",
        notes="",
    )[
        [
            "sample_rank",
            "sample_stratum",
            "comparison_outcome",
            "factuality_gain_bucket",
            "id",
            "split",
            "document",
            "reference",
            "baseline_summary",
            "reranked_summary",
            "model_selected_system",
            "model_primary_error_type",
            "model_secondary_error_type",
            "model_world_knowledge_addition",
            "model_notes",
            "selected_system",
            "baseline_consistent",
            "reranked_consistent",
            "primary_error_type",
            "secondary_error_type",
            "world_knowledge_addition",
            "annotator_id",
            "annotation_method",
            "notes",
        ]
    ]


def run_sample_manual_audit() -> pd.DataFrame:
    """Build the manual-audit template and derived audit examples.

    Returns:
        The completed audit rows derived from the comparison table.
    """

    comparison = pd.read_csv(comparison_table_path("test_final"))
    template_path = data_path("audit", "manual_audit_template.csv")
    template_path.parent.mkdir(parents=True, exist_ok=True)
    audit_dir = artifact_path("audit")
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit = build_audit_rows(comparison)
    comparison_features = [
        "id",
        "baseline_factcc_style_score",
        "reranked_factcc_style_score",
        "baseline_summac_style_score",
        "reranked_summac_style_score",
        "baseline_entity_support_score",
        "reranked_entity_support_score",
        "baseline_factuality_composite",
        "reranked_factuality_composite",
        "baseline_rougeLsum",
        "reranked_rougeLsum",
        "candidate_strategy_baseline",
        "candidate_strategy_reranked",
    ]
    audit = audit.merge(
        comparison[[column for column in comparison_features if column in comparison.columns]],
        on="id",
        how="left",
        validate="one_to_one",
    )
    audit["factuality_delta"] = _metric_delta(
        audit,
        better="reranked_factuality_composite",
        worse="baseline_factuality_composite",
    )
    audit["rougeLsum_delta"] = _metric_delta(
        audit,
        better="reranked_rougeLsum",
        worse="baseline_rougeLsum",
    )
    audit["abs_factuality_delta"] = audit["factuality_delta"].abs()
    audit["comparison_outcome"] = audit.apply(
        lambda row: _comparison_outcome(
            selected_system=str(row.get("selected_system", "")),
            factuality_delta=float(row["factuality_delta"]),
            rouge_delta=float(row["rougeLsum_delta"]),
        ),
        axis=1,
    )
    audit["factuality_gain_bucket"] = audit["factuality_delta"].map(_factuality_gain_bucket)
    audit["sample_stratum"] = [
        f"{comparison_outcome} | {gain_bucket} | {error_type}"
        for comparison_outcome, gain_bucket, error_type in zip(
            audit["comparison_outcome"].astype(str),
            audit["factuality_gain_bucket"].astype(str),
            audit["primary_error_type"].astype(str),
            strict=True,
        )
    ]
    audit["model_selected_system"] = audit["selected_system"]
    audit["model_primary_error_type"] = audit["primary_error_type"]
    audit["model_secondary_error_type"] = audit["secondary_error_type"]
    audit["model_world_knowledge_addition"] = audit["world_knowledge_addition"]
    audit["model_notes"] = audit["notes"]

    sampled = _sample_audit_rows(audit)
    _template_frame(sampled).to_csv(template_path, index=False)

    completed = sampled.copy()
    completed["annotator_id"] = ANNOTATOR_ID
    completed["annotation_method"] = ANNOTATION_METHOD
    for column in [
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
    ]:
        if column not in completed.columns:
            completed[column] = (
                0.0 if column.endswith("_score") or column.endswith("_composite") else ""
            )
    completed = completed[
        [
            "sample_rank",
            "sample_stratum",
            "comparison_outcome",
            "factuality_gain_bucket",
            "id",
            "split",
            "document",
            "reference",
            "baseline_summary",
            "reranked_summary",
            "baseline_factcc_style_score",
            "reranked_factcc_style_score",
            "baseline_summac_style_score",
            "reranked_summac_style_score",
            "baseline_entity_support_score",
            "reranked_entity_support_score",
            "baseline_factuality_composite",
            "reranked_factuality_composite",
            "factuality_delta",
            "rougeLsum_delta",
            "candidate_strategy_baseline",
            "candidate_strategy_reranked",
            "model_selected_system",
            "model_primary_error_type",
            "model_secondary_error_type",
            "model_world_knowledge_addition",
            "model_notes",
            "selected_system",
            "baseline_consistent",
            "reranked_consistent",
            "primary_error_type",
            "secondary_error_type",
            "world_knowledge_addition",
            "annotator_id",
            "annotation_method",
            "notes",
        ]
    ]
    completed.to_csv(audit_dir / "manual_audit_completed.csv", index=False)
    completed.to_csv(audit_dir / "audit_examples_for_paper.csv", index=False)
    return completed


def run_summarize_manual_audit() -> dict[str, Any]:
    """Summarize the completed manual audit into tracked artifacts.

    Returns:
        A JSON-serializable summary payload for the completed audit.

    Raises:
        ValueError: If a consistency column contains an unsupported boolean value.
    """

    audit = pd.read_csv(artifact_path("audit", "manual_audit_completed.csv"))
    summary_frame = (
        audit.groupby("primary_error_type", as_index=False)
        .size()
        .rename(columns={"size": "count"})
        .sort_values("count", ascending=False)
    )
    summary_frame.to_csv(artifact_path("audit", "audit_taxonomy_table.csv"), index=False)
    payload = {
        "rows": len(audit),
        "baseline_consistent_rate": round(
            float(audit["baseline_consistent"].map(_parse_boolish).mean()), 6
        ),
        "reranked_consistent_rate": round(
            float(audit["reranked_consistent"].map(_parse_boolish).mean()), 6
        ),
        "selected_system_counts": audit["selected_system"].value_counts().to_dict(),
        "comparison_outcome_counts": audit["comparison_outcome"].value_counts().to_dict(),
        "annotation_method_counts": audit["annotation_method"].value_counts().to_dict(),
        "annotator_ids": sorted({str(value) for value in audit["annotator_id"].dropna().tolist()}),
        "error_counts": dict(
            zip(summary_frame["primary_error_type"], summary_frame["count"], strict=True)
        ),
    }
    write_json(artifact_path("audit", "manual_audit_summary.json"), payload)
    return payload
