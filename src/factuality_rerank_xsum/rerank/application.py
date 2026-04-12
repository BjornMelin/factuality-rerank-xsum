from __future__ import annotations

from typing import Any

import pandas as pd

from factuality_rerank_xsum.artifacts.layout import (
    merged_table_path,
    search_selection_path,
    selected_table_path,
)
from factuality_rerank_xsum.eval.metrics import enrich_with_rouge
from factuality_rerank_xsum.rerank.fusion import fuse_scores, select_top_candidate
from factuality_rerank_xsum.utils.io import read_yaml
from factuality_rerank_xsum.utils.paths import artifact_path


def load_selection_config(name: str) -> dict[str, Any]:
    """Load one persisted rerank selection config.

    Args:
        name: Saved selection name.

    Returns:
        The persisted rerank configuration payload.
    """

    return read_yaml(search_selection_path(name))


def apply_system(
    split: str, *, system_name: str, beam_size: int, weights: dict[str, float], normalization: str
) -> pd.DataFrame:
    """Apply one rerank system to a merged candidate table.

    Args:
        split: Pipeline split name.
        system_name: Logical name for the rerank system.
        beam_size: Beam size whose merged table should be selected.
        weights: Score weights passed to the fusion stage.
        normalization: Score normalization mode.

    Returns:
        The selected candidates enriched with ROUGE and composite factuality.
    """

    merged = pd.read_parquet(merged_table_path(split, beam_size))
    fused = fuse_scores(merged, weights, normalization)
    selected = select_top_candidate(fused)
    selected = enrich_with_rouge(selected)
    selected["factuality_composite"] = selected[
        ["summac_style_score", "factcc_style_score", "entity_support_score"]
    ].mean(axis=1)
    selected["system"] = system_name
    selected["beam_size"] = beam_size
    selected["normalization"] = normalization
    selected_table_path(split, system_name).parent.mkdir(parents=True, exist_ok=True)
    selected.to_parquet(selected_table_path(split, system_name), index=False)
    selected.to_csv(artifact_path("eval", f"{split}_{system_name}_selected.csv"), index=False)
    return selected
