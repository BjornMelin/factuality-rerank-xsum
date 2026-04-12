"""Candidate-generation stage orchestration."""

from __future__ import annotations

from typing import Any

import pandas as pd

from factuality_rerank_xsum.artifacts.layout import candidate_table_path
from factuality_rerank_xsum.constants import PIPELINE_SPLITS
from factuality_rerank_xsum.data.fixtures import ids_for_split, load_dataset_table
from factuality_rerank_xsum.generation.offline import generate_candidates_for_examples
from factuality_rerank_xsum.utils.io import read_yaml, write_json
from factuality_rerank_xsum.utils.paths import artifact_path, config_path


def config_beams() -> list[dict[str, Any]]:
    """Load the configured beam search variants.

    Returns:
        The beam-search parameter sets from the generate configs.
    """

    return [
        read_yaml(config_path("generate", name))
        for name in ["beams_4.yaml", "beams_8.yaml", "beams_16.yaml"]
    ]


def example_rows(split: str) -> list[dict[str, str]]:
    """Load normalized example rows for one split.

    Args:
        split: Pipeline split name.

    Returns:
        The normalized example rows for the requested split.
    """

    frame = load_dataset_table()
    rows = frame[frame["id"].isin(ids_for_split(split))].copy()
    rows = rows.sort_values("id").reset_index(drop=True)
    return [
        {"id": str(row.id), "document": str(row.document), "summary": str(row.summary)}
        for row in rows.itertuples(index=False)
    ]


def generation_integrity_report(frame: pd.DataFrame, requested_ids: list[str]) -> dict[str, Any]:
    """Summarize candidate generation coverage for one split and beam.

    Args:
        frame: Generated candidate rows for one split and beam size.
        requested_ids: Example IDs that were requested for generation.

    Returns:
        A coverage and integrity summary for the generated frame.
    """

    if frame.empty:
        return {
            "requested_ids": len(requested_ids),
            "observed_ids": 0,
            "missing_ids": sorted(set(requested_ids)),
            "rows": 0,
            "min_candidates_per_example": 0,
            "max_candidates_per_example": 0,
            "non_empty_summaries": False,
            "has_nan_scores": False,
        }
    grouped = frame.groupby("id", as_index=False).size()
    observed_ids = set(frame["id"].astype(str))
    return {
        "requested_ids": len(requested_ids),
        "observed_ids": int(grouped["id"].nunique()),
        "missing_ids": sorted(set(requested_ids) - observed_ids),
        "rows": len(frame),
        "min_candidates_per_example": int(grouped["size"].min()),
        "max_candidates_per_example": int(grouped["size"].max()),
        "non_empty_summaries": bool(
            frame["summary"].notna().all() and frame["summary"].astype(str).str.len().gt(0).all()
        ),
        "has_nan_scores": bool(
            frame[["sequence_score_hf", "token_logprob_sum", "token_logprob_avg"]]
            .isna()
            .any()
            .any()
        ),
    }


def run_generate_candidates() -> dict[str, Any]:
    """Generate candidate summaries for every configured split and beam size.

    Returns:
        The generation summary payload written to tracked artifacts.
    """

    beams = config_beams()
    generation_config = read_yaml(config_path("model", "bart_xsum_public.yaml"))
    summary: dict[str, Any] = {
        "splits": {},
        "beam_sizes": [beam["num_beams"] for beam in beams],
        "generator_mode": generation_config.get("mode", "huggingface_generation"),
        "generator_model": generation_config["model_name_or_path"],
        "generator_revision": generation_config.get("revision"),
    }
    for split in PIPELINE_SPLITS:
        split_rows = example_rows(split)
        summary["splits"][split] = {"examples": len(split_rows)}
        requested_ids = [row["id"] for row in split_rows]
        for beam in beams:
            generated = generate_candidates_for_examples(
                split_rows,
                split=split,
                num_beams=int(beam["num_beams"]),
                length_penalty=float(beam["length_penalty"]),
                no_repeat_ngram_size=int(beam["no_repeat_ngram_size"]),
                max_new_tokens=int(beam["max_new_tokens"]),
                min_new_tokens=int(beam["min_new_tokens"]),
                config=generation_config,
            )
            frame = pd.DataFrame(generated)
            target = candidate_table_path(split, int(beam["num_beams"]))
            target.parent.mkdir(parents=True, exist_ok=True)
            frame.to_parquet(target, index=False)
            frame.to_csv(target.with_suffix(".csv"), index=False)
            write_json(
                target.parent / "integrity_report.json",
                generation_integrity_report(frame, requested_ids),
            )
    write_json(artifact_path("generations", "generation_summary.json"), summary)
    return summary
