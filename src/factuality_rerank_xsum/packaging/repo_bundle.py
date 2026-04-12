"""Repository packaging helpers for final handoff artifacts."""

from __future__ import annotations

import shutil
import subprocess
import zipfile
from pathlib import Path

from factuality_rerank_xsum.utils.io import write_json
from factuality_rerank_xsum.utils.paths import artifact_path, output_path, project_root


def _tracked_repo_files(root: Path) -> list[Path]:
    """Return the tracked repository files relative to the project root."""

    git_binary = shutil.which("git")
    if git_binary is None:
        msg = "Failed listing tracked repository files because git is not installed."
        raise OSError(msg)
    try:
        result = subprocess.run(  # noqa: S603
            [git_binary, "ls-files", "-z"],
            cwd=root,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        msg = f"Failed listing tracked repository files at {root}: {exc}"
        raise OSError(msg) from exc
    return [Path(path) for path in result.stdout.decode("utf-8").split("\0") if path]


def run_package_repo() -> Path:
    """Build the final repository zip and record its manifest.

    Returns:
        The path to the packaged repository zip.
    """

    final_path = project_root().parent / "factuality-rerank-xsum.zip"
    try:
        if final_path.exists():
            final_path.unlink()
    except OSError as exc:
        msg = f"Failed removing existing repository bundle at {final_path}: {exc}"
        raise OSError(msg) from exc
    excluded_parts = {
        ".git",
        ".venv",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
    }
    try:
        with zipfile.ZipFile(final_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            root = project_root()
            for relative in _tracked_repo_files(root):
                path = root / relative
                if not path.is_file():
                    continue
                if any(part in excluded_parts for part in relative.parts):
                    continue
                if relative.parts[:2] == ("artifacts", "package") and path.suffix == ".zip":
                    continue
                archive.write(path, arcname=str(Path(root.name) / relative))
    except OSError as exc:
        msg = f"Failed creating repository bundle at {final_path}: {exc}"
        raise OSError(msg) from exc
    artifact_copy = artifact_path("package", final_path.name)
    artifact_copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(final_path, artifact_copy)
    root = project_root()
    write_json(
        artifact_path("package", "artifact_manifest.json"),
        {
            "repo_zip": str(final_path.relative_to(root.parent)),
            "artifact_copy": str(artifact_copy.relative_to(root)),
            "final_outputs": sorted(
                str(path.relative_to(root))
                for path in output_path("final").rglob("*")
                if path.is_file()
            ),
        },
    )
    return final_path
