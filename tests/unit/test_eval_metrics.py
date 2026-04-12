"""Regression tests for evaluation metric helpers."""

import pandas as pd

from factuality_rerank_xsum.eval.metrics import aggregate_rouge, metrics_for_selection


def test_aggregate_rouge_returns_stable_keys_for_empty_inputs() -> None:
    """Empty selections should still return the full ROUGE schema."""

    assert aggregate_rouge([], []) == {
        "rouge1": 0.0,
        "rouge2": 0.0,
        "rougeL": 0.0,
        "rougeLsum": 0.0,
    }


def test_metrics_for_selection_returns_zeroed_metrics_for_empty_frames() -> None:
    """Empty selections should not propagate NaN aggregate metrics."""

    frame = pd.DataFrame(
        columns=[
            "summary",
            "reference",
            "summac_style_score",
            "factcc_style_score",
            "entity_support_score",
            "summary_len_tokens",
        ]
    )

    assert metrics_for_selection(frame) == {
        "rouge1": 0.0,
        "rouge2": 0.0,
        "rougeL": 0.0,
        "rougeLsum": 0.0,
        "summac_style_score": 0.0,
        "factcc_style_score": 0.0,
        "entity_support_score": 0.0,
        "factuality_composite": 0.0,
        "summary_len_tokens": 0.0,
    }
