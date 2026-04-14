"""Unit tests for runtime contract validation and related runtime helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pandas as pd
import pytest

from factuality_rerank_xsum.audit.stage import _parse_boolish, run_sample_manual_audit
from factuality_rerank_xsum.runtime.manifests import runtime_contract
from factuality_rerank_xsum.runtime.stage import run_env_check
from factuality_rerank_xsum.scorers.factcc_style import score_factcc_style
from factuality_rerank_xsum.scorers.summac_style import score_summac_style
from factuality_rerank_xsum.scoring.stage import _merge_scores
from factuality_rerank_xsum.search.stage import _required_search_row
from factuality_rerank_xsum.utils import hf as hf_utils
from factuality_rerank_xsum.utils.transformers_runtime import select_torch_device


def test_select_torch_device_rejects_unknown_preference() -> None:
    """Reject unsupported torch device preferences."""

    with pytest.raises(ValueError, match="Unsupported torch device preference"):
        select_torch_device("cdua")


def test_score_factcc_style_rejects_unknown_mode() -> None:
    """Reject unsupported FactCC scorer modes."""

    with pytest.raises(ValueError, match="Unsupported FactCC mode"):
        score_factcc_style("source", "summary", config={"mode": "typo"})


def test_score_summac_style_rejects_unknown_mode() -> None:
    """Reject unsupported SummaC scorer modes."""

    with pytest.raises(ValueError, match="Unsupported SummaC mode"):
        score_summac_style("source", "summary", config={"mode": "typo"})


def test_merge_scores_raises_when_stage_values_are_missing() -> None:
    """Fail when a scorer merge leaves stage values missing."""

    base = pd.DataFrame(
        [{"id": "x1", "candidate_id": 0, "candidate_hash": "h1", "document": "doc"}]
    )
    scores = pd.DataFrame(columns=["id", "candidate_id", "candidate_hash", "summac_style_score"])

    with pytest.raises(ValueError, match="Missing summac scores after merge"):
        _merge_scores(base, scores, stage="summac")


def test_parse_boolish_handles_string_flags() -> None:
    """Parse common truthy and falsy string flags."""

    assert _parse_boolish("yes") is True
    assert _parse_boolish("0") is False


def test_run_sample_manual_audit_creates_output_directories(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Audit stage should create missing output directories before writing CSVs."""

    comparison = pd.DataFrame(
        [
            {
                "id": "1",
                "split": "test_final",
                "document": "doc",
                "reference": "ref",
                "baseline_summary": "base",
                "reranked_summary": "rerank",
            }
        ]
    )
    audit = pd.DataFrame(
        [
            {
                "id": "1",
                "split": "test_final",
                "document": "doc",
                "reference": "ref",
                "baseline_summary": "base",
                "reranked_summary": "rerank",
                "selected_system": "",
                "baseline_consistent": "",
                "reranked_consistent": "",
                "primary_error_type": "",
                "secondary_error_type": "",
                "world_knowledge_addition": "",
                "notes": "",
            }
        ]
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.audit.stage.comparison_table_path",
        lambda _split: tmp_path / "inputs" / "comparison.csv",
    )
    monkeypatch.setattr("pandas.read_csv", lambda _path: comparison.copy())
    monkeypatch.setattr("factuality_rerank_xsum.audit.stage.build_audit_rows", lambda _frame: audit)
    monkeypatch.setattr(
        "factuality_rerank_xsum.audit.stage.data_path",
        lambda *parts: tmp_path.joinpath(*parts),
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.audit.stage.artifact_path",
        lambda *parts: tmp_path.joinpath(*parts),
    )

    result = run_sample_manual_audit()

    assert len(result) == 1
    assert result.loc[0, "annotator_id"] == "codex"
    assert result.loc[0, "annotation_method"] == "ai-assisted expert adjudication"
    assert result.loc[0, "sample_rank"] == 1
    assert (tmp_path / "audit" / "manual_audit_template.csv").exists()
    assert (tmp_path / "audit" / "manual_audit_completed.csv").exists()
    assert (tmp_path / "audit" / "audit_examples_for_paper.csv").exists()


