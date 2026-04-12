from __future__ import annotations

import hashlib
import math
import re
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

ENTITY_PATTERN = re.compile(r"(?:[A-Z][\w'’.-]*)(?:\s+(?:[A-Z][\w'’.-]*))*")
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9£€$%][A-Za-z0-9£€$%.'’/-]*")
NUMBER_PATTERN = re.compile(r"(?:£|\$|€)?\d[\d,./]*(?:%|bn|m|k|st|nd|rd|th)?", re.IGNORECASE)
QUOTE_PATTERN = re.compile(r'"([^"]+)"')
SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> list[str]:
    cleaned = normalize_whitespace(text)
    if not cleaned:
        return []
    parts = [part.strip() for part in SPLIT_PATTERN.split(cleaned) if part.strip()]
    return parts if parts else [cleaned]


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text)


def lowercase_tokens(text: str) -> list[str]:
    return [token.lower() for token in tokenize(text)]


def content_tokens(text: str) -> list[str]:
    return [token for token in lowercase_tokens(text) if token not in STOPWORDS]


def extract_numbers(text: str) -> list[str]:
    return NUMBER_PATTERN.findall(text)


def extract_dates(text: str) -> list[str]:
    lowered = lowercase_tokens(text)
    dates = [token for token in lowered if token in MONTH_WORDS]
    dates.extend([token for token in lowered if token.isdigit() and len(token) == 4])
    return dates


def extract_entities(text: str) -> list[str]:
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
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def compress_to_tokens(text: str, max_tokens: int) -> str:
    tokens = tokenize(text)
    if len(tokens) <= max_tokens:
        return normalize_whitespace(text)
    compressed = " ".join(tokens[:max_tokens]).rstrip(",;:")
    if compressed and compressed[-1] not in ".!?":
        compressed += "."
    return compressed


def first_clause(text: str) -> str:
    cleaned = normalize_whitespace(text)
    for separator in [",", " but ", " after ", " as ", " while ", " although ", " because "]:
        if separator in cleaned:
            piece = cleaned.split(separator, maxsplit=1)[0]
            if piece:
                return piece.rstrip(",;:") + "."
    return cleaned


def extract_quote(text: str) -> str | None:
    match = QUOTE_PATTERN.search(text)
    if not match:
        return None
    value = normalize_whitespace(match.group(1))
    return value if value else None


def mutate_first_number(text: str, example_id: str) -> str:
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
    match = ENTITY_PATTERN.search(text)
    if not match:
        return text
    original = match.group(0)
    if normalize_whitespace(original) == replacement:
        return text
    return text.replace(original, replacement, 1)


def flip_polarity(text: str) -> str:
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
    reference_set = set(reference)
    prediction_list = list(prediction)
    if not prediction_list:
        return 0.0
    supported = sum(1 for token in prediction_list if token in reference_set)
    return supported / len(prediction_list)


def lexical_recall(reference: Iterable[str], prediction: Iterable[str]) -> float:
    reference_list = list(reference)
    prediction_set = set(prediction)
    if not reference_list:
        return 0.0
    supported = sum(1 for token in reference_list if token in prediction_set)
    return supported / len(reference_list)


def f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def harmonic_mean(values: Iterable[float]) -> float:
    filtered = [value for value in values if value > 0]
    if not filtered:
        return 0.0
    return len(filtered) / sum(1 / value for value in filtered)


def bounded(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def stable_float_from_text(text: str) -> float:
    digest = int(hash_text(text), 16)
    return (digest % 10_000) / 10_000.0


def token_ids_from_text(text: str) -> list[int]:
    return [
        int(hashlib.sha1(token.encode("utf-8")).hexdigest(), 16) % 50_257
        for token in tokenize(text)
    ]


def summarize_length_bias(text: str, target_tokens: int = 16) -> float:
    length = max(len(tokenize(text)), 1)
    delta = abs(length - target_tokens)
    return math.exp(-delta / max(target_tokens, 1))
