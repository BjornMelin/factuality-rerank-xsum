import pandas as pd
import pytest

from factuality_rerank_xsum.data.fixtures import load_preview_fixture, split_id_map
from factuality_rerank_xsum.generation.offline import (
    CANDIDATE_COLUMNS,
    generate_candidates_for_examples,
)
from factuality_rerank_xsum.generation.stage import (
    generation_integrity_report,
    run_generate_candidates,
)


def test_preview_fixture_has_expected_minimum_size() -> None:
    frame = load_preview_fixture()
    assert len(frame) >= 16
    split_map = split_id_map(frame["id"].astype(str).tolist())
    assert len(split_map["test_final"]) == 8


def test_offline_generation_returns_multiple_candidates() -> None:
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
    report = generation_integrity_report(pd.DataFrame(columns=["id", "summary"]), ["a", "b"])

    assert report["rows"] == 0
    assert report["observed_ids"] == 0
    assert report["missing_ids"] == ["a", "b"]
    assert report["min_candidates_per_example"] == 0
    assert report["max_candidates_per_example"] == 0
    assert report["non_empty_summaries"] is False
    assert report["has_nan_scores"] is False


def test_generation_integrity_report_treats_whitespace_summaries_as_empty() -> None:
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
    split_map = split_id_map([str(index) for index in range(10)])

    assert split_map["test_final"] == ["8", "9"]
