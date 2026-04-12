from __future__ import annotations

import pandas as pd

from factuality_rerank_xsum.reporting.final_outputs import (
    markdown_table,
    qualitative_case_lines,
    system_card_lines,
)


def test_markdown_table_renders_headers_and_rows() -> None:
    frame = pd.DataFrame([{"system": "best_balanced", "rougeLsum": 0.3412}])

    assert markdown_table(frame) == "\n".join(
        [
            "| system | rougeLsum |",
            "| --- | --- |",
            "| best_balanced | 0.3412 |",
        ]
    )


def test_qualitative_case_lines_render_expected_case_summary() -> None:
    frame = pd.DataFrame(
        [
            {
                "id": "x1",
                "reference": "Reference text",
                "baseline_summary": "Baseline summary",
                "reranked_summary": "Reranked summary",
                "factuality_delta": 0.125,
            }
        ]
    )

    assert qualitative_case_lines("Success cases", frame) == [
        "# Success cases",
        "",
        "## x1",
        "- Reference: Reference text",
        "- Baseline: Baseline summary",
        "- Reranked: Reranked summary",
        "- Factuality delta: 0.1250",
        "",
    ]


def test_system_card_lines_change_with_runtime_mode() -> None:
    requested = {
        "dataset_name": "EdinburghNLP/xsum",
        "generator_model": "facebook/bart-large-xsum",
        "factcc_model": "manueldeprada/FactCC",
        "nli_model": "microsoft/deberta-large-mnli",
    }
    online = "\n".join(
        system_card_lines(
            {
                "requested": {**requested, "generator_mode": "huggingface_generation"},
                "dataset_mode": "online_hub",
                "generator_mode": "huggingface_generation",
                "online_execution": True,
            }
        )
    )
    offline = "\n".join(
        system_card_lines(
            {
                "requested": {**requested, "generator_mode": "offline_surrogate_generator"},
                "dataset_mode": "fixture_preview",
                "generator_mode": "offline_surrogate_generator",
                "online_execution": False,
            }
        )
    )

    assert "Executed dataset mode: `online_hub`." in online
    assert "public Hugging Face runtime path" in online
    assert "repository scaffolding" not in online
    assert "Current outputs should be read together with the executed dataset" in offline
    assert "public Hugging Face runtime path" not in offline
    assert "Executed dataset mode: `fixture_preview`." in offline
    assert "Requested generator mode: `huggingface_generation`." in online
    assert "Executed generator mode: `huggingface_generation`." in online
    assert "Requested generator mode: `offline_surrogate_generator`." in offline
    assert "Executed generator mode: `offline_surrogate_generator`." in offline


def test_markdown_table_extracts_scalar_beam_sizes() -> None:
    beam_tradeoff = pd.DataFrame(
        [{"system": "logprob_only_beam_16"}, {"system": "logprob_only_beam_4"}]
    )

    beam_tradeoff["beam_size"] = (
        beam_tradeoff["system"].str.extract(r"(\d+)", expand=False).astype(int)
    )

    assert beam_tradeoff["beam_size"].tolist() == [16, 4]