def test_runtime_contract_requires_all_online_modes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Use executed scorer modes, not only requested config, for online execution."""

    expected_root = Path("/expected-artifacts")
    expected_dataset_manifest = expected_root / "data" / "dataset_manifest.json"
    expected_model_manifest = expected_root / "models" / "baseline_info.json"
    expected_generation_summary = expected_root / "generations" / "generation_summary.json"
    expected_factcc_summary = expected_root / "scores" / "factcc" / "stage_summary.json"
    expected_summac_summary = expected_root / "scores" / "summac" / "stage_summary.json"
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
        lambda path: {
            expected_dataset_manifest: {"dataset_mode": "online_hub"},
            expected_generation_summary: {"generator_mode": "huggingface_generation"},
            expected_factcc_summary: {"actual_mode": "heuristic_factcc_style_fallback"},
            expected_summac_summary: {"actual_mode": "huggingface_nli_consistency"},
            expected_model_manifest: {},
        }.get(path, {}),
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.runtime.manifests.artifact_path",
        lambda *parts: expected_root.joinpath(*parts),
    )

    contract = runtime_contract()

    assert contract["online_execution"] is False
    assert contract["factcc_mode"] == "heuristic_factcc_style_fallback"


def test_runtime_contract_requires_executed_stage_summaries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Do not declare online execution from requested modes alone."""

    expected_root = Path("/expected-artifacts")
    expected_dataset_manifest = expected_root / "data" / "dataset_manifest.json"
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
            "factcc_mode": "huggingface_text_classification",
            "nli_model": "nli",
            "nli_revision": "rev-nli",
            "nli_mode": "huggingface_nli_consistency",
        },
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.runtime.manifests.read_json_if_exists",
        lambda path: {expected_dataset_manifest: {"dataset_mode": "online_hub"}}.get(path, {}),
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.runtime.manifests.artifact_path",
        lambda *parts: expected_root.joinpath(*parts),
    )

    contract = runtime_contract()

    assert contract["generator_mode"] == "not_run"
    assert contract["factcc_mode"] == "not_run"
    assert contract["nli_mode"] == "not_run"
    assert contract["online_execution"] is False


def test_dataset_sha_does_not_depend_on_hf_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    """Resolve dataset SHAs through the Hub API even without the CLI."""

    class StubInfo:
        sha = "sha-123"

    monkeypatch.setattr(
        hf_utils,
        "HF_API",
        type("StubApi", (), {"dataset_info": lambda *_args, **_kwargs: StubInfo()})(),
    )
    monkeypatch.setattr(hf_utils, "hf_cli_available", lambda: False)

    assert hf_utils.dataset_sha("owner/dataset") == "sha-123"


def test_dataset_sha_returns_none_on_hub_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return `None` when dataset SHA lookups fail."""

    class StubApi:
        def dataset_info(self, *_args: object, **_kwargs: object) -> object:
            raise OSError("network down")

    monkeypatch.setattr(hf_utils, "HF_API", cast("Any", StubApi()))

    assert hf_utils.dataset_sha("owner/dataset") is None


def test_model_sha_returns_none_on_hub_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return `None` when model SHA lookups fail."""

    class StubApi:
        def model_info(self, *_args: object, **_kwargs: object) -> object:
            raise OSError("network down")

    monkeypatch.setattr(hf_utils, "HF_API", cast("Any", StubApi()))

    assert hf_utils.model_sha("owner/model") is None


def test_required_search_row_raises_when_selection_is_missing() -> None:
    """Raise when the search stage cannot find the expected row."""

    with pytest.raises(ValueError, match="Missing search result row"):
        _required_search_row(pd.DataFrame(), description="missing winner")


def test_run_hf_json_passes_requested_revision(monkeypatch: pytest.MonkeyPatch) -> None:
    """Forward explicit revisions to Hub model lookups."""

    class StubInfo:
        id = "owner/model"
        sha = "sha-123"

    captured: dict[str, str | None] = {}

    class StubApi:
        def model_info(self, model_name: str, revision: str | None = None) -> StubInfo:
            captured["model_name"] = model_name
            captured["revision"] = revision
            return StubInfo()

    monkeypatch.setattr(hf_utils, "HF_API", cast("Any", StubApi()))

    payload = hf_utils.run_hf_json("models", "info", "owner/model", "rev-42")

    assert payload == {"id": "owner/model", "sha": "sha-123"}
    assert captured == {"model_name": "owner/model", "revision": "rev-42"}


def test_runtime_contract_does_not_treat_env_readiness_as_dataset_execution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Require the dataset stage artifact before declaring an executed mode."""

    expected_root = Path("/expected-artifacts")
    expected_env_report = expected_root / "env" / "env_report.json"
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
            "factcc_mode": "huggingface_text_classification",
            "nli_model": "nli",
            "nli_revision": "rev-nli",
            "nli_mode": "huggingface_nli_consistency",
        },
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.runtime.manifests.read_json_if_exists",
        lambda path: {expected_env_report: {"mode": "online_hf_ready"}}.get(path, {}),
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.runtime.manifests.artifact_path",
        lambda *parts: expected_root.joinpath(*parts),
    )

    contract = runtime_contract()

    assert contract["dataset_mode"] == "not_run"
    assert contract["online_execution"] is False


def test_run_env_check_does_not_require_auth_for_public_assets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Treat public asset resolution as ready even when auth is absent."""

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
