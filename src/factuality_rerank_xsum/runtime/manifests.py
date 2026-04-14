"""Runtime manifest helpers for install and asset provenance."""

from __future__ import annotations

import importlib.metadata
import shutil
import socket
import subprocess
from pathlib import Path
from typing import Any

from factuality_rerank_xsum.utils.io import read_json, read_yaml
from factuality_rerank_xsum.utils.paths import (
    artifact_path,
    config_path,
    project_root,
)


def _optional_text(value: Any) -> str | None:
    text = str(value or "")
    return text or None


def repo_relative_display_path(value: str | Path) -> str:
    """Return a stable repo-relative display path when possible."""

    path = Path(value)
    if not path.is_absolute():
        return str(path)
    try:
        return str(path.resolve().relative_to(project_root()))
    except ValueError:
        return str(path)


def package_version(name: str) -> str | None:
    """Return the installed version for a package, if present.

    Args:
        name: Package distribution name.

    Returns:
        The installed version string, or `None` when the package is absent.
    """

    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def dns_check(hostname: str) -> dict[str, str | bool]:
    """Resolve a hostname and return a structured DNS check payload.

    Args:
        hostname: Hostname to resolve.

    Returns:
        A structured payload describing whether the hostname resolved.
    """

    try:
        socket.gethostbyname(hostname)
        return {"host": hostname, "resolvable": True, "error": ""}
    except OSError as exc:
        return {"host": hostname, "resolvable": False, "error": str(exc)}


def uv_version() -> str:
    """Return the installed ``uv`` version string.

    Returns:
        The installed `uv` version string, or an empty string if unavailable.
    """

    version = package_version("uv")
    if version:
        return version
    uv_executable = shutil.which("uv")
    if not uv_executable:
        return ""
    try:
        result = subprocess.run(  # noqa: S603
            [uv_executable, "--version"],
            capture_output=True,
            check=False,
            text=True,
        )
    except OSError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip() or result.stderr.strip()


def read_json_if_exists(path: Path) -> dict[str, Any]:
    """Read a JSON object from disk when the file exists.

    Args:
        path: JSON file path to read.

    Returns:
        The decoded JSON object, or an empty dictionary when missing or non-object.
    """

    if not path.exists():
        return {}
    payload = read_json(path)
    return payload if isinstance(payload, dict) else {}


def requested_runtime_config() -> dict[str, Any]:
    """Load the requested dataset and model configuration contract.

    Returns:
        The normalized runtime configuration derived from tracked YAML files.
    """

    data_config = read_yaml(config_path("data", "xsum.yaml"))
    generation_config = read_yaml(config_path("model", "bart_xsum_public.yaml"))
    factcc_config = read_yaml(config_path("model", "factcc_hf.yaml"))
    nli_config = read_yaml(config_path("score", "summac.yaml"))
    return {
        "dataset_name": str(data_config["dataset_name"]),
        "dataset_revision": _optional_text(data_config.get("dataset_revision")),
        "generator_model": str(generation_config["model_name_or_path"]),
        "generator_revision": _optional_text(generation_config.get("revision")),
        "generator_mode": str(generation_config.get("mode") or "huggingface_generation"),
        "factcc_model": str(factcc_config["model_name_or_path"]),
        "factcc_revision": _optional_text(factcc_config.get("revision")),
        "factcc_mode": str(factcc_config.get("mode") or "huggingface_text_classification"),
        "nli_model": str(nli_config["requested_model"]),
        "nli_revision": _optional_text(nli_config.get("revision")),
        "nli_mode": str(nli_config.get("mode") or "huggingface_nli_consistency"),
    }


def public_generator_config() -> dict[str, Any]:
    """Load the public baseline generator config."""

    return read_yaml(config_path("model", "bart_xsum_public.yaml"))


def finetune_generator_config() -> dict[str, Any]:
    """Load the bounded fine-tuning config."""

    return read_yaml(config_path("model", "bart_xsum_finetune.yaml"))


def active_generator_config() -> dict[str, Any]:
    """Resolve the generator config used by the main generate stage."""

    public_config = public_generator_config()
    finetune_config = finetune_generator_config()
    if not bool(finetune_config.get("enabled", False)):
        return {
            **public_config,
            "generator_label": "bart_xsum_public",
            "baseline_generator_model": public_config["model_name_or_path"],
            "baseline_generator_revision": _optional_text(public_config.get("revision")),
            "batch_size": int(public_config.get("batch_size", 1)),
        }

    export_dir_value = str(
        finetune_config.get("export_dir") or finetune_config.get("output_dir") or ""
    )
    export_dir = (
        project_root() / export_dir_value
        if export_dir_value and not export_dir_value.startswith("/")
        else Path(export_dir_value)
    ).resolve()
    if export_dir.exists():
        return {
            "model_name_or_path": str(export_dir),
            "revision": None,
            "mode": "huggingface_generation",
            "device": finetune_config.get("device", public_config.get("device", "auto")),
            "batch_size": int(
                finetune_config.get("batch_size", public_config.get("batch_size", 1))
            ),
            "max_source_length": finetune_config.get(
                "max_source_length", public_config.get("max_source_length", 768)
            ),
            "generator_label": "bart_xsum_finetuned",
            "baseline_generator_model": public_config["model_name_or_path"],
            "baseline_generator_revision": _optional_text(public_config.get("revision")),
            "source_base_model": str(finetune_config["base_model_name_or_path"]),
            "source_base_revision": _optional_text(finetune_config.get("base_revision")),
        }
    return {
        **public_config,
        "generator_label": "bart_xsum_public",
        "baseline_generator_model": public_config["model_name_or_path"],
        "baseline_generator_revision": _optional_text(public_config.get("revision")),
        "batch_size": int(public_config.get("batch_size", 1)),
    }


def runtime_contract() -> dict[str, Any]:
    """Assemble the current requested and resolved runtime state.

    Returns:
        The combined requested and resolved runtime contract payload.
    """

    requested = requested_runtime_config()
    env_report = read_json_if_exists(artifact_path("env", "env_report.json"))
    dataset_manifest = read_json_if_exists(artifact_path("data", "dataset_manifest.json"))
    model_manifest = read_json_if_exists(artifact_path("models", "baseline_info.json"))
    generation_summary = read_json_if_exists(
        artifact_path("generations", "generation_summary.json")
    )
    factcc_stage_summary = read_json_if_exists(
        artifact_path("scores", "factcc", "stage_summary.json")
    )
    summac_stage_summary = read_json_if_exists(
        artifact_path("scores", "summac", "stage_summary.json")
    )
    dataset_mode = str(dataset_manifest.get("dataset_mode") or "not_run")
    executed_generator_mode = generation_summary.get("generator_mode")
    executed_factcc_mode = factcc_stage_summary.get("actual_mode")
    executed_nli_mode = summac_stage_summary.get("actual_mode")
    generator_mode = str(executed_generator_mode or "not_run")
    factcc_mode = str(executed_factcc_mode or "not_run")
    nli_mode = str(executed_nli_mode or "not_run")
    online_execution = (
        dataset_mode == "online_hub"
        and executed_generator_mode == "huggingface_generation"
        and executed_factcc_mode == "huggingface_text_classification"
        and executed_nli_mode == "huggingface_nli_consistency"
    )
    return {
        "requested": requested,
        "env_report": env_report,
        "dataset_manifest": dataset_manifest,
        "model_manifest": model_manifest,
        "generation_summary": generation_summary,
        "dataset_mode": dataset_mode,
        "generator_mode": generator_mode,
        "factcc_mode": factcc_mode,
        "nli_mode": nli_mode,
        "online_execution": online_execution,
    }
