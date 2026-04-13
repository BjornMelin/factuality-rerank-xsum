"""Evaluation stages for reranked selections and bootstrap metrics."""

from __future__ import annotations

from typing import Any

import pandas as pd

from factuality_rerank_xsum.artifacts.layout import comparison_table_path, selected_table_path
from factuality_rerank_xsum.constants import (
    BASELINE_SYSTEM,
    BEAM_SIZES,
    BEST_BALANCED,
    BEST_FACTUALITY,
    BEST_SIMPLE,
)
from factuality_rerank_xsum.eval.bootstrap import bootstrap_difference
from factuality_rerank_xsum.eval.metrics import metrics_for_selection
from factuality_rerank_xsum.rerank.application import apply_system, load_selection_config
from factuality_rerank_xsum.rerank.fusion import named_weight_configs
from factuality_rerank_xsum.utils.io import write_json
from factuality_rerank_xsum.utils.paths import artifact_path


def _comparison_table(baseline: pd.DataFrame, reranked: pd.DataFrame) -> pd.DataFrame:
    """Build the comparison table used by audit and reporting stages.

    Args:
        baseline: Baseline system selections for one split.
        reranked: Reranked system selections for the same split.

    Returns:
        A normalized comparison table with paired baseline and reranked fields.
    """

    missing_from_reranked = sorted(
        set(baseline["id"].astype(str)) - set(reranked["id"].astype(str))
    )
    missing_from_baseline = sorted(
        set(reranked["id"].astype(str)) - set(baseline["id"].astype(str))
    )
    if missing_from_reranked or missing_from_baseline:
        msg = (
            "Baseline and reranked selections must cover the same example IDs. "
            f"Missing from reranked: {missing_from_reranked[:5]}; "
            f"missing from baseline: {missing_from_baseline[:5]}"
        )
        raise ValueError(msg)

    comparison = baseline.merge(
        reranked,
        on="id",
        suffixes=("_baseline", "_reranked"),
        validate="one_to_one",
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
    return comparison[keep_columns]


def run_rerank_and_eval() -> pd.DataFrame:
    """Apply canonical rerank systems and write evaluation artifacts.

    Returns:
        The per-system metrics table written to `artifacts/eval/system_metrics.csv`.
    """

    weight_configs = named_weight_configs()
    systems: list[tuple[str, dict[str, Any]]] = [
        (
            BASELINE_SYSTEM,
            {
                "beam_size": 8,
                "normalization": "zscore",
                "weights": weight_configs["logprob_only"],
            },
        ),
        (BEST_BALANCED, load_selection_config(BEST_BALANCED)),
        (BEST_FACTUALITY, load_selection_config(BEST_FACTUALITY)),
        (BEST_SIMPLE, load_selection_config(BEST_SIMPLE)),
    ]
    for beam in BEAM_SIZES:
        systems.append(
            (
                f"logprob_only_beam_{beam}",
                {
                    "beam_size": beam,
                    "normalization": "zscore",
                    "weights": weight_configs["logprob_only"],
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
                    "weights": weight_configs[name],
                },
            )
        )
    metrics_rows: list[dict[str, Any]] = []
    for split in ["val_full", "test_final"]:
        for system_name, config in systems:
            selected = apply_system(
                split,
                system_name=system_name,
                beam_size=int(config["beam_size"]),
                weights=dict(config["weights"]),
                normalization=str(config["normalization"]),
            )
            metrics_rows.append(
                {
                    "split": split,
                    "system": system_name,
                    "beam_size": int(config["beam_size"]),
                    "normalization": str(config["normalization"]),
                    **metrics_for_selection(selected),
                }
            )
    metrics_frame = pd.DataFrame(metrics_rows)
    metrics_frame.to_csv(artifact_path("eval", "system_metrics.csv"), index=False)

    for split in ["val_full", "test_final"]:
        baseline = pd.read_parquet(selected_table_path(split, BASELINE_SYSTEM))
        reranked = pd.read_parquet(selected_table_path(split, BEST_BALANCED))
        _comparison_table(baseline, reranked).to_csv(comparison_table_path(split), index=False)
    return metrics_frame


def run_bootstrap_metrics() -> dict[str, Any]:
    """Compute bootstrap confidence intervals for the main test comparison.

    Returns:
        The bootstrap confidence-interval payload written to tracked artifacts.
    """

    baseline = pd.read_parquet(selected_table_path("test_final", BASELINE_SYSTEM))
    contender = pd.read_parquet(selected_table_path("test_final", BEST_BALANCED))
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
