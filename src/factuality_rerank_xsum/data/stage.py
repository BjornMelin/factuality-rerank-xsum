"""Dataset staging: materialize prepared data and write a small preview
artifact."""

from __future__ import annotations

from typing import Any

from factuality_rerank_xsum.data.fixtures import prepare_dataset
from factuality_rerank_xsum.utils.paths import artifact_path


def run_prepare_dataset() -> dict[str, Any]:
    """Build the prepared dataset, write a CSV preview, and return run metadata.

    Writes ``dataset_preview.csv`` under the data artifact directory with the
    first eight rows and columns ``id`` and ``summary``.

    Returns:
        Mapping with keys ``mode``, ``revision``, ``rows`` (row count), and
        ``note`` from the prepared dataset object.
    """
    prepared = prepare_dataset()
    preview = prepared.frame[["id", "summary"]].head(8)
    preview.to_csv(artifact_path("data", "dataset_preview.csv"), index=False)
    return {
        "mode": prepared.mode,
        "revision": prepared.revision,
        "rows": len(prepared.frame),
        "note": prepared.note,
    }
