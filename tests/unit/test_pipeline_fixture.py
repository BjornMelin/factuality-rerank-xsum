import pandas as pd

from factuality_rerank_xsum.data.fixtures import load_preview_fixture, split_id_map
from factuality_rerank_xsum.generation.offline import generate_candidates_for_examples
from factuality_rerank_xsum.generation.stage import generation_integrity_report


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


def test_split_id_map_uses_tail_examples_for_small_fixtures() -> None:
    split_map = split_id_map([str(index) for index in range(10)])

    assert split_map["test_final"] == ["8", "9"]
