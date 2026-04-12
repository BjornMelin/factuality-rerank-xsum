from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from factuality_rerank_xsum.utils.io import write_json, write_text
from factuality_rerank_xsum.utils.paths import artifact_path, data_path


@dataclass(frozen=True)
class PreparedDataset:
    frame: pd.DataFrame
    mode: str
    revision: str | None
    note: str


FIXTURE_PATH = data_path("fixtures", "xsum_preview_fixture.jsonl")


def load_preview_fixture() -> pd.DataFrame:
    frame = pd.read_json(FIXTURE_PATH, lines=True)
    expected_columns = {"id", "document", "summary"}
    missing = expected_columns - set(frame.columns)
    if missing:
        msg = f"Fixture dataset missing columns: {sorted(missing)}"
        raise ValueError(msg)
    frame = frame.copy()
    frame["id"] = frame["id"].astype(str)
    frame["source_mode"] = "xsum_public_preview_fixture"
    return frame


def prepare_dataset() -> PreparedDataset:
    frame = load_preview_fixture()
    manifest: dict[str, Any] = {
        "dataset_mode": "offline_preview_fixture",
        "dataset_name_requested": "EdinburghNLP/xsum",
        "dataset_revision_requested": "378fbf291bd25d5c8cbb3e0dc602301707be5693",
        "rows_available": int(len(frame)),
        "fields": ["document", "summary", "id"],
        "note": (
            "The executed run used a local fixture built from public XSum preview rows because "
            "the runtime could not resolve huggingface.co to download the official dataset snapshot."
        ),
    }
    write_json(artifact_path("data", "dataset_manifest.json"), manifest)
    frame.to_parquet(artifact_path("data", "dataset.parquet"), index=False)
    save_split_ids(frame["id"].astype(str).tolist())
    return PreparedDataset(
        frame=frame,
        mode="offline_preview_fixture",
        revision="378fbf291bd25d5c8cbb3e0dc602301707be5693",
        note=str(manifest["note"]),
    )


def split_id_map(ids: list[str]) -> dict[str, list[str]]:
    if len(ids) < 8:
        msg = "Need at least 8 fixture examples to build deterministic splits."
        raise ValueError(msg)
    dev_smoke = ids[:4]
    dev_small = ids[:8]
    val_tune = ids[:8]
    val_full = ids[:8]
    test_final = ids[8:16] if len(ids) >= 16 else ids[4:8]
    return {
        "dev_smoke": dev_smoke,
        "dev_small": dev_small,
        "val_tune": val_tune,
        "val_full": val_full,
        "test_final": test_final,
    }


def save_split_ids(ids: list[str]) -> None:
    for name, split_ids in split_id_map(ids).items():
        write_text(data_path("processed", "splits", f"{name}_ids.txt"), "\n".join(split_ids) + "\n")


def ids_for_split(name: str) -> list[str]:
    path = data_path("processed", "splits", f"{name}_ids.txt")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_dataset_table() -> pd.DataFrame:
    path = artifact_path("data", "dataset.parquet")
    return pd.read_parquet(path)
