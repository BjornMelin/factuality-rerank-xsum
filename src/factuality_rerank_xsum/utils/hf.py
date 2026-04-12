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
        the CLI is unavailable, the query shape is unsupported, or the Hub
        request fails.
    """

    try:
        match args:
            case ("auth", "whoami"):
                payload = HF_API.whoami()
            case ("datasets", "info", dataset_name):
                dataset_info = HF_API.dataset_info(dataset_name)
                payload = {"id": dataset_info.id, "sha": dataset_info.sha}
            case ("models", "info", model_name):
                model_info = HF_API.model_info(model_name)
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
        The resolved Git SHA when the dataset lookup succeeds, otherwise
        `None`.

    Raises:
        HfHubHTTPError: If the Hub rejects the dataset lookup request.
        LocalTokenNotFoundError: If an authenticated lookup requires a token.
        OSError: If the request fails due to a local I/O or network issue.
        ValueError: If the provided arguments are invalid for the Hub client.
    """

    info = HF_API.dataset_info(dataset_name, revision=revision)
    return info.sha


def model_sha(model_name: str, revision: str | None = None) -> str | None:
    """Get the Git SHA for a model revision on Hugging Face Hub.

    Args:
        model_name: Model identifier on the Hub.
        revision: Optional branch, tag, or commit to inspect.

    Returns:
        The resolved Git SHA when the model lookup succeeds, otherwise `None`.

    Raises:
        HfHubHTTPError: If the Hub rejects the model lookup request.
        LocalTokenNotFoundError: If an authenticated lookup requires a token.
        OSError: If the request fails due to a local I/O or network issue.
        ValueError: If the provided arguments are invalid for the Hub client.
    """

    info = HF_API.model_info(model_name, revision=revision)
    return info.sha
