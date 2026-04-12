"""Repository packaging helpers for final handoff artifacts."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from factuality_rerank_xsum.utils.io import write_json
from factuality_rerank_xsum.utils.paths import artifact_path, output_path, project_root


def run_package_repo() -> Path:
    """Build the final repository zip and record its manifest."""

    final_path = project_root().parent / "factuality-rerank-xsum.zip"
    if final_path.exists():
        final_path.unlink()
    excluded_parts = {
        ".git",
        ".venv",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
    }
    with zipfile.ZipFile(final_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in project_root().rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(project_root())
            if any(part in excluded_parts for part in relative.parts):
                continue
            if relative.parts[:2] == ("artifacts", "package") and path.suffix == ".zip":
                continue
            archive.write(path, arcname=str(Path(project_root().name) / relative))
    artifact_copy = artifact_path("package", final_path.name)
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
