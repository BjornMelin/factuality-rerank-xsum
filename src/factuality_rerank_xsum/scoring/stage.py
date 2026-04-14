"""Scoring stage orchestration for candidate tables."""

from __future__ import annotations

import json
import subprocess

import pandas as pd

from factuality_rerank_xsum.artifacts.layout import (
    candidate_table_path,
    merged_table_path,
    score_table_path,
)
from factuality_rerank_xsum.constants import BEAM_SIZES, PIPELINE_SPLITS
from factuality_rerank_xsum.scorers.entity_support import score_dataframe as entity_score_dataframe
from factuality_rerank_xsum.scorers.factcc_style import HF_MODE as FACTCC_HF_MODE
from factuality_rerank_xsum.scorers.factcc_style import score_dataframe as factcc_score_dataframe
from factuality_rerank_xsum.scorers.summac_style import HF_MODE as SUMMAC_HF_MODE
from factuality_rerank_xsum.scorers.summac_style import score_dataframe as summac_score_dataframe
from factuality_rerank_xsum.utils.io import read_yaml, write_json, write_text
from factuality_rerank_xsum.utils.paths import artifact_path, config_path, project_root

MERGE_KEYS = ["id", "candidate_id", "candidate_hash"]
SCORE_COLUMNS = {
    "summac": [
        "summac_style_support",
        "summac_style_contradiction_penalty",
        "summac_style_score",
    ],
    "factcc": [
        "factcc_style_lexical_support",
        "factcc_style_negation_mismatch",
        "factcc_style_relation_penalty",
        "factcc_style_score",
    ],
    "entity_support": [
        "entity_precision",
        "number_precision",
        "date_precision",
        "entity_support_score",
        "unsupported_entity_count",
        "unsupported_number_count",
        "unsupported_date_count",
        "unsupported_entities",
        "unsupported_numbers",
        "unsupported_dates",
    ],
}


def _executed_stage_mode(stage: str) -> str:
    """Return the configured executed mode for one scorer stage."""

    if stage == "factcc":
        config = read_yaml(config_path("model", "factcc_hf.yaml"))
        return str(config.get("mode", FACTCC_HF_MODE))
    if stage == "summac":
        config = read_yaml(config_path("score", "summac.yaml"))
        return str(config.get("mode", SUMMAC_HF_MODE))
    if stage == "entity_support":
        return "entity_support_heuristic"
    msg = f"Unsupported score stage: {stage}"
    raise ValueError(msg)


def _merge_scores(base: pd.DataFrame, scores: pd.DataFrame, *, stage: str) -> pd.DataFrame:
    """Merge one scorer output into the candidate table with integrity checks.

    Args:
        base: Candidate rows accumulated so far.
        scores: Score rows for one scoring stage.
        stage: Stage name used for error reporting.

    Returns:
        The merged candidate and score dataframe.

    Raises:
        ValueError: If the merge changes row count or leaves missing score values.
    """

    merged = base.merge(scores, on=MERGE_KEYS, how="left", validate="one_to_one")
    if len(merged) != len(base):
        msg = f"Row-count mismatch after merging {stage}: base={len(base)} merged={len(merged)}"
        raise ValueError(msg)
    added_columns = [column for column in scores.columns if column not in MERGE_KEYS]
    if added_columns and merged[added_columns].isna().any().any():
        msg = f"Missing {stage} scores after merge for keys {MERGE_KEYS}"
        raise ValueError(msg)
    return merged


