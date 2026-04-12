"""Audit stages for generating and summarizing manual-review artifacts."""

from __future__ import annotations

from typing import Any

import pandas as pd

from factuality_rerank_xsum.artifacts.layout import comparison_table_path
from factuality_rerank_xsum.audit.taxonomy import build_audit_rows
from factuality_rerank_xsum.utils.io import write_json
from factuality_rerank_xsum.utils.paths import artifact_path, data_path


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


def run_sample_manual_audit() -> pd.DataFrame:
    """Build the manual-audit template and derived audit examples.

    Returns:
        The completed audit rows derived from the comparison table.
    """

    comparison = pd.read_csv(comparison_table_path("test_final"))
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
    template_path = data_path("audit", "manual_audit_template.csv")
    template_path.parent.mkdir(parents=True, exist_ok=True)
    audit_dir = artifact_path("audit")
    audit_dir.mkdir(parents=True, exist_ok=True)
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
    )[template_columns].to_csv(template_path, index=False)
    audit = build_audit_rows(comparison)
    audit.to_csv(audit_dir / "manual_audit_completed.csv", index=False)
    audit.to_csv(audit_dir / "audit_examples_for_paper.csv", index=False)
    return audit


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
        "error_counts": dict(
            zip(summary_frame["primary_error_type"], summary_frame["count"], strict=True)
        ),
    }
    write_json(artifact_path("audit", "manual_audit_summary.json"), payload)
    return payload
