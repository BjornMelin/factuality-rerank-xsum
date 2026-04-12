"""Weight-search stage for rerank configuration selection."""

from __future__ import annotations

from typing import Any

import pandas as pd

from factuality_rerank_xsum.artifacts.layout import merged_table_path, search_selection_path
from factuality_rerank_xsum.constants import BEAM_SIZES, BEST_BALANCED, BEST_FACTUALITY, BEST_SIMPLE
from factuality_rerank_xsum.eval.metrics import enrich_with_rouge, metrics_for_selection
from factuality_rerank_xsum.rerank.fusion import (
    fuse_scores,
    named_weight_configs,
    pareto_frontier,
    select_top_candidate,
    weight_grid,
)
from factuality_rerank_xsum.utils.io import read_yaml, write_yaml
from factuality_rerank_xsum.utils.paths import artifact_path, config_path


def _required_search_row(frame: pd.DataFrame, *, description: str) -> pd.Series:
    if frame.empty:
        msg = f"Missing search result row for {description}"
        raise ValueError(msg)
    return frame.iloc[0]


def run_search_weights() -> pd.DataFrame:
    """Search rerank weights on the validation split and persist winners."""

    results: list[dict[str, Any]] = []
    normalization = "zscore"
    named = named_weight_configs()
    for beam in BEAM_SIZES:
        frame = pd.read_parquet(merged_table_path("val_tune", beam))
        configs = list(named.items()) + [
            (f"custom_{index:04d}", weights)
            for index, weights in enumerate(weight_grid(step=0.25), start=1)
        ]
        for system_name, weights in configs:
            fused = fuse_scores(frame, weights, normalization)
            selected = select_top_candidate(fused)
            selected = enrich_with_rouge(selected)
            selected["factuality_composite"] = selected[
                ["summac_style_score", "factcc_style_score", "entity_support_score"]
            ].mean(axis=1)
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
    baseline_row = _required_search_row(
        result_frame.query("system == 'logprob_only' and beam_size == 8").sort_values(
            "factuality_composite", ascending=False
        ),
        description="system=logprob_only beam_size=8",
    )
    rouge_tolerance = float(
        read_yaml(config_path("rerank", "weight_grid.yaml"))["rouge_lsum_tolerance"]
    )
    balanced_candidates = result_frame[
        result_frame["rougeLsum"] >= float(baseline_row["rougeLsum"]) - rouge_tolerance
    ]
    best_balanced = _required_search_row(
        balanced_candidates.sort_values(
            ["factuality_composite", "rougeLsum"], ascending=[False, False]
        ),
        description="best_balanced candidate",
    )
    best_factuality = _required_search_row(
        result_frame,
        description="best_factuality candidate",
    )
    simple_candidates = result_frame[
        result_frame["system"].isin(
            ["logprob_plus_summac", "logprob_plus_factcc", "summac_only", "factcc_only"]
        )
    ]
    best_simple = _required_search_row(
        simple_candidates.sort_values(
            ["factuality_composite", "rougeLsum"], ascending=[False, False]
        ),
        description="best_simple candidate",
    )
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
        write_yaml(search_selection_path(name), payload)
    pareto = pareto_frontier(
        result_frame[["system", "beam_size", "rougeLsum", "factuality_composite"]],
        "rougeLsum",
        "factuality_composite",
    )
    pareto.to_csv(artifact_path("search", "pareto_points.csv"), index=False)
    write_yaml(
        config_path("rerank", "final_selection.yaml"),
        read_yaml(search_selection_path(BEST_BALANCED)),
    )
    return result_frame
