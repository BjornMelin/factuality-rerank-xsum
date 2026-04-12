"""Runtime stages for environment and model manifest generation."""

from __future__ import annotations

import platform
from typing import Any

from factuality_rerank_xsum.runtime.manifests import (
    dns_check,
    package_version,
    requested_runtime_config,
    uv_version,
)
from factuality_rerank_xsum.utils.hf import hf_cli_available, run_hf_json
from factuality_rerank_xsum.utils.io import write_json, write_text
from factuality_rerank_xsum.utils.paths import artifact_path, project_root


def _asset_info(requested: dict[str, Any]) -> dict[str, dict[str, Any] | None]:
    return {
        "dataset": run_hf_json(
            "datasets",
            "info",
            requested["dataset_name"],
            str(requested["dataset_revision"] or ""),
        ),
        "generator": run_hf_json(
            "models",
            "info",
            requested["generator_model"],
            str(requested["generator_revision"] or ""),
        ),
        "factcc": run_hf_json(
            "models",
            "info",
            requested["factcc_model"],
            str(requested["factcc_revision"] or ""),
        ),
        "nli": run_hf_json(
            "models",
            "info",
            requested["nli_model"],
            str(requested["nli_revision"] or ""),
        ),
    }


def run_env_check() -> dict[str, Any]:
    """Capture runtime readiness and write environment manifests."""

    requested = requested_runtime_config()
    hf_auth_payload = run_hf_json("auth", "whoami") or {}
    asset_info = _asset_info(requested)
    hf_auth = {"authenticated": bool(hf_auth_payload)}
    online_runtime_ready = bool(
        asset_info["dataset"]
        and asset_info["generator"]
        and asset_info["factcc"]
        and asset_info["nli"]
    )
    report: dict[str, Any] = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "uv_version": uv_version(),
        "package_versions": {
            package: package_version(package)
            for package in [
                "jsonlines",
                "accelerate",
                "huggingface-hub",
                "matplotlib",
                "mypy",
                "numpy",
                "pandas",
                "pyarrow",
                "pytest",
                "rouge-score",
                "ruff",
                "datasets",
                "sentencepiece",
                "torch",
                "transformers",
                "typer",
                "ty",
            ]
        },
        "dns_checks": [dns_check("huggingface.co"), dns_check("pypi.org")],
        "hf_cli_available": hf_cli_available(),
        "hf_auth": hf_auth,
        "online_runtime_ready": online_runtime_ready,
        "mode": "online_hf_ready" if online_runtime_ready else "online_hf_unverified",
        "requested_online_path": requested,
        "resolved_online_assets": {
            "dataset_revision": asset_info["dataset"].get("sha") if asset_info["dataset"] else None,
            "generator_revision": (
                asset_info["generator"].get("sha") if asset_info["generator"] else None
            ),
            "factcc_revision": asset_info["factcc"].get("sha") if asset_info["factcc"] else None,
            "nli_revision": asset_info["nli"].get("sha") if asset_info["nli"] else None,
        },
    }
    write_json(artifact_path("env", "env_report.json"), report)

    versions_md = "# VERSIONS.md\n\n"
    versions_md += f"- Python: `{report['python_version']}`\n"
    versions_md += f"- uv: `{report['uv_version']}`\n"
    versions_md += f"- Runtime mode: `{report['mode']}`\n"
    versions_md += f"- Hugging Face CLI available: `{report['hf_cli_available']}`\n"
    versions_md += f"- Hugging Face authenticated: `{report['hf_auth']['authenticated']}`\n"
    versions_md += "- DNS checks:\n"
    for row in report["dns_checks"]:
        versions_md += f"  - {row['host']}: resolvable={row['resolvable']} error=`{row['error']}`\n"
    versions_md += "\n## Requested runtime assets\n\n"
    versions_md += f"- Dataset: `{requested['dataset_name']}` @ `{requested['dataset_revision']}`\n"
    versions_md += (
        f"- Generator: `{requested['generator_model']}` @ `{requested['generator_revision']}`\n"
    )
    versions_md += (
        f"- FactCC scorer: `{requested['factcc_model']}` @ `{requested['factcc_revision']}`\n"
    )
    versions_md += f"- NLI scorer: `{requested['nli_model']}` @ `{requested['nli_revision']}`\n"
    versions_md += "\n## Installed package snapshot\n\n"
    for package, version in report["package_versions"].items():
        versions_md += f"- {package}: `{version}`\n"
    write_text(project_root() / "VERSIONS.md", versions_md)
    return report


def run_train_or_load_bart() -> dict[str, Any]:
    """Record the configured generator and scorer checkpoints."""

    requested = requested_runtime_config()
    asset_info = _asset_info(requested)
    payload = {
        "requested_baseline": requested["generator_model"],
        "requested_factcc_checkpoint": requested["factcc_model"],
        "requested_nli_checkpoint": requested["nli_model"],
        "baseline_revision_requested": requested["generator_revision"],
        "baseline_revision_resolved": (
            asset_info["generator"].get("sha") if asset_info["generator"] else None
        ),
        "factcc_revision_requested": requested["factcc_revision"],
        "factcc_revision_resolved": (
            asset_info["factcc"].get("sha") if asset_info["factcc"] else None
        ),
        "nli_revision_requested": requested["nli_revision"],
        "nli_revision_resolved": asset_info["nli"].get("sha") if asset_info["nli"] else None,
        "actual_mode": requested["generator_mode"],
        "actual_factcc_mode": requested["factcc_mode"],
        "actual_nli_mode": requested["nli_mode"],
        "reason": (
            "Generation and scoring are configured against public Hugging Face assets. "
            "This stage records the requested and resolved checkpoints without training."
        ),
    }
    write_json(artifact_path("models", "baseline_info.json"), payload)
    return payload
