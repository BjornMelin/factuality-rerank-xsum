"""Regression tests for fixture-backed dataset and generation helpers."""

from typing import Any

import pandas as pd
import pytest
import torch

from factuality_rerank_xsum.data.fixtures import (
    FIXTURE_PATH,
    load_preview_fixture,
    prepare_dataset,
    split_id_map,
)
from factuality_rerank_xsum.generation import offline as offline_generation
from factuality_rerank_xsum.generation.offline import (
    CANDIDATE_COLUMNS,
    generate_candidates_for_examples,
)
from factuality_rerank_xsum.generation.stage import (
    generation_integrity_report,
    run_generate_candidates,
)


def test_preview_fixture_has_expected_minimum_size() -> None:
    """Preview fixture should provide the minimum tracked sample surface."""

    frame = load_preview_fixture()
    assert len(frame) >= 16
    split_map = split_id_map(frame["id"].astype(str).tolist())
    assert len(split_map["test_final"]) == 8


def test_offline_generation_returns_multiple_candidates() -> None:
    """Offline surrogate generation should emit multiple candidates per example."""

    frame = load_preview_fixture().head(2)
    examples = [
        {
            "id": str(row["id"]),
            "document": str(row["document"]),
            "summary": str(row["summary"]),
        }
        for _, row in frame.iterrows()
    ]
    rows = generate_candidates_for_examples(
        examples,
        split="dev_smoke",
        num_beams=4,
        length_penalty=1.0,
        no_repeat_ngram_size=3,
        max_new_tokens=64,
        min_new_tokens=10,
        config={"mode": "offline_surrogate_generator"},
    )

    assert len(rows) == 8
    assert {row["id"] for row in rows} == set(frame["id"].astype(str).tolist())
    assert all(row["summary"] for row in rows)


def test_generation_integrity_report_handles_empty_frames() -> None:
    """Empty generation frames should report zero coverage without NaN failures."""

    report = generation_integrity_report(pd.DataFrame(columns=["id", "summary"]), ["a", "b"])

    assert report["rows"] == 0
    assert report["observed_ids"] == 0
    assert report["missing_ids"] == ["a", "b"]
    assert report["min_candidates_per_example"] == 0
    assert report["max_candidates_per_example"] == 0
    assert report["non_empty_summaries"] is False
    assert report["has_nan_scores"] is False


def test_generation_integrity_report_treats_whitespace_summaries_as_empty() -> None:
    """Whitespace-only summaries should fail the non-empty integrity check."""

    report = generation_integrity_report(
        pd.DataFrame(
            [
                {
                    "id": "x1",
                    "summary": "   ",
                    "sequence_score_hf": 0.0,
                    "token_logprob_sum": 0.0,
                    "token_logprob_avg": 0.0,
                }
            ]
        ),
        ["x1"],
    )

    assert report["non_empty_summaries"] is False


