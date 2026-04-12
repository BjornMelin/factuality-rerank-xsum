from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pandas as pd
import pytest

from factuality_rerank_xsum.audit.stage import _parse_boolish
from factuality_rerank_xsum.runtime.manifests import runtime_contract
from factuality_rerank_xsum.runtime.stage import run_env_check
from factuality_rerank_xsum.scorers.factcc_style import score_factcc_style
from factuality_rerank_xsum.scorers.summac_style import score_summac_style
from factuality_rerank_xsum.scoring.stage import _merge_scores
from factuality_rerank_xsum.search.stage import _required_search_row
from factuality_rerank_xsum.utils import hf as hf_utils
from factuality_rerank_xsum.utils.transformers_runtime import select_torch_device


def test_select_torch_device_rejects_unknown_preference() -> None:
    with pytest.raises(ValueError, match="Unsupported torch device preference"):
        select_torch_device("cdua")


def test_score_factcc_style_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError, match="Unsupported FactCC mode"):
        score_factcc_style("source", "summary", config={"mode": "typo"})


def test_score_summac_style_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError, match="Unsupported SummaC mode"):
        score_summac_style("source", "summary", config={"mode": "typo"})


def test_merge_scores_raises_when_stage_values_are_missing() -> None:
    base = pd.DataFrame([{"id": "x1", "candidate_hash": "h1", "document": "doc"}])
    scores = pd.DataFrame(columns=["id", "candidate_hash", "summac_style_score"])

    with pytest.raises(ValueError, match="Missing summac scores after merge"):
        _merge_scores(base, scores, stage="summac")


def test_parse_boolish_handles_string_flags() -> None:
    assert _parse_boolish("yes") is True
    assert _parse_boolish("0") is False


def test_runtime_contract_requires_all_online_modes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "factuality_rerank_xsum.runtime.manifests.requested_runtime_config",
        lambda: {
            "dataset_name": "ds",
            "dataset_revision": "rev-ds",
            "generator_model": "gen",
            "generator_revision": "rev-gen",
            "generator_mode": "huggingface_generation",
            "factcc_model": "factcc",
            "factcc_revision": "rev-factcc",
            "factcc_mode": "heuristic_factcc_style_fallback",
            "nli_model": "nli",
            "nli_revision": "rev-nli",
            "nli_mode": "huggingface_nli_consistency",
        },
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.runtime.manifests.read_json_if_exists",
        lambda path: (
            {"dataset_mode": "online_hub"}
            if path == Path("artifacts/data/dataset_manifest.json")
            else {"actual_mode": "huggingface_generation"}
            if path == Path("artifacts/models/baseline_info.json")
            else {}
        ),
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.runtime.manifests.artifact_path",
        lambda *parts: Path(*parts),
    )

    contract = runtime_contract()

    assert contract["online_execution"] is False


def test_dataset_sha_does_not_depend_on_hf_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    class StubInfo:
        sha = "sha-123"

    monkeypatch.setattr(
        hf_utils,
        "HF_API",
        type("StubApi", (), {"dataset_info": lambda *_args, **_kwargs: StubInfo()})(),
    )
    monkeypatch.setattr(hf_utils, "hf_cli_available", lambda: False)

    assert hf_utils.dataset_sha("owner/dataset") == "sha-123"


def test_required_search_row_raises_when_selection_is_missing() -> None:
    with pytest.raises(ValueError, match="Missing search result row"):
        _required_search_row(pd.DataFrame(), description="missing winner")


def test_run_hf_json_passes_requested_revision() -> None:
    class StubInfo:
        id = "owner/model"
        sha = "sha-123"

    captured: dict[str, str | None] = {}

    class StubApi:
        def model_info(self, model_name: str, revision: str | None = None) -> StubInfo:
            captured["model_name"] = model_name
            captured["revision"] = revision
            return StubInfo()

    original = hf_utils.HF_API
    hf_utils.HF_API = cast("Any", StubApi())
    try:
        payload = hf_utils.run_hf_json("models", "info", "owner/model", "rev-42")
    finally:
        hf_utils.HF_API = original

    assert payload == {"id": "owner/model", "sha": "sha-123"}
    assert captured == {"model_name": "owner/model", "revision": "rev-42"}


def test_run_env_check_does_not_require_auth_for_public_assets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "factuality_rerank_xsum.runtime.stage.requested_runtime_config",
        lambda: {
            "dataset_name": "ds",
            "dataset_revision": "rev-ds",
            "generator_model": "gen",
            "generator_revision": "rev-gen",
            "generator_mode": "huggingface_generation",
            "factcc_model": "factcc",
            "factcc_revision": "rev-factcc",
            "factcc_mode": "huggingface_text_classification",
            "nli_model": "nli",
            "nli_revision": "rev-nli",
            "nli_mode": "huggingface_nli_consistency",
        },
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.runtime.stage.run_hf_json",
        lambda *args: (
            None
            if args == ("auth", "whoami")
            else {"id": str(args[2]), "sha": f"{args[2]}-{args[3]}"}
        ),
    )
    monkeypatch.setattr("factuality_rerank_xsum.runtime.stage.hf_cli_available", lambda: False)
    monkeypatch.setattr(
        "factuality_rerank_xsum.runtime.stage.package_version", lambda _name: "1.0.0"
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.runtime.stage.dns_check",
        lambda host: {"host": host, "resolvable": True, "error": ""},
    )
    monkeypatch.setattr("factuality_rerank_xsum.runtime.stage.uv_version", lambda: "uv 1.0.0")
    monkeypatch.setattr(
        "factuality_rerank_xsum.runtime.stage.write_json", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.runtime.stage.write_text", lambda *_args, **_kwargs: None
    )

    report = run_env_check()

    assert report["online_runtime_ready"] is True
    assert report["hf_auth"] == {"authenticated": False}
    assert report["resolved_online_assets"]["dataset_revision"] == "ds-rev-ds"
