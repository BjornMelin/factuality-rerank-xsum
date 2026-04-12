"""Compute SummaC-style entailment scores for summaries."""

from __future__ import annotations

from typing import Any, TypedDict

import pandas as pd
import torch

from factuality_rerank_xsum.scorers.entity_support import score_entity_support
from factuality_rerank_xsum.utils.io import read_yaml
from factuality_rerank_xsum.utils.paths import config_path
from factuality_rerank_xsum.utils.text import (
    bounded,
    content_tokens,
    f1,
    lexical_precision,
    lexical_recall,
    split_sentences,
)
from factuality_rerank_xsum.utils.transformers_runtime import (
    load_sequence_classifier_runtime,
    move_batch_to_device,
)


class SummaCStyleScore(TypedDict):
    """SummaC-style scoring features for one summary.

    Parameters:
        summac_style_support: Aggregated entailment support score.
        summac_style_contradiction_penalty: Contradiction penalty term.
        summac_style_score: Final SummaC-style factuality score.
    """

    summac_style_support: float
    summac_style_contradiction_penalty: float
    summac_style_score: float


def _summac_config() -> dict[str, Any]:
    return read_yaml(config_path("score", "summac.yaml"))


def _heuristic_score(source: str, summary: str) -> SummaCStyleScore:
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


def _source_chunks(source: str, chunk_size: int, chunk_limit: int) -> list[str]:
    sentences = split_sentences(source) or [source]
    chunks = [
        " ".join(sentences[index : index + chunk_size])
        for index in range(0, len(sentences), chunk_size)
    ]
    return [chunk for chunk in chunks[:chunk_limit] if chunk.strip()]


def _summary_sentences(summary: str, sentence_limit: int) -> list[str]:
    sentences = split_sentences(summary)
    trimmed = [sentence for sentence in sentences[:sentence_limit] if sentence.strip()]
    return trimmed or [summary]


def _nli_label_ids(label_map: dict[str, int]) -> tuple[int, int]:
    normalized = {key.lower(): value for key, value in label_map.items()}
    entailment = normalized.get("entailment")
    contradiction = normalized.get("contradiction")
    if entailment is None or contradiction is None:
        msg = f"NLI labels missing entailment/contradiction: {sorted(label_map)}"
        raise KeyError(msg)
    return entailment, contradiction


def _nli_probabilities(
    premises: list[str],
    hypotheses: list[str],
    *,
    config: dict[str, Any],
) -> list[tuple[float, float]]:
    tokenizer, model, device = load_sequence_classifier_runtime(
        str(config["requested_model"]),
        str(config.get("revision") or "") or None,
        str(config.get("device", "auto")),
    )
    label_map = {str(value): int(key) for key, value in model.config.id2label.items()}
    entailment_id, contradiction_id = _nli_label_ids(label_map)
    batch_size = int(config.get("batch_size", 8))
    max_length = int(config.get("max_length", 512))
    probabilities: list[tuple[float, float]] = []
    for start in range(0, len(premises), batch_size):
        batch_premises = premises[start : start + batch_size]
        batch_hypotheses = hypotheses[start : start + batch_size]
        encoded = tokenizer(
            batch_premises,
            batch_hypotheses,
            max_length=max_length,
            padding=True,
            truncation="only_first",
            return_tensors="pt",
        )
        encoded = move_batch_to_device(encoded, device)
        with torch.inference_mode():
            logits = model(**encoded).logits
        softmax = torch.softmax(logits, dim=-1).detach().cpu()
        for row in softmax:
            probabilities.append(
                (
                    float(row[entailment_id].item()),
                    float(row[contradiction_id].item()),
                )
            )
    return probabilities


