import pandas as pd

from factuality_rerank_xsum.rerank.fusion import fuse_scores, pareto_frontier, select_top_candidate


def test_fuse_scores_and_select_top_candidate() -> None:
    frame = pd.DataFrame(
        [
            {
                "id": "a",
                "beam_rank": 0,
                "token_logprob_avg": 0.9,
                "summac_style_score": 0.4,
                "factcc_style_score": 0.4,
                "entity_support_score": 0.4,
            },
            {
                "id": "a",
                "beam_rank": 1,
                "token_logprob_avg": 0.2,
                "summac_style_score": 0.9,
                "factcc_style_score": 0.9,
                "entity_support_score": 0.9,
            },
            {
                "id": "b",
                "beam_rank": 0,
                "token_logprob_avg": 0.8,
                "summac_style_score": 0.8,
                "factcc_style_score": 0.8,
                "entity_support_score": 0.8,
            },
        ]
    )
    fused = fuse_scores(
        frame,
        {
            "token_logprob_avg": 0.0,
            "summac_style_score": 0.4,
            "factcc_style_score": 0.4,
            "entity_support_score": 0.2,
        },
        "zscore",
    )
    selected = select_top_candidate(fused)

    assert len(selected) == 2
    assert selected[selected["id"] == "a"].iloc[0]["beam_rank"] == 1


def test_pareto_frontier_keeps_non_dominated_points() -> None:
    frame = pd.DataFrame(
        [
            {"system": "a", "rougeLsum": 0.50, "factuality_composite": 0.50},
            {"system": "b", "rougeLsum": 0.55, "factuality_composite": 0.48},
            {"system": "c", "rougeLsum": 0.48, "factuality_composite": 0.60},
            {"system": "d", "rougeLsum": 0.45, "factuality_composite": 0.40},
        ]
    )

    frontier = pareto_frontier(frame, "rougeLsum", "factuality_composite")

    assert set(frontier["system"]) == {"b", "a", "c"}
