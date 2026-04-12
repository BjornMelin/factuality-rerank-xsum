"""Canonical artifact paths for generated pipeline outputs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from factuality_rerank_xsum.utils.paths import artifact_path

if TYPE_CHECKING:
    from pathlib import Path


def candidate_table_path(split: str, beam_size: int) -> Path:
    """Return the candidate-table path for a split and beam size."""

    return artifact_path("generations", split, f"beam_{beam_size}", "candidates.parquet")


def score_table_path(stage: str, split: str, beam_size: int) -> Path:
    """Return the scorer output path for one stage, split, and beam size."""

    return artifact_path("scores", stage, split, f"beam_{beam_size}.parquet")


def merged_table_path(split: str, beam_size: int) -> Path:
    """Return the merged-score table path for a split and beam size."""

    return artifact_path("scores", "merged", split, f"beam_{beam_size}.parquet")


def selected_table_path(split: str, system: str) -> Path:
    """Return the selected-candidate table path for one system and split."""

    return artifact_path("eval", f"{split}_{system}_selected.parquet")


def comparison_table_path(split: str) -> Path:
    """Return the comparison CSV path for a split."""

    return artifact_path("eval", f"{split}_comparison_table.csv")


def search_selection_path(name: str) -> Path:
    """Return the saved rerank-selection config path."""

    return artifact_path("search", f"{name}.yaml")