def _aggregate_nli(
    source: str,
    summary: str,
    *,
    config: dict[str, Any],
) -> SummaCStyleScore:
    source_chunks = _source_chunks(
        source,
        int(config.get("source_chunk_size", 3)),
        int(config.get("source_chunk_limit", 8)),
    )
    summary_sentences = _summary_sentences(summary, int(config.get("summary_sentence_limit", 4)))
    premises: list[str] = []
    hypotheses: list[str] = []
    chunk_count = max(len(source_chunks), 1)
    for sentence in summary_sentences:
        chunks = source_chunks or [source]
        premises.extend(chunks)
        hypotheses.extend([sentence] * len(chunks))
    probabilities = _nli_probabilities(premises, hypotheses, config=config)
    entailment_support: list[float] = []
    contradiction_scores: list[float] = []
    for offset in range(0, len(probabilities), chunk_count):
        sentence_pairs = probabilities[offset : offset + chunk_count]
        entailment_support.append(max(pair[0] for pair in sentence_pairs))
        contradiction_scores.append(max(pair[1] for pair in sentence_pairs))
    support = sum(entailment_support) / max(len(entailment_support), 1)
    contradiction_penalty = sum(contradiction_scores) / max(len(contradiction_scores), 1)
    entity_features = score_entity_support(source, summary)
    score = bounded(
        (0.70 * support)
        + (0.20 * entity_features["entity_support_score"])
        - (0.30 * contradiction_penalty)
    )
    return {
        "summac_style_support": round(support, 6),
        "summac_style_contradiction_penalty": round(contradiction_penalty, 6),
        "summac_style_score": round(score, 6),
    }


def score_summac_style(
    source: str,
    summary: str,
    *,
    config: dict[str, Any] | None = None,
) -> SummaCStyleScore:
    """Score a summary with the configured SummaC-style scorer.

    Args:
        source: Source document text.
        summary: Candidate summary text.
        config: Optional scorer configuration override.

    Returns:
        SummaC-style feature scores and the combined factuality score.
    """

    active_config = config or _summac_config()
    if str(active_config.get("mode", "")) == "heuristic_summac_style":
        return _heuristic_score(source, summary)
    return _aggregate_nli(source, summary, config=active_config)


def score_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    """Score every row in a dataframe with the SummaC-style scorer.

    Args:
        frame: Rows containing document, summary, and candidate identifiers.

    Returns:
        A dataframe with SummaC-style feature columns for each candidate.
    """

    config = _summac_config()
    if str(config.get("mode", "")) == "heuristic_summac_style":
        records = []
        for _, row in frame.iterrows():
            records.append(
                {
                    "id": row["id"],
                    "candidate_hash": row["candidate_hash"],
                    **_heuristic_score(str(row["document"]), str(row["summary"])),
                }
            )
        return pd.DataFrame.from_records(records)

    row_boundaries: list[tuple[int, int, str, str, Any, Any]] = []
    premises: list[str] = []
    hypotheses: list[str] = []
    for _, row in frame.iterrows():
        source = str(row["document"])
        summary = str(row["summary"])
        source_chunks = _source_chunks(
            source,
            int(config.get("source_chunk_size", 3)),
            int(config.get("source_chunk_limit", 8)),
        )
        summary_sentences = _summary_sentences(
            summary, int(config.get("summary_sentence_limit", 4))
        )
        start = len(premises)
        chunks = source_chunks or [source]
        for sentence in summary_sentences:
            premises.extend(chunks)
            hypotheses.extend([sentence] * len(chunks))
        row_boundaries.append(
            (start, len(premises), source, summary, row["id"], row["candidate_hash"])
        )

    probabilities = _nli_probabilities(premises, hypotheses, config=config)
    records = []
    for start, end, source, summary, example_id, candidate_hash in row_boundaries:
        row_pairs = probabilities[start:end]
        chunk_count = max(
            len(
                _source_chunks(
                    source,
                    int(config.get("source_chunk_size", 3)),
                    int(config.get("source_chunk_limit", 8)),
                )
            ),
            1,
        )
        entailment_support: list[float] = []
        contradiction_scores: list[float] = []
        for offset in range(0, len(row_pairs), chunk_count):
            sentence_pairs = row_pairs[offset : offset + chunk_count]
            entailment_support.append(max(pair[0] for pair in sentence_pairs))
            contradiction_scores.append(max(pair[1] for pair in sentence_pairs))
        support = sum(entailment_support) / max(len(entailment_support), 1)
        contradiction_penalty = sum(contradiction_scores) / max(len(contradiction_scores), 1)
        entity_features = score_entity_support(source, summary)
        score = bounded(
            (0.70 * support)
            + (0.20 * entity_features["entity_support_score"])
            - (0.30 * contradiction_penalty)
        )
        records.append(
            {
                "id": example_id,
                "candidate_hash": candidate_hash,
                "summac_style_support": round(support, 6),
                "summac_style_contradiction_penalty": round(contradiction_penalty, 6),
                "summac_style_score": round(score, 6),
            }
        )
    return pd.DataFrame.from_records(records)
