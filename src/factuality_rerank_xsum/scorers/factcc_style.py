from __future__ import annotations

import re
from typing import TypedDict

import pandas as pd

from factuality_rerank_xsum.scorers.entity_support import score_entity_support
from factuality_rerank_xsum.utils.text import bounded, content_tokens, lexical_precision

NEGATION_PATTERN = re.compile(r"\b(no|not|never|without|none)\b", re.IGNORECASE)


class FactCCStyleScore(TypedDict):
    factcc_style_lexical_support: float
    factcc_style_negation_mismatch: float
    factcc_style_relation_penalty: float
    factcc_style_score: float


def _negation_mismatch(source: str, summary: str) -> float:
    return float(bool(NEGATION_PATTERN.search(source)) != bool(NEGATION_PATTERN.search(summary)))


def _relation_penalty(source: str, summary: str) -> float:
    relation_pairs = [
        ("confirmed", "denied"),
        ("won", "lost"),
        ("charged", "cleared"),
        ("killed", "injured"),
        ("approved", "rejected"),
        ("agreed", "opposed"),
    ]
    lowered_source = source.lower()
    lowered_summary = summary.lower()
    for positive, negative in relation_pairs:
        if positive in lowered_source and negative in lowered_summary:
            return 1.0
        if negative in lowered_source and positive in lowered_summary:
            return 1.0
    return 0.0


def score_factcc_style(source: str, summary: str) -> FactCCStyleScore:
    support_features = score_entity_support(source, summary)
    lexical = lexical_precision(content_tokens(source), content_tokens(summary))
    negation = _negation_mismatch(source, summary)
    relation = _relation_penalty(source, summary)

    penalty = (
        (1 - support_features["entity_precision"]) * 0.30
        + (1 - support_features["number_precision"]) * 0.25
        + (1 - support_features["date_precision"]) * 0.10
        + (negation * 0.20)
        + (relation * 0.20)
    )
    score = bounded((0.65 * lexical) + (0.35 * support_features["entity_support_score"]) - penalty)
    return {
        "factcc_style_lexical_support": round(lexical, 6),
        "factcc_style_negation_mismatch": round(negation, 6),
        "factcc_style_relation_penalty": round(relation, 6),
        "factcc_style_score": round(score, 6),
    }


def score_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    records = []
    for _, row in frame.iterrows():
        records.append(
            {
                "id": row["id"],
                "candidate_hash": row["candidate_hash"],
                **score_factcc_style(str(row["document"]), str(row["summary"])),
            }
        )
    return pd.DataFrame.from_records(records)
