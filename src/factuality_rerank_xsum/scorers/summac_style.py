from __future__ import annotations

from typing import TypedDict

import pandas as pd

from factuality_rerank_xsum.scorers.entity_support import score_entity_support
from factuality_rerank_xsum.utils.text import (
    bounded,
    content_tokens,
    f1,
    lexical_precision,
    lexical_recall,
    split_sentences,
)


class SummaCStyleScore(TypedDict):
    summac_style_support: float
    summac_style_contradiction_penalty: float
    summac_style_score: float


def score_summac_style(source: str, summary: str) -> SummaCStyleScore:
    source_sentences = split_sentences(source)
    summary_sentences = split_sentences(summary)

    sentence_scores: list[float] = []
    for candidate_sentence in summary_sentences or [summary]:
        candidate_tokens = content_tokens(candidate_sentence)
        if not candidate_tokens:
            sentence_scores.append(0.0)
            continue
        per_source_scores: list[float] = []
        for source_sentence in source_sentences or [source]:
            source_tokens = content_tokens(source_sentence)
            precision = lexical_precision(source_tokens, candidate_tokens)
            recall = lexical_recall(source_tokens, candidate_tokens)
            per_source_scores.append(f1(precision, recall))
        sentence_scores.append(max(per_source_scores, default=0.0))

    entity_features = score_entity_support(source, summary)
    support = sum(sentence_scores) / max(len(sentence_scores), 1)
    contradiction_penalty = (
        (1 - entity_features["entity_precision"]) * 0.30
        + (1 - entity_features["number_precision"]) * 0.25
        + (1 - entity_features["date_precision"]) * 0.15
    )
    score = bounded(
        (0.75 * support) + (0.25 * entity_features["entity_support_score"]) - contradiction_penalty
    )
    return {
        "summac_style_support": round(support, 6),
        "summac_style_contradiction_penalty": round(contradiction_penalty, 6),
        "summac_style_score": round(score, 6),
    }


def score_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    records = []
    for _, row in frame.iterrows():
        records.append(
            {
                "id": row["id"],
                "candidate_hash": row["candidate_hash"],
                **score_summac_style(str(row["document"]), str(row["summary"])),
            }
        )
    return pd.DataFrame.from_records(records)
