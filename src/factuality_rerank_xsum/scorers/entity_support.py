from __future__ import annotations

from collections.abc import Iterable
from typing import TypedDict

import pandas as pd

from factuality_rerank_xsum.utils.text import (
    bounded,
    extract_dates,
    extract_entities,
    extract_numbers,
    lexical_precision,
)


class EntitySupportScore(TypedDict):
    entity_precision: float
    number_precision: float
    date_precision: float
    entity_support_score: float
    unsupported_entity_count: float
    unsupported_number_count: float
    unsupported_date_count: float
    unsupported_entities: list[str]
    unsupported_numbers: list[str]
    unsupported_dates: list[str]


def _precision(source_items: Iterable[str], candidate_items: Iterable[str]) -> float:
    source_set = {item.lower() for item in source_items}
    candidate_list = [item.lower() for item in candidate_items]
    if not candidate_list:
        return 1.0
    supported = sum(1 for item in candidate_list if item in source_set)
    return supported / len(candidate_list)


def score_entity_support(source: str, summary: str) -> EntitySupportScore:
    source_entities = extract_entities(source)
    summary_entities = extract_entities(summary)
    source_numbers = extract_numbers(source)
    summary_numbers = extract_numbers(summary)
    source_dates = extract_dates(source)
    summary_dates = extract_dates(summary)

    entity_precision = _precision(source_entities, summary_entities)
    number_precision = _precision(source_numbers, summary_numbers)
    date_precision = _precision(source_dates, summary_dates)
    lexical = lexical_precision(set(source.lower().split()), summary.lower().split())

    source_entity_set = {value.lower() for value in source_entities}
    source_number_set = {value.lower() for value in source_numbers}
    source_date_set = {value.lower() for value in source_dates}

    support_score = bounded(
        (0.45 * entity_precision)
        + (0.25 * number_precision)
        + (0.10 * date_precision)
        + (0.20 * lexical)
    )

    unsupported_entities = [
        item for item in summary_entities if item.lower() not in source_entity_set
    ]
    unsupported_numbers = [
        item for item in summary_numbers if item.lower() not in source_number_set
    ]
    unsupported_dates = [item for item in summary_dates if item.lower() not in source_date_set]

    return {
        "entity_precision": round(entity_precision, 6),
        "number_precision": round(number_precision, 6),
        "date_precision": round(date_precision, 6),
        "entity_support_score": round(support_score, 6),
        "unsupported_entity_count": float(len(unsupported_entities)),
        "unsupported_number_count": float(len(unsupported_numbers)),
        "unsupported_date_count": float(len(unsupported_dates)),
        "unsupported_entities": unsupported_entities,
        "unsupported_numbers": unsupported_numbers,
        "unsupported_dates": unsupported_dates,
    }


def score_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    records = []
    for _, row in frame.iterrows():
        records.append(
            {
                "id": row["id"],
                "candidate_hash": row["candidate_hash"],
                **score_entity_support(str(row["document"]), str(row["summary"])),
            }
        )
    return pd.DataFrame.from_records(records)
