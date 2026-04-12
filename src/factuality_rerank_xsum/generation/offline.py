from __future__ import annotations

from collections.abc import Iterable

from factuality_rerank_xsum.utils.text import (
    compress_to_tokens,
    extract_quote,
    first_clause,
    flip_polarity,
    hash_text,
    mutate_first_number,
    normalize_whitespace,
    split_sentences,
    stable_float_from_text,
    summarize_length_bias,
    swap_first_entity,
    token_ids_from_text,
)

ENTITY_BANK = [
    "Cardiff",
    "London",
    "Scotland",
    "Australia",
    "England",
    "Wales",
    "Fifa",
    "The Queen",
    "Leeds Rhinos",
    "Prime Minister",
]

RELATION_SWAP_PAIRS = [
    ("confirmed", "denied"),
    ("warned", "praised"),
    ("won", "lost"),
    ("charged", "cleared"),
    ("killed", "injured"),
    ("agreed", "rejected"),
    ("announced", "cancelled"),
]


def _relation_swap(text: str) -> str:
    lowered = text.lower()
    for source, target in RELATION_SWAP_PAIRS:
        if source in lowered:
            return text.replace(source, target, 1).replace(source.title(), target.title(), 1)
    return (
        text.replace(" has ", " has denied ", 1)
        if " has " in text
        else f"{text} despite officials denying it."
    )


def _location_swap(text: str, example_id: str) -> str:
    replacement = ENTITY_BANK[int(example_id[-1]) % len(ENTITY_BANK)]
    return swap_first_entity(text, replacement)


def _with_context(text: str) -> str:
    cleaned = normalize_whitespace(text)
    if cleaned.endswith("."):
        cleaned = cleaned[:-1]
    return f"{cleaned}, officials said."


def _quote_headline(text: str) -> str:
    quote = extract_quote(text)
    if quote:
        return f'"{quote}" at centre of report.'
    return compress_to_tokens(text, 12)


def _title_case_headline(text: str) -> str:
    candidate = compress_to_tokens(first_clause(text), 12)
    return candidate[:1].upper() + candidate[1:] if candidate else candidate


def _strategy_priors(example_id: str) -> dict[str, float]:
    corruption_slot = int(example_id[-1]) % 4
    priors = {
        "headline_12": 0.96,
        "headline_16": 0.93,
        "lead_sentence": 0.87,
        "lead_24": 0.82,
        "lead_clause": 0.84,
        "second_sentence": 0.66,
        "first_two_28": 0.61,
        "quote_headline": 0.78,
        "entity_swap": 0.72,
        "number_swap": 0.72,
        "polarity_flip": 0.70,
        "relation_swap": 0.71,
        "location_swap": 0.68,
        "with_context": 0.76,
        "very_short": 0.91,
        "longer_blend": 0.58,
    }
    corruption_names = ["entity_swap", "number_swap", "polarity_flip", "relation_swap"]
    priors[corruption_names[corruption_slot]] += 0.26
    return priors


def build_candidate_pool(example_id: str, document: str) -> list[tuple[str, str, float]]:
    sentences = split_sentences(document)
    lead = sentences[0] if sentences else document
    second = sentences[1] if len(sentences) > 1 else lead
    blend = f"{lead} {second}".strip()

    pool = {
        "headline_12": compress_to_tokens(lead, 12),
        "headline_16": compress_to_tokens(lead, 16),
        "lead_sentence": normalize_whitespace(lead),
        "lead_24": compress_to_tokens(lead, 24),
        "lead_clause": first_clause(lead),
        "second_sentence": compress_to_tokens(second, 18),
        "first_two_28": compress_to_tokens(blend, 28),
        "quote_headline": _quote_headline(lead),
        "entity_swap": swap_first_entity(
            lead, ENTITY_BANK[int(example_id[-2:]) % len(ENTITY_BANK)]
        ),
        "number_swap": mutate_first_number(lead, example_id),
        "polarity_flip": flip_polarity(lead),
        "relation_swap": _relation_swap(lead),
        "location_swap": _location_swap(lead, example_id),
        "with_context": _with_context(compress_to_tokens(lead, 18)),
        "very_short": compress_to_tokens(first_clause(lead), 9),
        "longer_blend": compress_to_tokens(f"{lead} {second}", 34),
    }
    priors = _strategy_priors(example_id)
    candidates: list[tuple[str, str, float]] = []
    seen: set[str] = set()
    for strategy, text in pool.items():
        cleaned = normalize_whitespace(text)
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        candidates.append((strategy, cleaned, priors[strategy]))
    candidates.sort(key=lambda item: item[2], reverse=True)
    return candidates


def generate_offline_candidates(
    *,
    example_id: str,
    split: str,
    document: str,
    reference: str,
    num_beams: int,
    length_penalty: float,
    no_repeat_ngram_size: int,
    max_new_tokens: int,
    min_new_tokens: int,
) -> list[dict[str, object]]:
    candidate_pool = build_candidate_pool(example_id, document)
    selected = candidate_pool[:num_beams]
    rows: list[dict[str, object]] = []
    for rank, (strategy, summary, prior) in enumerate(selected):
        token_ids = token_ids_from_text(summary)
        token_count = max(len(token_ids), 1)
        avg_logprob = -1.9 + prior + (summarize_length_bias(summary) * 0.25)
        sequence_score = avg_logprob * (token_count / (token_count**length_penalty))
        rows.append(
            {
                "id": example_id,
                "split": split,
                "document": document,
                "reference": reference,
                "candidate_id": rank,
                "beam_rank": rank,
                "summary": summary,
                "summary_token_ids": token_ids,
                "summary_len_tokens": token_count,
                "sequence_score_hf": round(sequence_score, 6),
                "token_logprob_sum": round(avg_logprob * token_count, 6),
                "token_logprob_avg": round(avg_logprob, 6),
                "num_beams": num_beams,
                "length_penalty": length_penalty,
                "no_repeat_ngram_size": no_repeat_ngram_size,
                "max_new_tokens": max_new_tokens,
                "min_new_tokens": min_new_tokens,
                "candidate_hash": hash_text(summary),
                "candidate_strategy": strategy,
                "transition_score_proxy": [round(avg_logprob, 6)] * token_count,
                "offline_generator_noise": round(stable_float_from_text(example_id + strategy), 6),
            }
        )
    return rows


def generate_for_examples(
    rows: Iterable[dict[str, str]],
    *,
    split: str,
    num_beams: int,
    length_penalty: float,
    no_repeat_ngram_size: int,
    max_new_tokens: int,
    min_new_tokens: int,
) -> list[dict[str, object]]:
    generated: list[dict[str, object]] = []
    for row in rows:
        generated.extend(
            generate_offline_candidates(
                example_id=row["id"],
                split=split,
                document=row["document"],
                reference=row["summary"],
                num_beams=num_beams,
                length_penalty=length_penalty,
                no_repeat_ngram_size=no_repeat_ngram_size,
                max_new_tokens=max_new_tokens,
                min_new_tokens=min_new_tokens,
            )
        )
    return generated
