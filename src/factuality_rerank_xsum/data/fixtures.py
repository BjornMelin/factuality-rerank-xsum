from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

import pandas as pd
from datasets import Dataset, load_dataset

from factuality_rerank_xsum.utils.hf import dataset_sha
from factuality_rerank_xsum.utils.io import read_yaml, write_json, write_text
from factuality_rerank_xsum.utils.paths import (
    artifact_path,
    config_path,
    data_path,
)


@dataclass(frozen=True)
class PreparedDataset:
    frame: pd.DataFrame
    mode: str
    revision: str | None
    note: str


@dataclass(frozen=True)
class SplitSample:
    name: str
    source_split: str
    limit: int


class DatasetLoader(Protocol):
    def __call__(self, path: str, /, *, split: str, revision: str | None = None) -> Dataset: ...


FIXTURE_PATH = data_path("fixtures", "xsum_preview_fixture.jsonl")


def split_id_map(ids: list[str]) -> dict[str, list[str]]:
    normalized = [str(value) for value in ids]
    return {
        "dev_smoke": normalized[:4],
        "dev_small": normalized[:8],
        "val_tune": normalized[:8],
        "val_full": normalized[:8],
        "test_final": normalized[8:16] if len(normalized) >= 16 else normalized[4:8],
    }


def load_preview_fixture(path: Path | None = None) -> pd.DataFrame:
    frame = pd.read_json(path or FIXTURE_PATH, lines=True)
    expected_columns = {"id", "document", "summary"}
    missing = expected_columns - set(frame.columns)
    if missing:
        msg = f"Fixture dataset missing columns: {sorted(missing)}"
        raise ValueError(msg)
    normalized = frame.copy()
    normalized["id"] = normalized["id"].astype(str)
    normalized["source_mode"] = "offline_fixture"
    normalized["source_split"] = "fixture"
    return normalized[["id", "document", "summary", "source_mode", "source_split"]]


def _split_samples(config: dict[str, Any]) -> list[SplitSample]:
    split_config = config.get("split_sampling")
    if not isinstance(split_config, dict):
        msg = "configs/data/xsum.yaml must define split_sampling"
        raise TypeError(msg)
    samples: list[SplitSample] = []
    for name, payload in split_config.items():
        if not isinstance(payload, dict):
            msg = f"Split sampling config for {name} must be a mapping"
            raise TypeError(msg)
        source_split = payload.get("source_split")
        limit = payload.get("limit")
        if not isinstance(source_split, str) or not isinstance(limit, int):
            msg = f"Split sampling config for {name} must define string source_split and int limit"
            raise TypeError(msg)
        samples.append(SplitSample(name=name, source_split=source_split, limit=limit))
    return samples


def _normalize_online_frame(frame: pd.DataFrame, *, source_split: str) -> pd.DataFrame:
    expected_columns = {"id", "document", "summary"}
    missing = expected_columns - set(frame.columns)
    if missing:
        msg = f"Dataset frame missing columns: {sorted(missing)}"
        raise ValueError(msg)
    normalized = frame.copy()
    normalized["id"] = normalized["id"].astype(str)
    normalized["source_mode"] = "online_hub"
    normalized["source_split"] = source_split
    return normalized[["id", "document", "summary", "source_mode", "source_split"]]


