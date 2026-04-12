from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_path(*parts: str) -> Path:
    return project_root().joinpath("configs", *parts)


def data_path(*parts: str) -> Path:
    return project_root().joinpath("data", *parts)


def artifact_path(*parts: str) -> Path:
    return project_root().joinpath("artifacts", *parts)


def output_path(*parts: str) -> Path:
    return project_root().joinpath("outputs", *parts)


def docs_path(*parts: str) -> Path:
    return project_root().joinpath("docs", *parts)
