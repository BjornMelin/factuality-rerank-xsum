"""Runtime manifest helpers for install and asset provenance."""

from __future__ import annotations

import importlib.metadata
import socket
from typing import TYPE_CHECKING, Any

from factuality_rerank_xsum.utils.io import read_json, read_yaml
from factuality_rerank_xsum.utils.paths import artifact_path, config_path

if TYPE_CHECKING:
    from pathlib import Path


def package_version(name: str) -> str | None:
    """Return the installed version for a package, if present."""

    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def dns_check(hostname: str) -> dict[str, str | bool]:
    """Resolve a hostname and return a structured DNS check payload."""

    try:
        socket.gethostbyname(hostname)
        return {"host": hostname, "resolvable": True, "error": ""}
    except OSError as exc:
        return {"host": hostname, "resolvable": False, "error": str(exc)}


def uv_version() -> str:
    """Return the installed ``uv`` version string."""

    return package_version("uv") or ""


def read_json_if_exists(path: Path) -> dict[str, Any]:
    """Read a JSON object from disk when the file exists."""

    if not path.exists():
        return {}
    payload = read_json(path)
    return payload if isinstance(payload, dict) else {}


def requested_runtime_config() -> dict[str, Any]:
    """Load the requested dataset and model configuration contract."""

    data_config = read_yaml(config_path("data", "xsum.yaml"))
    generation_config = read_yaml(config_path("model", "bart_xsum_public.yaml"))
    factcc_config = read_yaml(config_path("model", "factcc_hf.yaml"))
    nli_config = read_yaml(config_path("score", "summac.yaml"))
    return {
        "dataset_name": str(data_config["dataset_name"]),
        "dataset_revision": str(data_config.get("dataset_revision") or "") or None,
        "generator_model": str(generation_config["model_name_or_path"]),
        "generator_revision": str(generation_config.get("revision") or "") or None,
        "generator_mode": str(generation_config.get("mode", "huggingface_generation")),
        "factcc_model": str(factcc_config["model_name_or_path"]),
        "factcc_revision": str(factcc_config.get("revision") or "") or None,
        "factcc_mode": str(factcc_config.get("mode", "huggingface_text_classification")),
        "nli_model": str(nli_config["requested_model"]),
        "nli_revision": str(nli_config.get("revision") or "") or None,
        "nli_mode": str(nli_config.get("mode", "huggingface_nli_consistency")),
    }


def runtime_contract() -> dict[str, Any]:
    """Assemble the current requested and resolved runtime state."""

    requested = requested_runtime_config()
    env_report = read_json_if_exists(artifact_path("env", "env_report.json"))
    dataset_manifest = read_json_if_exists(artifact_path("data", "dataset_manifest.json"))
    model_manifest = read_json_if_exists(artifact_path("models", "baseline_info.json"))
    dataset_mode = str(dataset_manifest.get("dataset_mode") or env_report.get("mode") or "not_run")
    generator_mode = str(model_manifest.get("actual_mode") or requested["generator_mode"])
    online_execution = (
        dataset_mode == "online_hub"
        and generator_mode == "huggingface_generation"
        and requested["factcc_mode"] == "huggingface_text_classification"
        and requested["nli_mode"] == "huggingface_nli_consistency"
    )
    return {
        "requested": requested,
        "env_report": env_report,
        "dataset_manifest": dataset_manifest,
        "model_manifest": model_manifest,
        "dataset_mode": dataset_mode,
        "generator_mode": generator_mode,
        "online_execution": online_execution,
    }
