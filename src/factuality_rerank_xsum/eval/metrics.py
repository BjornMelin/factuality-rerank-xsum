"""Compute ROUGE-based evaluation aggregates for selected summaries."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
from rouge_score import rouge_scorer

from factuality_rerank_xsum.utils.text import split_sentences

if TYPE_CHECKING:
    from collections.abc import Sequence


ROUGE_KEYS = ("rouge1", "rouge2", "rougeL", "rougeLsum")


def _scorer() -> rouge_scorer.RougeScorer:
    return rouge_scorer.RougeScorer(list(ROUGE_KEYS), use_stemmer=True)


def _prepare_for_rouge_lsum(text: str) -> str:
    return "\n".join(split_sentences(text.strip()))


def per_example_rouge(prediction: str, reference: str) -> dict[str, float]:
    """Compute per-example ROUGE metrics for one prediction/reference pair.

    Args:
        prediction: Candidate summary text.
        reference: Reference summary text.

    Returns:
        Rounded ROUGE metrics keyed by metric name.
    """

    scorer = _scorer()
    scores = scorer.score(_prepare_for_rouge_lsum(reference), _prepare_for_rouge_lsum(prediction))
    return {metric: round(value.fmeasure, 6) for metric, value in scores.items()}


def aggregate_rouge(predictions: Sequence[str], references: Sequence[str]) -> dict[str, float]:
    """Aggregate per-example ROUGE scores across paired sequences.

    Args:
        predictions: Candidate summaries.
        references: Reference summaries aligned with `predictions`.

    Returns:
        Mean ROUGE metrics across all provided pairs.
    """

    rows = [
        per_example_rouge(prediction, reference)
        for prediction, reference in zip(predictions, references, strict=True)
    ]
    if not rows:
        return dict.fromkeys(ROUGE_KEYS, 0.0)
    frame = pd.DataFrame(rows)
    return {column: round(float(frame[column].mean()), 6) for column in frame.columns}


def metrics_for_selection(frame: pd.DataFrame) -> dict[str, float]:
    """Summarize automatic metrics for a selected-summary dataframe.

    Args:
        frame: Evaluation rows containing summaries, references, and scorer
            outputs.

    Returns:
        Aggregate ROUGE and factuality metrics for the selection.
    """

    if frame.empty:
        return {
            **dict.fromkeys(ROUGE_KEYS, 0.0),
            "summac_style_score": 0.0,
            "factcc_style_score": 0.0,
            "entity_support_score": 0.0,
            "factuality_composite": 0.0,
            "summary_len_tokens": 0.0,
        }

    rouge = aggregate_rouge(
        frame["summary"].astype(str).tolist(),
        frame["reference"].astype(str).tolist(),
    )
    return {
        **rouge,
        "summac_style_score": round(float(frame["summac_style_score"].mean()), 6),
        "factcc_style_score": round(float(frame["factcc_style_score"].mean()), 6),
        "entity_support_score": round(float(frame["entity_support_score"].mean()), 6),
        "factuality_composite": round(
            float(
                frame[["summac_style_score", "factcc_style_score", "entity_support_score"]]
                .mean(axis=1)
                .mean()
            ),
            6,
        ),
        "summary_len_tokens": round(float(frame["summary_len_tokens"].mean()), 6),
    }


def enrich_with_rouge(frame: pd.DataFrame) -> pd.DataFrame:
    """Attach per-example ROUGE columns to a dataframe of summaries.

    Args:
        frame: Rows containing `summary` and `reference` columns.

    Returns:
        A copy of the input frame with ROUGE metrics appended.
    """

    scored = frame.copy()
    rouge_rows = [
        per_example_rouge(summary, reference)
        for summary, reference in zip(
            scored["summary"].astype(str).tolist(),
            scored["reference"].astype(str).tolist(),
            strict=True,
        )
    ]
    rouge_frame = pd.DataFrame(rouge_rows)
    for column in rouge_frame.columns:
        scored[column] = rouge_frame[column]
    return scored
