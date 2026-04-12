from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

import pandas as pd
from datasets import Dataset, load_dataset
from huggingface_hub.errors import HfHubHTTPError

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
    """Tracked split-sampling configuration for one output split.

    Attributes:
        name: Pipeline split name written under `data/processed/splits/`.
        source_split: Source dataset split to sample from.
        limit: Maximum number of rows to materialize for the split.
    """

    name: str
    source_split: str
    limit: int


class DatasetLoader(Protocol):
    """Callable interface for loading one dataset split.

    Args:
        path: Dataset identifier passed to the backend loader.
        split: Named dataset split to materialize.
        revision: Optional dataset revision, tag, or commit.

    Returns:
        A materialized Hugging Face `Dataset` for the requested split.
    """

    def __call__(self, path: str, /, *, split: str, revision: str | None = None) -> Dataset: ...


FIXTURE_PATH = data_path("fixtures", "xsum_preview_fixture.jsonl")


def _test_final_ids(normalized_ids: list[str]) -> list[str]:
    """Select the tracked `test_final` slice for bounded fixture datasets.

    For 16 or more IDs, this returns indices 8 through 15. For datasets with
    more than 8 but fewer than 16 IDs, it returns the tail from index 8 onward.
    Otherwise it returns the latter half of the list using floor division, with
    an empty list preserved for empty inputs.
    """

    if len(normalized_ids) >= 16:
        return normalized_ids[8:16]
    if len(normalized_ids) > 8:
        return normalized_ids[8:]
    return normalized_ids[max(len(normalized_ids) // 2, 0) :]


def split_id_map(ids: list[str]) -> dict[str, list[str]]:
    """Build the tracked split-to-ID mapping for fixture-backed runs.

    Args:
        ids: Source example IDs in deterministic order.

    Returns:
        The tracked split map used by the bounded fixture workflow.
    """

    normalized = [str(value) for value in ids]
    return {
        "dev_smoke": normalized[:4],
        "dev_small": normalized[:8],
        "val_tune": normalized[:8],
        "val_full": normalized[:8],
        "test_final": _test_final_ids(normalized),
    }


def load_preview_fixture(path: Path | None = None) -> pd.DataFrame:
    """Load and normalize the tracked offline XSum preview fixture.

    Args:
        path: Optional fixture file override. When omitted, uses the tracked
            repository fixture at `data/fixtures/xsum_preview_fixture.jsonl`.

    Returns:
        A normalized fixture dataframe with string IDs and source metadata.

    Raises:
        ValueError: If the fixture file is missing required dataset columns.
    """

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
    if not isinstance(split_config, dict) or not split_config:
        msg = "configs/data/xsum.yaml must define a non-empty split_sampling mapping"
        raise TypeError(msg)
    samples: list[SplitSample] = []
    for name, payload in split_config.items():
        if not isinstance(payload, dict):
            msg = f"Split sampling config for {name} must be a mapping"
            raise TypeError(msg)
        source_split = payload.get("source_split")
        limit = payload.get("limit")
        if not isinstance(source_split, str):
            msg = f"Split sampling config for {name} must define string source_split"
            raise TypeError(msg)
        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            msg = f"Split sampling config for {name} must define positive int limit"
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
    dataset_path = artifact_path("data", "dataset.parquet")
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(dataset_path, index=False)

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
    raw_fixture_path = config.get("fixture_path")
    configured_path = (
        raw_fixture_path
        if isinstance(raw_fixture_path, Path)
        else Path(raw_fixture_path)
        if raw_fixture_path
        else FIXTURE_PATH
    )
    fixture_path = (
        configured_path if configured_path.is_absolute() else data_path().parent / configured_path
    )
    frame = load_preview_fixture(fixture_path)
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
    dataset_path = artifact_path("data", "dataset.parquet")
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(dataset_path, index=False)

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
    """Materialize the configured dataset in online or fixture mode.

    Args:
        dataset_loader: Optional dataset-loading callable used for online Hub
            materialization. Defaults to `datasets.load_dataset`.

    Returns:
        The prepared dataset payload, including the normalized dataframe and
        dataset provenance metadata written to tracked artifacts.

    Raises:
        ConnectionError: If the online dataset lookup fails and offline fallback
            is disabled.
        HfHubHTTPError: If the online dataset lookup fails and offline fallback
            is disabled.
        OSError: If dataset reads or artifact writes fail and offline fallback
            is disabled.
        TypeError: If the dataset config contains an invalid split-sampling
            shape.
        ValueError: If the loaded dataset frame is missing required columns.
    """

    config = read_yaml(config_path("data", "xsum.yaml"))
    active_loader = dataset_loader or load_dataset
    use_offline = str(config.get("mode", "online_hub")) == "offline_fixture"
    if use_offline:
        return _prepare_offline_fixture(config)
    try:
        return _prepare_online_dataset(config, dataset_loader=active_loader)
    except (ConnectionError, HfHubHTTPError, OSError) as exc:
        if bool(config.get("offline_fallback_on_error", False)):
            return _prepare_offline_fixture(config, error=exc)
        raise


def ids_for_split(name: str) -> list[str]:
    path = data_path("processed", "splits", f"{name}_ids.txt")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_dataset_table() -> pd.DataFrame:
    path = artifact_path("data", "dataset.parquet")
    return pd.read_parquet(path)