def test_run_generate_candidates_preserves_schema_for_empty_outputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Empty generation outputs should still preserve the candidate schema."""

    def _capture_parquet(self: pd.DataFrame, path: object, index: bool = False) -> None:
        _ = index
        captured[str(path)] = self.copy()

    def _ignore_csv(_self: pd.DataFrame, _path: object, index: bool = False) -> None:
        _ = index

    monkeypatch.setattr(
        "factuality_rerank_xsum.generation.stage.config_beams",
        lambda: [
            {
                "num_beams": 4,
                "length_penalty": 1.0,
                "no_repeat_ngram_size": 3,
                "max_new_tokens": 64,
                "min_new_tokens": 10,
            }
        ],
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.generation.stage.read_yaml",
        lambda _path: {
            "mode": "offline_surrogate_generator",
            "model_name_or_path": "offline-surrogate",
            "revision": None,
        },
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.generation.stage.example_rows",
        lambda _split: [],
    )
    captured: dict[str, pd.DataFrame] = {}
    monkeypatch.setattr(pd.DataFrame, "to_parquet", _capture_parquet)
    monkeypatch.setattr(pd.DataFrame, "to_csv", _ignore_csv)
    monkeypatch.setattr(
        "factuality_rerank_xsum.generation.stage.write_json",
        lambda *_args, **_kwargs: None,
    )

    run_generate_candidates()

    assert captured
    assert all(list(frame.columns) == CANDIDATE_COLUMNS for frame in captured.values())
    assert all(frame.empty for frame in captured.values())


def test_split_id_map_uses_tail_examples_for_small_fixtures() -> None:
    """Small fixture splits should use the tail slice for test_final."""

    split_map = split_id_map([str(index) for index in range(10)])

    assert split_map["test_final"] == ["8", "9"]


def test_prepare_dataset_uses_default_fixture_when_fixture_path_is_null(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A null fixture path should fall back to the tracked preview fixture."""

    captured: dict[str, object] = {}

    def _capture_fixture(path: Any = None) -> pd.DataFrame:
        captured["path"] = path
        return load_preview_fixture(FIXTURE_PATH)

    monkeypatch.setattr(
        "factuality_rerank_xsum.data.fixtures.read_yaml",
        lambda _path: {
            "dataset_name": "owner/dataset",
            "dataset_revision": None,
            "mode": "offline_fixture",
            "fixture_path": None,
        },
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.data.fixtures.load_preview_fixture",
        _capture_fixture,
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.data.fixtures.write_json",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.data.fixtures.write_text",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(pd.DataFrame, "to_parquet", lambda *_args, **_kwargs: None)

    prepare_dataset()

    assert captured["path"] == FIXTURE_PATH


def test_generate_candidates_for_examples_reuses_hf_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """HF generation should initialize its cached runtime only once per batch."""

    offline_generation._cached_seq2seq_runtime.cache_clear()
    call_count = {"runtime": 0}

    class StubTokenizer:
        pad_token_id = 0
        eos_token_id = 0

        def __call__(self, *_args: Any, **kwargs: Any) -> dict[str, list[int] | list[list[int]]]:
            if kwargs.get("return_tensors") == "pt":
                return {"input_ids": [[1, 2, 3]]}
            return {"input_ids": [1, 2, 3]}

        def batch_decode(self, _sequences: Any, skip_special_tokens: bool = True) -> list[str]:
            _ = skip_special_tokens
            return ["summary"]

    class StubModel:
        def generate(self, **_kwargs: Any) -> Any:
            return type(
                "Outputs",
                (),
                {
                    "sequences": torch.tensor([[1, 2, 3]]),
                    "scores": None,
                    "sequences_scores": None,
                },
            )()

        def compute_transition_scores(self, *_args: Any, **_kwargs: Any) -> torch.Tensor:
            return torch.tensor([[-0.1, -0.2]])

    def _load_runtime(*_args: Any) -> tuple[StubTokenizer, StubModel, str]:
        call_count["runtime"] += 1
        return StubTokenizer(), StubModel(), "cpu"

    monkeypatch.setattr(
        "factuality_rerank_xsum.generation.offline.load_seq2seq_runtime",
        _load_runtime,
    )
    monkeypatch.setattr(
        "factuality_rerank_xsum.generation.offline.move_batch_to_device",
        lambda batch, _device: batch,
    )

    try:
        rows = generate_candidates_for_examples(
            [
                {"id": "x1", "document": "doc one", "summary": "ref one"},
                {"id": "x2", "document": "doc two", "summary": "ref two"},
            ],
            split="dev_smoke",
            num_beams=1,
            length_penalty=1.0,
            no_repeat_ngram_size=3,
            max_new_tokens=32,
            min_new_tokens=8,
            config={"mode": "huggingface_generation", "model_name_or_path": "stub-model"},
        )

        assert len(rows) == 2
        assert call_count["runtime"] == 1
    finally:
        offline_generation._cached_seq2seq_runtime.cache_clear()


def test_generate_candidates_for_examples_rejects_unknown_mode_even_when_empty() -> None:
    """Unsupported generator modes should be rejected before empty-batch return."""

    with pytest.raises(ValueError, match="Unsupported generator mode"):
        generate_candidates_for_examples(
            [],
            split="dev_smoke",
            num_beams=1,
            length_penalty=1.0,
            no_repeat_ngram_size=3,
            max_new_tokens=32,
            min_new_tokens=8,
            config={"mode": "bad-mode", "model_name_or_path": "stub-model"},
        )
