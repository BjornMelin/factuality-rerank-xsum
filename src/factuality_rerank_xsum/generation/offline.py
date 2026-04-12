from __future__ import annotations

from typing import TYPE_CHECKING, Any

from factuality_rerank_xsum.utils.io import read_yaml
from factuality_rerank_xsum.utils.paths import config_path
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
from factuality_rerank_xsum.utils.transformers_runtime import (
    load_seq2seq_runtime,
    move_batch_to_device,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

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


def _generation_config() -> dict[str, Any]:
    return read_yaml(config_path("model", "bart_xsum_public.yaml"))


def _requested_revision(config: dict[str, Any]) -> str | None:
    value = str(config.get("revision") or "")
    return value or None


def _sequence_scores(
    token_scores: list[float],
    *,
    sequence_score_hf: float | None,
    token_count: int,
    length_penalty: float,
) -> tuple[float, float]:
    if token_scores:
        token_logprob_sum = float(sum(token_scores))
        token_logprob_avg = token_logprob_sum / max(token_count, 1)
        return token_logprob_sum, token_logprob_avg
    if sequence_score_hf is None:
        return 0.0, 0.0
    approx_sum = float(sequence_score_hf) * (max(token_count, 1) ** length_penalty)
    return approx_sum, approx_sum / max(token_count, 1)


def _runtime_rows_from_outputs(
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
    model_name_or_path: str,
    revision: str | None,
    tokenizer: Any,
    model: Any,
    outputs: Any,
) -> list[dict[str, object]]:
    decoded_summaries = tokenizer.batch_decode(outputs.sequences, skip_special_tokens=True)
    beam_indices = getattr(outputs, "beam_indices", None)
    transition_tensor = None
    if getattr(outputs, "scores", None):
        transition_tensor = model.compute_transition_scores(
            outputs.sequences,
            outputs.scores,
            beam_indices,
            normalize_logits=True,
        )
    sequence_scores = getattr(outputs, "sequences_scores", None)
    pad_token_id = tokenizer.pad_token_id
    if pad_token_id is None:
        pad_token_id = tokenizer.eos_token_id if tokenizer.eos_token_id is not None else 0

    rows: list[dict[str, object]] = []
    for rank, summary in enumerate(decoded_summaries):
        cleaned_summary = normalize_whitespace(summary)
        summary_token_ids = tokenizer(
            cleaned_summary,
            add_special_tokens=False,
            truncation=False,
        )["input_ids"]
        token_count = max(len(summary_token_ids), 1)
        per_token_scores: list[float] = []
        if transition_tensor is not None:
            generated_length = int((outputs.sequences[rank] != pad_token_id).sum().item())
            trimmed = transition_tensor[rank][: max(generated_length - 1, 1)].tolist()
            per_token_scores = [float(score) for score in trimmed if float(score) <= 0.0]
        sequence_score_hf = None
        if sequence_scores is not None:
            sequence_score_hf = float(sequence_scores[rank].item())
        token_logprob_sum, token_logprob_avg = _sequence_scores(
            per_token_scores,
            sequence_score_hf=sequence_score_hf,
            token_count=token_count,
            length_penalty=length_penalty,
        )
        rows.append(
            {
                "id": example_id,
                "split": split,
                "document": document,
                "reference": reference,
                "candidate_id": rank,
                "beam_rank": rank,
                "summary": cleaned_summary,
                "summary_token_ids": summary_token_ids,
                "summary_len_tokens": token_count,
                "sequence_score_hf": round(sequence_score_hf or 0.0, 6),
                "token_logprob_sum": round(token_logprob_sum, 6),
                "token_logprob_avg": round(token_logprob_avg, 6),
                "num_beams": num_beams,
                "length_penalty": length_penalty,
                "no_repeat_ngram_size": no_repeat_ngram_size,
                "max_new_tokens": max_new_tokens,
                "min_new_tokens": min_new_tokens,
                "candidate_hash": hash_text(cleaned_summary),
                "candidate_strategy": f"hf_beam_{rank}",
                "transition_score_proxy": [round(float(score), 6) for score in per_token_scores],
                "generator_mode": "huggingface_generation",
                "requested_model": model_name_or_path,
                "requested_revision": revision or "",
            }
        )
    return rows


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
                "generator_mode": "offline_surrogate_generator",
                "requested_model": "offline_surrogate",
                "requested_revision": "",
            }
        )
    return rows


def generate_model_candidates(
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
    config: dict[str, Any] | None = None,
) -> list[dict[str, object]]:
    generation_config = config or _generation_config()
    mode = str(generation_config.get("mode", "huggingface_generation"))
    if mode == "offline_surrogate_generator":
        return generate_offline_candidates(
            example_id=example_id,
            split=split,
            document=document,
            reference=reference,
            num_beams=num_beams,
            length_penalty=length_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
            max_new_tokens=max_new_tokens,
            min_new_tokens=min_new_tokens,
        )

    import torch

    revision = _requested_revision(generation_config)
    tokenizer, model, device = load_seq2seq_runtime(
        str(generation_config["model_name_or_path"]),
        revision,
        str(generation_config.get("device", "auto")),
    )
    encoded = tokenizer(
        document,
        max_length=int(generation_config.get("max_source_length", 1024)),
        truncation=True,
        return_tensors="pt",
    )
    encoded = move_batch_to_device(encoded, device)
    with torch.inference_mode():
        outputs = model.generate(
            **encoded,
            num_beams=num_beams,
            num_return_sequences=num_beams,
            length_penalty=length_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
            max_new_tokens=max_new_tokens,
            min_new_tokens=min_new_tokens,
            early_stopping=True,
            output_scores=True,
            return_dict_in_generate=True,
        )
    return _runtime_rows_from_outputs(
        example_id=example_id,
        split=split,
        document=document,
        reference=reference,
        num_beams=num_beams,
        length_penalty=length_penalty,
        no_repeat_ngram_size=no_repeat_ngram_size,
        max_new_tokens=max_new_tokens,
        min_new_tokens=min_new_tokens,
        model_name_or_path=str(generation_config["model_name_or_path"]),
        revision=revision,
        tokenizer=tokenizer,
        model=model,
        outputs=outputs,
    )


def generate_candidates_for_examples(
    rows: Iterable[dict[str, str]],
    *,
    split: str,
    num_beams: int,
    length_penalty: float,
    no_repeat_ngram_size: int,
    max_new_tokens: int,
    min_new_tokens: int,
    config: dict[str, Any] | None = None,
) -> list[dict[str, object]]:
    """Generate candidates for a batch of examples.

    Args:
        rows: Normalized example rows.
        split: Pipeline split name.
        num_beams: Number of beam candidates to generate.
        length_penalty: Generation length-penalty setting.
        no_repeat_ngram_size: No-repeat n-gram constraint.
        max_new_tokens: Maximum generated token count.
        min_new_tokens: Minimum generated token count.
        config: Optional generator configuration override.

    Returns:
        The generated candidate rows for the provided examples.
    """

    generated: list[dict[str, object]] = []
    for row in rows:
        generated.extend(
            generate_model_candidates(
                example_id=row["id"],
                split=split,
                document=row["document"],
                reference=row["summary"],
                num_beams=num_beams,
                length_penalty=length_penalty,
                no_repeat_ngram_size=no_repeat_ngram_size,
                max_new_tokens=max_new_tokens,
                min_new_tokens=min_new_tokens,
                config=config,
            )
        )
    return generated
