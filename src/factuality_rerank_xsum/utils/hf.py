"""Helpers for querying Hugging Face Hub metadata from runtime stages."""

from __future__ import annotations

import shutil
from typing import Any

from huggingface_hub import HfApi
from huggingface_hub.errors import HfHubHTTPError, LocalTokenNotFoundError

HF_API = HfApi()


def hf_cli_available() -> bool:
    """Return whether the Hugging Face CLI is available on `PATH`."""

    return shutil.which("hf") is not None


def run_hf_json(*args: str) -> dict[str, Any] | None:
    """Fetch Hugging Face metadata using supported Hub API calls.

    Args:
        *args: CLI-shaped tokens describing the requested resource.

    Returns:
        A JSON-like dictionary payload for the supported query, or `None` when
        the query shape is unsupported or the Hub request fails.
    """

    try:
        match args:
            case ("auth", "whoami"):
                payload = HF_API.whoami()
            case ("datasets", "info", dataset_name):
                dataset_info = HF_API.dataset_info(dataset_name)
                payload = {"id": dataset_info.id, "sha": dataset_info.sha}
            case ("datasets", "info", dataset_name, revision):
                dataset_info = HF_API.dataset_info(dataset_name, revision=revision or None)
                payload = {"id": dataset_info.id, "sha": dataset_info.sha}
            case ("models", "info", model_name):
                model_info = HF_API.model_info(model_name)
                payload = {"id": model_info.id, "sha": model_info.sha}
            case ("models", "info", model_name, revision):
                model_info = HF_API.model_info(model_name, revision=revision or None)
                payload = {"id": model_info.id, "sha": model_info.sha}
            case _:
                return None
    except (HfHubHTTPError, LocalTokenNotFoundError, OSError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def dataset_sha(dataset_name: str, revision: str | None = None) -> str | None:
    """Get the Git SHA for a dataset revision on Hugging Face Hub.

    Args:
        dataset_name: Dataset identifier on the Hub.
        revision: Optional branch, tag, or commit to inspect.

    Returns:
        The resolved Git SHA from the Hub response, or `None` when the Hub
        does not report one.
    """

    try:
        info = HF_API.dataset_info(dataset_name, revision=revision)
    except (HfHubHTTPError, LocalTokenNotFoundError, OSError, ValueError):
        return None
    return info.sha if info else None


def model_sha(model_name: str, revision: str | None = None) -> str | None:
    """Get the Git SHA for a model revision on Hugging Face Hub.

    Args:
        model_name: Model identifier on the Hub.
        revision: Optional branch, tag, or commit to inspect.

    Returns:
        The resolved Git SHA from the Hub response, or `None` when the Hub
        does not report one.
    """

    try:
        info = HF_API.model_info(model_name, revision=revision)
    except (HfHubHTTPError, LocalTokenNotFoundError, OSError, ValueError):
        return None
    return info.sha if info else None
