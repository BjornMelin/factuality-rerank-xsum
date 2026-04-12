"""Provide text normalization and lightweight heuristic text features."""

from __future__ import annotations

import hashlib
import math
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "but",
    "by",
    "for",
    "from",
    "had",
    "has",
    "have",
    "he",
    "her",
    "his",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "said",
    "she",
    "that",
    "the",
    "their",
    "there",
    "they",
    "this",
    "to",
    "was",
    "were",
    "will",
    "with",
}

MONTH_WORDS = {
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
}

ENTITY_PATTERN = re.compile(r"(?:[A-Z][\w'\u2019.-]*)(?:\s+(?:[A-Z][\w'\u2019.-]*))*")
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9£€$%][A-Za-z0-9£€$%.'\u2019/-]*")
NUMBER_PATTERN = re.compile(r"(?:£|\$|€)?\d[\d,./]*(?:%|bn|m|k|st|nd|rd|th)?", re.IGNORECASE)
QUOTE_PATTERN = re.compile(r'"([^"]+)"')
SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")


def normalize_whitespace(text: str) -> str:
    """Collapse repeated whitespace and trim surrounding spaces.

    Args:
        text: Raw text input.

    Returns:
        The whitespace-normalized text.
    """

    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> list[str]:
    """Split free text into lightly normalized sentence-like segments.

    Args:
        text: Raw text input.

    Returns:
        Sentence-like segments extracted from the text.
    """

    cleaned = normalize_whitespace(text)
    if not cleaned:
        return []
    parts = [part.strip() for part in SPLIT_PATTERN.split(cleaned) if part.strip()]
    return parts if parts else [cleaned]


def tokenize(text: str) -> list[str]:
    """Extract regex-based tokens from free text.

    Args:
        text: Raw text input.

    Returns:
        Regex-tokenized text spans.
    """

    return TOKEN_PATTERN.findall(text)


def lowercase_tokens(text: str) -> list[str]:
    """Return lowercase tokens for the given text.

    Args:
        text: Raw text input.

    Returns:
        Lowercased tokens extracted from the text.
    """

    return [token.lower() for token in tokenize(text)]


def content_tokens(text: str) -> list[str]:
    """Return lowercase tokens with common stopwords removed.

    Args:
        text: Raw text input.

    Returns:
        Lowercased non-stopword tokens extracted from the text.
    """

    return [token for token in lowercase_tokens(text) if token not in STOPWORDS]


def extract_numbers(text: str) -> list[str]:
    """Extract number-like spans from text.

    Args:
        text: Raw text input.

    Returns:
        Number-like spans extracted from the text.
    """

    return NUMBER_PATTERN.findall(text)


def extract_dates(text: str) -> list[str]:
    """Extract lightweight date cues such as months and 4-digit years.

    Args:
        text: Raw text input.

    Returns:
        Extracted month and year tokens.
    """

    lowered = lowercase_tokens(text)
    dates = [token for token in lowered if token in MONTH_WORDS]
    dates.extend([token for token in lowered if token.isdigit() and len(token) == 4])
    return dates


def extract_entities(text: str) -> list[str]:
    """Extract simple capitalized entity spans from text.

    Args:
        text: Raw text input.

    Returns:
        Extracted capitalized entity spans.
    """

    entities: list[str] = []
    for match in ENTITY_PATTERN.finditer(text):
        value = normalize_whitespace(match.group(0))
        if not value:
            continue
        if value.lower() in MONTH_WORDS:
            continue
        if value.isupper() and len(value) == 1:
            continue
        entities.append(value)
    return entities


def hash_text(text: str) -> str:
    """Return a short stable hash for text.

    Args:
        text: Raw text input.

    Returns:
        A short stable hexadecimal hash prefix.
    """

    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def compress_to_tokens(text: str, max_tokens: int) -> str:
    """Truncate text to a token budget while preserving readability.

    Args:
        text: Raw text input.
        max_tokens: Maximum token count to preserve.

    Returns:
        The text truncated to the requested token budget.
    """

    tokens = tokenize(text)
    if len(tokens) <= max_tokens:
        return normalize_whitespace(text)
    compressed = " ".join(tokens[:max_tokens]).rstrip(",;:")
    if compressed and compressed[-1] not in ".!?":
        compressed += "."
    return compressed


def first_clause(text: str) -> str:
    """Return the first clause-like segment from a sentence.

    Args:
        text: Raw text input.

    Returns:
        The first clause-like segment from the text.
    """

    cleaned = normalize_whitespace(text)
    for separator in [",", " but ", " after ", " as ", " while ", " although ", " because "]:
        if separator in cleaned:
            piece = cleaned.split(separator, maxsplit=1)[0]
            if piece:
                return piece.rstrip(",;:") + "."
    return cleaned


def extract_quote(text: str) -> str | None:
    """Extract the first quoted span from text, if present.

    Args:
        text: Raw text input.

    Returns:
        The first quoted span, or `None` when absent.
    """

    match = QUOTE_PATTERN.search(text)
    if not match:
        return None
    value = normalize_whitespace(match.group(1))
    return value if value else None


def mutate_first_number(text: str, example_id: str) -> str:
    """Deterministically perturb the first numeric token in text.

    Args:
        text: Raw text input.
        example_id: Example identifier used to derive a deterministic perturbation.

    Returns:
        The text with its first numeric token mutated when one is present.
    """

    match = NUMBER_PATTERN.search(text)
    if not match:
        return text
    token = match.group(0)
    digits = re.sub(r"[^\d]", "", token)
    if not digits:
        return text
    value = int(digits)
    delta = (int(example_id[-1]) % 4) + 1
    mutated = str(value + delta)
    replacement = token.replace(digits, mutated, 1)
    return text.replace(token, replacement, 1)


def swap_first_entity(text: str, replacement: str) -> str:
    """Replace the first extracted entity span with a new value.

    Args:
        text: Raw text input.
        replacement: Replacement entity text.

    Returns:
        The text with its first entity span replaced when possible.
    """

    match = ENTITY_PATTERN.search(text)
    if not match:
        return text
    original = match.group(0)
    if normalize_whitespace(original) == replacement:
        return text
    return text.replace(original, replacement, 1)


def flip_polarity(text: str) -> str:
    """Flip a small set of polarity and outcome phrases in text.

    Args:
        text: Raw text input.

    Returns:
        The text with a polarity cue or outcome phrase inverted.
    """

    cleaned = normalize_whitespace(text)
    replacements = [
        (" has ", " has not "),
        (" have ", " have not "),
        (" was ", " was not "),
        (" were ", " were not "),
        (" will ", " will not "),
        (" can ", " cannot "),
        (" won ", " lost "),
        (" confirmed ", " denied "),
        (" approved ", " rejected "),
        (" agreed ", " opposed "),
    ]
    lowered = f" {cleaned} "
    for source, target in replacements:
        if source in lowered.lower():
            pattern = re.compile(re.escape(source.strip()), re.IGNORECASE)
            return pattern.sub(target.strip(), cleaned, count=1)
    if " not " in lowered.lower():
        return re.sub(r"\bnot\b\s*", "", cleaned, count=1, flags=re.IGNORECASE)
    return cleaned.replace(" is ", " is not ", 1) if " is " in cleaned else f"Not {cleaned}"


def lexical_precision(reference: Iterable[str], prediction: Iterable[str]) -> float:
    """Compute token-level precision of `prediction` against `reference`.

    Args:
        reference: Reference token sequence.
        prediction: Predicted token sequence.

    Returns:
        Token-level precision.
    """

    reference_set = set(reference)
    prediction_list = list(prediction)
    if not prediction_list:
        return 0.0
    supported = sum(1 for token in prediction_list if token in reference_set)
    return supported / len(prediction_list)


def lexical_recall(reference: Iterable[str], prediction: Iterable[str]) -> float:
    """Compute token-level recall of `prediction` against `reference`.

    Args:
        reference: Reference token sequence.
        prediction: Predicted token sequence.

    Returns:
        Token-level recall.
    """

    reference_list = list(reference)
    prediction_set = set(prediction)
    if not reference_list:
        return 0.0
    supported = sum(1 for token in reference_list if token in prediction_set)
    return supported / len(reference_list)


def f1(precision: float, recall: float) -> float:
    """Compute the F1 score for a precision/recall pair.

    Args:
        precision: Precision value.
        recall: Recall value.

    Returns:
        The harmonic mean of precision and recall.
    """

    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def harmonic_mean(values: Iterable[float]) -> float:
    """Compute the harmonic mean of positive values.

    Args:
        values: Positive numeric values.

    Returns:
        The harmonic mean of the positive inputs, or `0.0` when none exist.
    """

    filtered = [value for value in values if value > 0]
    if not filtered:
        return 0.0
    return len(filtered) / sum(1 / value for value in filtered)


def bounded(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    """Clamp a value to the inclusive `[minimum, maximum]` interval.

    Args:
        value: Input value.
        minimum: Inclusive lower bound.
        maximum: Inclusive upper bound.

    Returns:
        The clamped value.
    """

    return max(minimum, min(maximum, value))


def stable_float_from_text(text: str) -> float:
    """Map text to a stable pseudo-random float in `[0, 1)`.

    Args:
        text: Raw text input.

    Returns:
        A stable pseudo-random float derived from the text.
    """

    digest = int(hash_text(text), 16)
    return (digest % 10_000) / 10_000.0


def token_ids_from_text(text: str) -> list[int]:
    """Map tokens to stable integer identifiers.

    Args:
        text: Raw text input.

    Returns:
        Stable integer identifiers derived from the text tokens.
    """

    return [
        int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16) % 50_257
        for token in tokenize(text)
    ]


def summarize_length_bias(text: str, target_tokens: int = 16) -> float:
    """Score how closely text length matches a target token count.

    Args:
        text: Raw text input.
        target_tokens: Desired token count.

    Returns:
        A smooth score rewarding lengths near the target.
    """

    length = max(len(tokenize(text)), 1)
    delta = abs(length - target_tokens)
    return math.exp(-delta / max(target_tokens, 1))