def _prepare_online_dataset(
    config: dict[str, Any],
    *,
    dataset_loader: DatasetLoader,
) -> PreparedDataset:
    dataset_name = str(config["dataset_name"])
    requested_revision = cast("str | None", config.get("dataset_revision"))
    split_samples = _split_samples(config)

    split_limits: dict[str, int] = {}
    for sample in split_samples:
        split_limits[sample.source_split] = max(
            split_limits.get(sample.source_split, 0), sample.limit
        )

    loaded_frames: dict[str, pd.DataFrame] = {}
    for source_split, limit in split_limits.items():
        dataset = dataset_loader(dataset_name, split=source_split, revision=requested_revision)
        selected = dataset.select(range(min(limit, len(dataset))))
        selected_frame = cast("pd.DataFrame", selected.to_pandas())
        loaded_frames[source_split] = _normalize_online_frame(
            selected_frame, source_split=source_split
        )

    combined = pd.concat(loaded_frames.values(), ignore_index=True).drop_duplicates(subset=["id"])
    combined.to_parquet(artifact_path("data", "dataset.parquet"), index=False)

    split_manifest: dict[str, dict[str, int | str]] = {}
    for sample in split_samples:
        split_rows = loaded_frames[sample.source_split].head(sample.limit)
        split_manifest[sample.name] = {
            "source_split": sample.source_split,
            "limit": int(sample.limit),
            "rows_selected": len(split_rows),
        }
        write_text(
            data_path("processed", "splits", f"{sample.name}_ids.txt"),
            "\n".join(split_rows["id"].astype(str).tolist()) + "\n",
        )

    resolved_revision = dataset_sha(dataset_name, requested_revision)
    manifest: dict[str, Any] = {
        "dataset_mode": "online_hub",
        "dataset_name_requested": dataset_name,
        "dataset_revision_requested": requested_revision,
        "dataset_revision_resolved": resolved_revision,
        "rows_available": len(combined),
        "fields": ["document", "summary", "id"],
        "split_sampling": split_manifest,
        "note": "Dataset materialized from the public Hugging Face Hub.",
    }
    write_json(artifact_path("data", "dataset_manifest.json"), manifest)
    return PreparedDataset(
        frame=combined,
        mode="online_hub",
        revision=resolved_revision,
        note=str(manifest["note"]),
    )


def _prepare_offline_fixture(
    config: dict[str, Any], error: Exception | None = None
) -> PreparedDataset:
    frame = load_preview_fixture(Path(str(config.get("fixture_path", FIXTURE_PATH))))
    manifest: dict[str, Any] = {
        "dataset_mode": "offline_preview_fixture",
        "dataset_name_requested": str(config["dataset_name"]),
        "dataset_revision_requested": config.get("dataset_revision"),
        "rows_available": len(frame),
        "fields": ["document", "summary", "id"],
        "note": (
            "Fell back to the local XSum preview fixture because the online dataset path failed."
            if error is not None
            else "Used the local XSum preview fixture."
        ),
        "fallback_error": str(error) if error is not None else "",
    }
    write_json(artifact_path("data", "dataset_manifest.json"), manifest)
    frame.to_parquet(artifact_path("data", "dataset.parquet"), index=False)

    fallback_splits = split_id_map(frame["id"].astype(str).tolist())
    for split_name, split_ids in fallback_splits.items():
        write_text(
            data_path("processed", "splits", f"{split_name}_ids.txt"),
            "\n".join(split_ids) + "\n",
        )

    return PreparedDataset(
        frame=frame,
        mode="offline_preview_fixture",
        revision=cast("str | None", config.get("dataset_revision")),
        note=str(manifest["note"]),
    )


def prepare_dataset(*, dataset_loader: DatasetLoader | None = None) -> PreparedDataset:
    config = read_yaml(config_path("data", "xsum.yaml"))
    active_loader = dataset_loader or load_dataset
    use_offline = str(config.get("mode", "online_hub")) == "offline_fixture"
    if use_offline:
        return _prepare_offline_fixture(config)
    try:
        return _prepare_online_dataset(config, dataset_loader=active_loader)
    except Exception as exc:
        if bool(config.get("offline_fallback_on_error", False)):
            return _prepare_offline_fixture(config, error=exc)
        raise


def ids_for_split(name: str) -> list[str]:
    path = data_path("processed", "splits", f"{name}_ids.txt")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_dataset_table() -> pd.DataFrame:
    path = artifact_path("data", "dataset.parquet")
    return pd.read_parquet(path)
