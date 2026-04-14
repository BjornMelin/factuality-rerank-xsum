from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
import pytest

from factuality_rerank_xsum.constants import PIPELINE_SPLITS
from factuality_rerank_xsum.runtime.artifact_truth import assert_artifact_truth
from factuality_rerank_xsum.utils.io import write_json
from factuality_rerank_xsum.utils.paths import artifact_path, data_path, output_path

if TYPE_CHECKING:
    from pathlib import Path


def _patch_project_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("factuality_rerank_xsum.utils.paths.project_root", lambda: tmp_path)


def _setup_valid_artifacts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    include_offline_column: bool = False,
    wrong_generation_count: bool = False,
) -> None:
    _patch_project_root(monkeypatch, tmp_path)
    expected_ids_by_split = {split: [f"{split}-1", f"{split}-2"] for split in PIPELINE_SPLITS}
    for split, ids in expected_ids_by_split.items():
        split_path = data_path("processed", "splits", f"{split}_ids.txt")
        split_path.parent.mkdir(parents=True, exist_ok=True)
        split_path.write_text(
            "\n".join(ids) + "\n",
            encoding="utf-8",
        )

    write_json(
        artifact_path("data", "dataset_manifest.json"),
        {
            "dataset_mode": "online_hub",
            "split_sampling": {
                split: {"rows_selected": len(ids), "limit": len(ids), "source_split": "validation"}
                for split, ids in expected_ids_by_split.items()
            },
        },
    )
    split_examples = {
        split: {"examples": (1 if wrong_generation_count and split == "test_final" else len(ids))}
        for split, ids in expected_ids_by_split.items()
    }
    write_json(
        artifact_path("generations", "generation_summary.json"),
        {
            "beam_sizes": [4, 8, 16],
            "generator_mode": "huggingface_generation",
            "generator_model": "facebook/bart-large-xsum",
            "splits": split_examples,
        },
    )

    for split, ids in expected_ids_by_split.items():
        for beam_size in [4, 8, 16]:
            rows: list[dict[str, object]] = []
            for example_id in ids:
                for rank in range(beam_size):
                    row: dict[str, object] = {
                        "id": example_id,
                        "split": split,
                        "summary": f"{example_id} summary {rank}",
                        "candidate_strategy": f"hf_beam_{rank}",
                        "generator_mode": "huggingface_generation",
                        "requested_model": "facebook/bart-large-xsum",
                        "requested_revision": "rev-gen",
                    }
                    if include_offline_column:
                        row["offline_generator_noise"] = 0.5
                    rows.append(row)
            frame = pd.DataFrame(rows)
            target = artifact_path("generations", split, f"beam_{beam_size}", "candidates.parquet")
            target.parent.mkdir(parents=True, exist_ok=True)
            frame.to_parquet(target, index=False)

    for split in ["val_full", "test_final"]:
        ids = expected_ids_by_split[split]
        baseline = pd.DataFrame({"id": ids})
        reranked = pd.DataFrame({"id": ids})
        baseline_path = artifact_path("eval", f"{split}_baseline_best_likelihood_selected.parquet")
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline.to_parquet(baseline_path, index=False)
        reranked_path = artifact_path("eval", f"{split}_best_balanced_selected.parquet")
        reranked_path.parent.mkdir(parents=True, exist_ok=True)
        reranked.to_parquet(reranked_path, index=False)
        comparison_path = artifact_path("eval", f"{split}_comparison_table.csv")
        comparison_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"id": ids}).to_csv(comparison_path, index=False)

    audit_rows = [
        {
            "id": f"audit-{index:02d}",
            "annotator_id": "codex",
            "annotation_method": "ai-assisted expert adjudication",
        }
        for index in range(24)
    ]
    audit_frame = pd.DataFrame(audit_rows)
    audit_path = artifact_path("audit", "manual_audit_completed.csv")
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_frame.to_csv(audit_path, index=False)
    write_json(artifact_path("audit", "manual_audit_summary.json"), {"rows": 24})
    output_path("final").mkdir(parents=True, exist_ok=True)
    audit_frame.to_csv(output_path("final", "manual_audit.csv"), index=False)
    write_json(output_path("final", "manual_audit_summary.json"), {"rows": 24})
    pd.DataFrame(
        [
            {"split": "val_full", "system": "baseline_best_likelihood"},
            {"split": "val_full", "system": "best_balanced"},
            {"split": "val_full", "system": "best_factuality"},
            {"split": "val_full", "system": "best_simple"},
            {"split": "test_final", "system": "baseline_best_likelihood"},
            {"split": "test_final", "system": "best_balanced"},
            {"split": "test_final", "system": "best_factuality"},
            {"split": "test_final", "system": "best_simple"},
        ]
    ).to_csv(output_path("final", "main_metrics.csv"), index=False)


def test_assert_artifact_truth_accepts_consistent_artifacts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _setup_valid_artifacts(monkeypatch, tmp_path)

    report = assert_artifact_truth(stage_name="package", require_final_outputs=True)

    assert report["ok"] is True
    assert report["audit"]["rows"] == 24


def test_assert_artifact_truth_rejects_offline_generation_columns(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _setup_valid_artifacts(monkeypatch, tmp_path, include_offline_column=True)

    with pytest.raises(ValueError, match="offline_generator_noise"):
        assert_artifact_truth(stage_name="figures", require_final_outputs=False)


def test_assert_artifact_truth_rejects_generation_count_mismatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _setup_valid_artifacts(monkeypatch, tmp_path, wrong_generation_count=True)

    with pytest.raises(ValueError, match="generation_summary split test_final reports examples=1"):
        assert_artifact_truth(stage_name="figures", require_final_outputs=False)
