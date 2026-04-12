from __future__ import annotations

from typing import Any

import pandas as pd

from factuality_rerank_xsum.artifacts.layout import comparison_table_path
from factuality_rerank_xsum.audit.taxonomy import build_audit_rows
from factuality_rerank_xsum.utils.io import write_json
from factuality_rerank_xsum.utils.paths import artifact_path, data_path


def run_sample_manual_audit() -> pd.DataFrame:
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
    )
    summary_frame.to_csv(artifact_path("audit", "audit_taxonomy_table.csv"), index=False)
    payload = {
        "rows": len(audit),
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