def run_score_stage(stage: str) -> None:
    """Run one scorer over every generated candidate table.

    Args:
        stage: Scoring stage name.

    Raises:
        ValueError: If the requested stage name is unsupported.
    """

    if stage not in SCORE_COLUMNS:
        msg = f"Unsupported score stage: {stage}"
        raise ValueError(msg)
    for split in PIPELINE_SPLITS:
        for beam in BEAM_SIZES:
            frame = pd.read_parquet(candidate_table_path(split, beam))
            if frame.empty:
                scored = pd.DataFrame(columns=[*MERGE_KEYS, *SCORE_COLUMNS[stage]])
            elif stage == "summac":
                scored = summac_score_dataframe(frame)
            elif stage == "factcc":
                scored = factcc_score_dataframe(frame)
            elif stage == "entity_support":
                scored = entity_score_dataframe(frame)
            target = score_table_path(stage, split, beam)
            target.parent.mkdir(parents=True, exist_ok=True)
            scored.to_parquet(target, index=False)
            scored.to_csv(target.with_suffix(".csv"), index=False)
    summary_path = artifact_path("scores", stage, "stage_summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(summary_path, {"stage": stage, "actual_mode": _executed_stage_mode(stage)})


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
    """Run a bounded MiniCheck audit-subset evaluation or record a deferral."""

    config = read_yaml(config_path("score", "minicheck_optional.yaml"))
    output_dir = artifact_path("scores", "minicheck")
    output_dir.mkdir(parents=True, exist_ok=True)
    audit = pd.read_csv(artifact_path("audit", "manual_audit_completed.csv")).head(
        int(config.get("max_rows", 24))
    )

    records: list[dict[str, object]] = []
    for row in audit.itertuples(index=False):
        records.append(
            {
                "id": str(row.id),
                "system": "baseline",
                "claim": str(row.baseline_summary),
                "document": str(row.document),
                "expected_consistent": int(bool(row.baseline_consistent)),
            }
        )
        records.append(
            {
                "id": str(row.id),
                "system": "reranked",
                "claim": str(row.reranked_summary),
                "document": str(row.document),
                "expected_consistent": int(bool(row.reranked_consistent)),
            }
        )

    input_path = output_dir / "audit_subset_input.json"
    output_path = output_dir / "audit_subset_output.json"
    input_path.write_text(json.dumps(records), encoding="utf-8")

    model_name = str(config.get("model_name", "roberta-large"))
    install_spec = str(config["install_spec"])
    cache_dir = str(
        (project_root() / str(config.get("cache_dir", "artifacts/models/minicheck"))).resolve()
    )
    script = """
import json
import sys
from pathlib import Path
from minicheck.minicheck import MiniCheck

input_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
model_name = sys.argv[3]
cache_dir = sys.argv[4]
records = json.loads(input_path.read_text(encoding="utf-8"))
scorer = MiniCheck(model_name=model_name, cache_dir=cache_dir)
pred_label, raw_prob, _, _ = scorer.score(
    docs=[record["document"] for record in records],
    claims=[record["claim"] for record in records],
)
for record, label, probability in zip(records, pred_label, raw_prob, strict=True):
    record["minicheck_label"] = int(label)
    record["minicheck_prob"] = float(probability)
output_path.write_text(json.dumps(records), encoding="utf-8")
""".strip()
    command = [
        "uv",
        "run",
        "--with",
        install_spec,
        "python",
        "-c",
        script,
        str(input_path),
        str(output_path),
        model_name,
        cache_dir,
    ]
    result = subprocess.run(  # noqa: S603
        command,
        cwd=str(project_root()),
        capture_output=True,
        text=True,
        check=False,
    )

    summary_path = output_dir / "stage_summary.json"
    if result.returncode != 0 or not output_path.exists():
        payload = {
            "status": "deferred",
            "model_name": model_name,
            "install_spec": install_spec,
            "audit_rows": len(audit),
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-2000:],
            "stderr_tail": result.stderr[-2000:],
        }
        write_json(summary_path, payload)
        write_text(
            output_dir / "NOT_RUN.md",
            "\n".join(
                [
                    "# MiniCheck optional stage deferred",
                    "",
                    f"- Status: {payload['status']}",
                    f"- Model: `{model_name}`",
                    f"- Audit rows attempted: `{len(audit)}`",
                    f"- Install spec: `{install_spec}`",
                    f"- Return code: `{result.returncode}`",
                    "",
                    "The bounded MiniCheck feasibility attempt did not complete in the current environment.",
                ]
            ),
        )
        return

    scored = pd.DataFrame(json.loads(output_path.read_text(encoding="utf-8")))
    scored.to_csv(output_dir / "audit_subset_scores.csv", index=False)
    write_json(
        summary_path,
        {
            "status": "completed",
            "model_name": model_name,
            "install_spec": install_spec,
            "audit_rows": len(audit),
            "scored_rows": len(scored),
            "systems": {
                system: {
                    "rows": len(system_frame),
                    "mean_minicheck_prob": round(float(system_frame["minicheck_prob"].mean()), 6),
                    "support_rate": round(float(system_frame["minicheck_label"].mean()), 6),
                    "agreement_with_codex_labels": round(
                        float(
                            (
                                system_frame["minicheck_label"].astype(int)
                                == system_frame["expected_consistent"].astype(int)
                            ).mean()
                        ),
                        6,
                    ),
                }
                for system, system_frame in scored.groupby("system")
            },
        },
    )


def run_merge_candidate_scores() -> None:
    """Merge per-stage scorer outputs into one table per split and beam size.

    Raises:
        ValueError: If any scorer merge changes candidate cardinality or leaves gaps.
    """

    for split in PIPELINE_SPLITS:
        for beam in BEAM_SIZES:
            base = pd.read_parquet(candidate_table_path(split, beam))
            summac = pd.read_parquet(score_table_path("summac", split, beam))
            factcc = pd.read_parquet(score_table_path("factcc", split, beam))
            entity = pd.read_parquet(score_table_path("entity_support", split, beam))
            merged = _merge_scores(base, summac, stage="summac")
            merged = _merge_scores(merged, factcc, stage="factcc")
            merged = _merge_scores(merged, entity, stage="entity_support")
            target = merged_table_path(split, beam)
            target.parent.mkdir(parents=True, exist_ok=True)
            merged.to_parquet(target, index=False)
            merged.to_csv(target.with_suffix(".csv"), index=False)
