from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
from rouge_score import rouge_scorer

from factuality_rerank_xsum.utils.text import split_sentences


def _scorer() -> rouge_scorer.RougeScorer:
    return rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL", "rougeLsum"], use_stemmer=True)


def _prepare_for_rouge_lsum(text: str) -> str:
    return "\n".join(split_sentences(text.strip()))


def per_example_rouge(prediction: str, reference: str) -> dict[str, float]:
    scorer = _scorer()
    scores = scorer.score(_prepare_for_rouge_lsum(reference), _prepare_for_rouge_lsum(prediction))
    return {metric: round(value.fmeasure, 6) for metric, value in scores.items()}


def aggregate_rouge(predictions: Sequence[str], references: Sequence[str]) -> dict[str, float]:
    rows = [
        per_example_rouge(prediction, reference)
        for prediction, reference in zip(predictions, references, strict=True)
    ]
    frame = pd.DataFrame(rows)
    return {column: round(float(frame[column].mean()), 6) for column in frame.columns}


def metrics_for_selection(frame: pd.DataFrame) -> dict[str, float]:
    rouge = aggregate_rouge(
        frame["summary"].astype(str).tolist(),
        frame["reference"].astype(str).tolist(),
    )
    aggregate = {
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
    return aggregate


def enrich_with_rouge(frame: pd.DataFrame) -> pd.DataFrame:
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
