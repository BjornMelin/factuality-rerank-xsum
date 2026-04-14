"""Compute FactCC-style factuality scores for summaries."""

from __future__ import annotations

import re
from typing import Any, TypedDict

import pandas as pd
import torch

from factuality_rerank_xsum.scorers.entity_support import score_entity_support
from factuality_rerank_xsum.utils.io import read_yaml
from factuality_rerank_xsum.utils.paths import config_path
from factuality_rerank_xsum.utils.text import (
    bounded,
    content_tokens,
    lexical_precision,
    split_sentences,
)
from factuality_rerank_xsum.utils.transformers_runtime import (
    load_sequence_classifier_runtime,
    move_batch_to_device,
)

NEGATION_PATTERN = re.compile(r"\b(no|not|never|without|none)\b", re.IGNORECASE)
HEURISTIC_MODE = "heuristic_factcc_style_fallback"
HF_MODE = "huggingface_text_classification"


class FactCCStyleScore(TypedDict):
    """FactCC-style scoring features for one summary.

    Parameters:
        factcc_style_lexical_support: Legacy compatibility field for the
            primary support signal, populated by lexical precision in
            heuristic mode and model probability in Hugging Face mode.
        factcc_style_negation_mismatch: Penalty term for negation conflicts.
        factcc_style_relation_penalty: Penalty term for relation inversions.
        factcc_style_score: Final FactCC-style factuality score.
    """

    factcc_style_lexical_support: float
    factcc_style_negation_mismatch: float
    factcc_style_relation_penalty: float
    factcc_style_score: float


def _factcc_config() -> dict[str, Any]:
    return read_yaml(config_path("model", "factcc_hf.yaml"))


def _validated_mode(config: dict[str, Any]) -> str:
    mode = str(config.get("mode", ""))
    if mode in {HEURISTIC_MODE, HF_MODE}:
        return mode
    msg = f"Unsupported FactCC mode: {mode}"
    raise ValueError(msg)


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


def _source_excerpt(source: str, sentence_limit: int) -> str:
    sentences = split_sentences(source)
    if not sentences:
        return source
    return " ".join(sentences[:sentence_limit])


def _heuristic_score(source: str, summary: str) -> FactCCStyleScore:
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


def _label_id(label_map: dict[str, int], target: str) -> int:
    normalized = {key.lower(): value for key, value in label_map.items()}
    if target.lower() not in normalized:
        msg = f"Missing label {target!r} in model labels: {sorted(label_map)}"
        raise KeyError(msg)
    return normalized[target.lower()]


def _factcc_probabilities(
    sources: list[str],
    summaries: list[str],
    *,
    config: dict[str, Any],
) -> list[tuple[float, float]]:
    tokenizer, model, device = load_sequence_classifier_runtime(
        str(config["model_name_or_path"]),
        str(config.get("revision") or "") or None,
        str(config.get("device", "auto")),
    )
    label_map = {str(value): int(key) for key, value in model.config.id2label.items()}
    correct_id = _label_id(label_map, "CORRECT")
    incorrect_id = _label_id(label_map, "INCORRECT")
    batch_size = int(config.get("batch_size", 8))
    max_length = int(config.get("max_length", 512))
    probabilities: list[tuple[float, float]] = []
    for start in range(0, len(sources), batch_size):
        batch_sources = sources[start : start + batch_size]
        batch_summaries = summaries[start : start + batch_size]
        encoded = tokenizer(
            batch_sources,
            batch_summaries,
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
            probabilities.append((float(row[correct_id].item()), float(row[incorrect_id].item())))
    return probabilities


def _score_from_probability(
    *,
    correct_probability: float,
    source: str,
    summary: str,
) -> FactCCStyleScore:
    support_features = score_entity_support(source, summary)
    negation = _negation_mismatch(source, summary)
    relation = _relation_penalty(source, summary)
    score = bounded(
        (0.85 * correct_probability)
        + (0.15 * support_features["entity_support_score"])
        - (0.10 * negation)
        - (0.10 * relation)
    )
    return {
        "factcc_style_lexical_support": round(correct_probability, 6),
        "factcc_style_negation_mismatch": round(negation, 6),
        "factcc_style_relation_penalty": round(relation, 6),
        "factcc_style_score": round(score, 6),
    }


def score_factcc_style(
    source: str,
    summary: str,
    *,
    config: dict[str, Any] | None = None,
) -> FactCCStyleScore:
    """Score a summary with the configured FactCC-style scorer.

    Args:
        source: Source document text.
        summary: Candidate summary text.
        config: Optional scorer configuration override.

    Returns:
        FactCC-style feature scores and the combined factuality score.
    """

    active_config = config or _factcc_config()
    mode = _validated_mode(active_config)
    if mode == HEURISTIC_MODE:
        return _heuristic_score(source, summary)
    probability = _factcc_probabilities(
        [_source_excerpt(source, int(active_config.get("source_sentence_limit", 8)))],
        [summary],
        config=active_config,
    )[0][0]
    return _score_from_probability(correct_probability=probability, source=source, summary=summary)


def score_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    """Score every row in a dataframe with the FactCC-style scorer.

    Args:
        frame: Rows containing document, summary, and candidate identifiers.

    Returns:
        A dataframe with FactCC-style feature columns for each candidate.
    """

    config = _factcc_config()
    mode = _validated_mode(config)
    if mode == HEURISTIC_MODE:
        records = []
        for row in frame.itertuples(index=False):
            records.append(
                {
                    "id": row.id,
                    "candidate_id": row.candidate_id,
                    "candidate_hash": row.candidate_hash,
                    **_heuristic_score(str(row.document), str(row.summary)),
                }
            )
        return pd.DataFrame.from_records(records)

    sources = [
        _source_excerpt(str(row.document), int(config.get("source_sentence_limit", 8)))
        for row in frame.itertuples(index=False)
    ]
    summaries = [str(row.summary) for row in frame.itertuples(index=False)]
    probabilities = _factcc_probabilities(sources, summaries, config=config)
    records = []
    for index, row in enumerate(frame.itertuples(index=False)):
        records.append(
            {
                "id": row.id,
                "candidate_id": row.candidate_id,
                "candidate_hash": row.candidate_hash,
                **_score_from_probability(
                    correct_probability=probabilities[index][0],
                    source=str(row.document),
                    summary=str(row.summary),
                ),
            }
        )
    return pd.DataFrame.from_records(records)
