"""Regression tests for evaluation metric helpers."""

from factuality_rerank_xsum.eval.metrics import aggregate_rouge


def test_aggregate_rouge_returns_stable_keys_for_empty_inputs() -> None:
    """Empty selections should still return the full ROUGE schema."""

    assert aggregate_rouge([], []) == {
        "rouge1": 0.0,
        "rouge2": 0.0,
        "rougeL": 0.0,
        "rougeLsum": 0.0,
    }
