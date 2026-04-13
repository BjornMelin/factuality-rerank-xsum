"""Canonical artifact paths for generated pipeline outputs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from factuality_rerank_xsum.utils.paths import artifact_path

if TYPE_CHECKING:
    from pathlib import Path


def candidate_table_path(split: str, beam_size: int) -> Path:
    """Return the candidate-table path for a split and beam size.

    Args:
        split: Pipeline split name.
        beam_size: Beam width used for candidate generation.

    Returns:
        The canonical parquet path for generated candidates.
    """

    return artifact_path("generations", split, f"beam_{beam_size}", "candidates.parquet")


def score_table_path(stage: str, split: str, beam_size: int) -> Path:
    """Return the scorer output path for one stage, split, and beam size.

    Args:
        stage: Scoring stage name.
        split: Pipeline split name.
        beam_size: Beam width used for candidate generation.

    Returns:
        The canonical parquet path for scorer outputs.
    """

    return artifact_path("scores", stage, split, f"beam_{beam_size}.parquet")


def merged_table_path(split: str, beam_size: int) -> Path:
    """Return the merged-score table path for a split and beam size.

    Args:
        split: Pipeline split name.
        beam_size: Beam width used for candidate generation.

    Returns:
        The canonical parquet path for merged scorer outputs.
    """

    return artifact_path("scores", "merged", split, f"beam_{beam_size}.parquet")


def selected_table_path(split: str, system: str) -> Path:
    """Return the selected-candidate table path for one system and split.

    Args:
        split: Pipeline split name.
        system: Selection-system identifier.

    Returns:
        The canonical parquet path for selected candidates.
    """

    return artifact_path("eval", f"{split}_{system}_selected.parquet")


def comparison_table_path(split: str) -> Path:
    """Return the comparison CSV path for a split.

    Args:
        split: Pipeline split name.

    Returns:
        The canonical CSV path for baseline-versus-reranked comparisons.
    """

    return artifact_path("eval", f"{split}_comparison_table.csv")


def search_selection_path(name: str) -> Path:
    """Return the saved rerank-selection config path.

    Args:
        name: Saved rerank-selection name.

    Returns:
        The canonical YAML path for a persisted search selection.
    """

    return artifact_path("search", f"{name}.yaml")
