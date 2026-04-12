from __future__ import annotations

from typing import TypedDict

import pandas as pd

from factuality_rerank_xsum.scorers.entity_support import score_entity_support
from factuality_rerank_xsum.scorers.factcc_style import score_factcc_style
from factuality_rerank_xsum.utils.text import split_sentences

NO_ISSUE = "No clear factual issue"
ENTITY_ISSUE = "Entity swap / wrong named entity / unsupported named entity"
NUMBER_ISSUE = "Number or date distortion"
NEGATION_ISSUE = "Negation / polarity / stance reversal"
RELATION_ISSUE = "Unsupported relation / unsupported event composition / unsupported causal link"
WORLD_KNOWLEDGE_ISSUE = "Source-unsupported but plausibly factual world knowledge addition"


class SummaryAudit(TypedDict):
    consistent: bool
    primary_error_type: str
    secondary_error_type: str
    world_knowledge_addition: bool
    notes: str


def classify_summary(source: str, summary: str) -> SummaryAudit:
    entity = score_entity_support(source, summary)
    factcc = score_factcc_style(source, summary)

    entity_count = int(entity["unsupported_entity_count"])
    number_count = int(entity["unsupported_number_count"] + entity["unsupported_date_count"])
    negation = factcc["factcc_style_negation_mismatch"]
    relation = factcc["factcc_style_relation_penalty"]
    support = entity["entity_support_score"]

    if number_count > 0:
        primary = NUMBER_ISSUE
    elif entity_count > 0:
        primary = ENTITY_ISSUE
    elif negation > 0:
        primary = NEGATION_ISSUE
    elif relation > 0:
        primary = RELATION_ISSUE
    elif support < 0.45:
        primary = WORLD_KNOWLEDGE_ISSUE
    else:
        primary = NO_ISSUE

    consistent = primary == NO_ISSUE and factcc["factcc_style_score"] >= 0.55
    return {
        "consistent": consistent,
        "primary_error_type": primary,
        "secondary_error_type": "" if consistent else NO_ISSUE,
        "world_knowledge_addition": primary == WORLD_KNOWLEDGE_ISSUE,
        "notes": (
            f"Sentence count={len(split_sentences(summary))}; "
            f"entity_support={support:.3f}; factcc_style={factcc['factcc_style_score']:.3f}"
        ),
    }


def build_audit_rows(comparison_frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in comparison_frame.iterrows():
        baseline_review = classify_summary(str(row["document"]), str(row["baseline_summary"]))
        reranked_review = classify_summary(str(row["document"]), str(row["reranked_summary"]))
        selected_system = "reranked"
        if baseline_review["consistent"] and not reranked_review["consistent"]:
            selected_system = "baseline"
        elif reranked_review["consistent"] == baseline_review["consistent"]:
            if float(row["reranked_factcc_style_score"]) < float(
                row["baseline_factcc_style_score"]
            ):
                selected_system = "baseline"

        selected_review = reranked_review if selected_system == "reranked" else baseline_review
        rows.append(
            {
                "id": row["id"],
                "split": row["split"],
                "document": row["document"],
                "reference": row["reference"],
                "baseline_summary": row["baseline_summary"],
                "reranked_summary": row["reranked_summary"],
                "selected_system": selected_system,
                "baseline_consistent": baseline_review["consistent"],
                "reranked_consistent": reranked_review["consistent"],
                "primary_error_type": selected_review["primary_error_type"],
                "secondary_error_type": selected_review["secondary_error_type"],
                "world_knowledge_addition": selected_review["world_knowledge_addition"],
                "notes": selected_review["notes"],
            }
        )
    return pd.DataFrame(rows)
