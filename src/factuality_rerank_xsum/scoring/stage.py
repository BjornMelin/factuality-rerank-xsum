"""Scoring stage orchestration for candidate tables."""

from __future__ import annotations

import pandas as pd

from factuality_rerank_xsum.artifacts.layout import (
    candidate_table_path,
    merged_table_path,
    score_table_path,
)
from factuality_rerank_xsum.constants import BEAM_SIZES, PIPELINE_SPLITS
from factuality_rerank_xsum.scorers.entity_support import score_dataframe as entity_score_dataframe
from factuality_rerank_xsum.scorers.factcc_style import score_dataframe as factcc_score_dataframe
from factuality_rerank_xsum.scorers.summac_style import score_dataframe as summac_score_dataframe
from factuality_rerank_xsum.utils.io import write_text
from factuality_rerank_xsum.utils.paths import artifact_path


def run_score_stage(stage: str) -> None:
    """Run one scorer over every generated candidate table."""

    for split in PIPELINE_SPLITS:
        for beam in BEAM_SIZES:
            frame = pd.read_parquet(candidate_table_path(split, beam))
            if stage == "summac":
                scored = summac_score_dataframe(frame)
            elif stage == "factcc":
                scored = factcc_score_dataframe(frame)
            elif stage == "entity_support":
                scored = entity_score_dataframe(frame)
            else:
                msg = f"Unsupported score stage: {stage}"
                raise ValueError(msg)
            target = score_table_path(stage, split, beam)
            target.parent.mkdir(parents=True, exist_ok=True)
            scored.to_parquet(target, index=False)
            scored.to_csv(target.with_suffix(".csv"), index=False)


def run_score_candidates_summac() -> None:
    """Run the NLI-consistency scorer across all candidate tables."""

    run_score_stage("summac")


def run_score_candidates_factcc() -> None:
    """Run the FactCC-style scorer across all candidate tables."""

    run_score_stage("factcc")


def run_score_candidates_entity_support() -> None:
    """Run the entity-support scorer across all candidate tables."""

    run_score_stage("entity_support")


def run_optional_minicheck_placeholder() -> None:
    """Record that the optional MiniCheck stage was intentionally skipped."""

    write_text(
        artifact_path("scores", "minicheck", "NOT_RUN.md"),
        "# MiniCheck optional stage not executed\n\nThe executed run stayed on the required path.\n",
    )


def run_merge_candidate_scores() -> None:
    """Merge per-stage scorer outputs into one table per split and beam size."""

    for split in PIPELINE_SPLITS:
        for beam in BEAM_SIZES:
            base = pd.read_parquet(candidate_table_path(split, beam))
            summac = pd.read_parquet(score_table_path("summac", split, beam))
            factcc = pd.read_parquet(score_table_path("factcc", split, beam))
            entity = pd.read_parquet(score_table_path("entity_support", split, beam))
            merged = (
                base.merge(summac, on=["id", "candidate_hash"])
                .merge(factcc, on=["id", "candidate_hash"])
                .merge(entity, on=["id", "candidate_hash"])
            )
            target = merged_table_path(split, beam)
            target.parent.mkdir(parents=True, exist_ok=True)
            merged.to_parquet(target, index=False)
            merged.to_csv(target.with_suffix(".csv"), index=False)
